# src/crystal_ml/pipeline.py

import pandas as pd
from pathlib import Path
from crystal_ml.config import load_config
import os
from imblearn.ensemble import BalancedRandomForestClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV, StratifiedKFold
from sklearn.metrics import (
    confusion_matrix, roc_auc_score, average_precision_score,
    accuracy_score, recall_score, precision_score, f1_score, fbeta_score, make_scorer
)
from sklearn.utils.class_weight import compute_class_weight
from sklearn.svm import SVC
from xgboost import XGBClassifier
from autogluon.tabular import TabularPredictor
from joblib import Parallel, delayed
import numpy as np
from SupervisedDiscretization.discretizer import FCCA
import re
import graphviz
import seaborn as sns
import matplotlib.pyplot as plt
from gosdt import GOSDTClassifier
import json
import time
import pickle
from sklearn.preprocessing import MinMaxScaler


def data_ingestion(cfg: dict = None):
    """
    Load dataset(s) and return train/test splits and feature columns.

    Parameters:
    - cfg: dict, configuration for data ingestion. Expected keys:
        - input_data_complete (str, optional): path to full dataset (CSV or XLSX).
        - input_data_train (str, optional): path to pre-split train dataset.
        - input_data_test (str, optional): path to pre-split test dataset.
        - target_column (str): name of the target variable column.
        - train_test_split (dict): parameters for sklearn.model_selection.train_test_split:
            - test_size (float)
            - random_state (int)
            - shuffle (bool)
            - stratify (bool)

    Returns:
    - X_train (pd.DataFrame)
    - y_train (pd.Series)
    - X_test (pd.DataFrame)
    - y_test (pd.Series)
    - feature_columns (List[str])
    """
    if cfg is None:
        cfg = load_config().get("Data_Ingestion", {})

    # Extract config values
    complete_path = cfg.get("input_data_complete")
    train_path = cfg.get("input_data_train")
    test_path = cfg.get("input_data_test")
    target_col = cfg.get("target_column")

    tts_cfg = cfg.get("train_test_split", {})
    test_size = tts_cfg.get("test_size", 0.3)
    random_state = tts_cfg.get("random_state", 42)
    shuffle = tts_cfg.get("shuffle", True)
    stratify_flag = tts_cfg.get("stratify", True)

    # Helper to load CSV or XLSX
    def _load(path: str) -> pd.DataFrame:
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"File not found: {path}")
        if p.suffix.lower() in [".csv"]:
            return pd.read_csv(p)
        elif p.suffix.lower() in [".xlsx", ".xls"]:
            return pd.read_excel(p)
        else:
            raise ValueError(f"Unsupported file format: {p.suffix}")

    # Case 1: single complete dataset -> split
    if complete_path and not (train_path and test_path):
        df = _load(complete_path)
        if target_col not in df.columns:
            raise KeyError(f"Target column '{target_col}' not found in dataset columns")

        X = df.drop(columns=[target_col])
        y = df[target_col]
        stratify = y if stratify_flag else None
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
            shuffle=shuffle,
            stratify=stratify,
        )

    # Case 2: pre-split train and test provided
    elif train_path and test_path:
        df_train = _load(train_path)
        df_test = _load(test_path)
        for df, name in [(df_train, 'train'), (df_test, 'test')]:
            if target_col not in df.columns:
                raise KeyError(f"Target column '{target_col}' not found in {name} dataset columns")

        X_train = df_train.drop(columns=[target_col])
        y_train = df_train[target_col]
        X_test = df_test.drop(columns=[target_col])
        y_test = df_test[target_col]

    else:
        raise ValueError(
            "Config must specify either 'input_data_complete' or both 'input_data_train' and 'input_data_test'."
        )

    feature_columns = list(X_train.columns)
    # Scale features with MinMaxScaler and save the scaler
    scaler = MinMaxScaler()
    X_train = pd.DataFrame(
        scaler.fit_transform(X_train),
        columns=feature_columns,
        index=X_train.index
    )
    X_test = pd.DataFrame(
        scaler.transform(X_test),
        columns=feature_columns,
        index=X_test.index
    )

    # Persist scaler to the current working directory
    scaler_path = Path.cwd() / "minmax_scaler.pkl"
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
    # ————————————————————————————————————————————————

    return X_train, y_train, X_test, y_test, feature_columns


def train_brf(x_train, y_train, x_test, y_test, feature_columns, cfg=None):
    """
    Train a Balanced Random Forest with hyperparameter search and save results.

    Parameters are read from the 'Balanced_Random_Forest' section of config:
      - enabled: bool
      - output_dir: str
      - replacement: bool
      - sampling_strategy: str
      - param_grid: Dict[str, List]
      - n_iter: int
      - scoring: str
      - n_jobs: int
      - cv_splits: int
      - cv_shuffle: bool
      - random_state: int

    Returns:
      - best trained BRF model
    """
    # Load config section
    if cfg is None:
        cfg = load_config().get("Balanced_Random_Forest", {})

    # Output directory
    output_dir = cfg.get("output_dir", "")
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Base classifier settings
    replacement = cfg.get("replacement", False)
    sampling_strategy = cfg.get("sampling_strategy", "auto")
    random_state = cfg.get("random_state", None)

    # Hyperparameter search grid
    param_grid = cfg.get("param_grid", {})
    n_iter = cfg.get("n_iter", 200)
    scoring = cfg.get("scoring", "f1")
    n_jobs = cfg.get("n_jobs", -1)
    cv_splits = cfg.get("cv_splits", 5)
    cv_shuffle = cfg.get("cv_shuffle", True)

    # Initialize classifier and CV
    base_clf = BalancedRandomForestClassifier(
        replacement=replacement,
        sampling_strategy=sampling_strategy,
        random_state=random_state
    )
    cv = StratifiedKFold(n_splits=cv_splits, shuffle=cv_shuffle, random_state=random_state)

    search = RandomizedSearchCV(
        estimator=base_clf,
        param_distributions=param_grid,
        n_iter=n_iter,
        scoring=scoring,
        n_jobs=n_jobs,
        cv=cv,
        random_state=random_state
    )

    # Fit
    search.fit(x_train, y_train)
    model = search.best_estimator_

    # Save CV results
    results_df = pd.DataFrame(search.cv_results_)
    if output_dir:
        results_df.to_excel(os.path.join(output_dir, "RandomSearch_Results.xlsx"), index=False)

    # Feature importances
    fi = model.feature_importances_
    fi_df = pd.DataFrame({"Feature": feature_columns, "Importance": fi})
    fi_df = fi_df.sort_values(by="Importance", ascending=False)
    if output_dir:
        fi_df.to_excel(os.path.join(output_dir, "Feature_Importance.xlsx"), index=False)

    # Predictions and metrics
    y_pred_test = model.predict(x_test)
    y_prob_test = model.predict_proba(x_test)[:, 1]
    y_pred_train = model.predict(x_train)
    y_prob_train = model.predict_proba(x_train)[:, 1]

    def compute_metrics(y_true, y_pred, y_prob):
        cm = confusion_matrix(y_true, y_pred)
        return {
            'TN': cm[0,0], 'FP': cm[0,1], 'FN': cm[1,0], 'TP': cm[1,1],
            'ROC auc': roc_auc_score(y_true, y_prob),
            'PR auc': average_precision_score(y_true, y_prob),
            'Accuracy': accuracy_score(y_true, y_pred),
            'Recall': recall_score(y_true, y_pred),
            'Precision': precision_score(y_true, y_pred),
            'f1': f1_score(y_true, y_pred),
            'f2': fbeta_score(y_true, y_pred, beta=2)
        }

    metrics_test = compute_metrics(y_test, y_pred_test, y_prob_test)
    metrics_train = compute_metrics(y_train, y_pred_train, y_prob_train)

    # Save performance
    if output_dir:
        with pd.ExcelWriter(os.path.join(output_dir, "BRF_Performance.xlsx")) as writer:
            pd.DataFrame([metrics_test], index=["Test"]).to_excel(writer, sheet_name="Test Metrics")
            pd.DataFrame([metrics_train], index=["Train"]).to_excel(writer, sheet_name="Train Metrics")

    print("BRF results saved")
    return model


def train_svm(x_train, y_train, x_test, y_test, feature_columns, class_weights, cfg=None):
    """
    Randomized Search su SVM, salvataggio metriche di train e test.

    Legge da config['SVM']:
      - enabled: bool
      - output_dir: str
      - param_grid: dict
      - n_iter: int
      - cv: int
      - n_jobs: int
      - verbose: int
      - random_state: int
      - probability: bool
    """
    if cfg is None:
        cfg = load_config().get("SVM", {})

    # prepara output
    output_dir = cfg.get("output_dir", "")
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # forza i threads per SVC
    os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())


    # parametri di RandomizedSearch
    param_grid   = cfg.get("param_grid", {})
    n_iter       = cfg.get("n_iter", 100)
    cv_splits    = cfg.get("cv", 3)
    n_jobs       = cfg.get("n_jobs", -1)
    verbose      = cfg.get("verbose", 3)
    random_state = cfg.get("random_state", None)
    probability  = cfg.get("probability", True)

    # scorer su f1
    scorer = make_scorer(f1_score)

    # modello e ricerca
    svc = SVC(probability=probability, class_weight={1: class_weights[1], -1: class_weights[-1]})
    search = RandomizedSearchCV(
        estimator=svc,
        param_distributions=param_grid,
        n_iter=n_iter,
        scoring=scorer,
        cv=cv_splits,
        n_jobs=n_jobs,
        verbose=verbose,
        random_state=random_state
    )
    search.fit(x_train, y_train)

    # best estimator
    model = search.best_estimator_

    # calcolo delle metriche
    def compute_metrics(y_true, y_pred, y_prob):
        cm = confusion_matrix(y_true, y_pred)
        return {
            'TN': cm[0,0], 'FP': cm[0,1], 'FN': cm[1,0], 'TP': cm[1,1],
            'ROC auc': roc_auc_score(y_true, y_prob),
            'PR auc': average_precision_score(y_true, y_prob),
            'Accuracy': accuracy_score(y_true, y_pred),
            'Recall': recall_score(y_true, y_pred),
            'Precision': precision_score(y_true, y_pred),
            'f1': f1_score(y_true, y_pred),
            'f2': fbeta_score(y_true, y_pred, beta=2)
        }

    y_pred_test  = model.predict(x_test)
    y_prob_test  = model.predict_proba(x_test)[:, 1]
    y_pred_train = model.predict(x_train)
    y_prob_train = model.predict_proba(x_train)[:, 1]

    metrics_test  = compute_metrics(y_test,  y_pred_test,  y_prob_test)
    metrics_train = compute_metrics(y_train, y_pred_train, y_prob_train)

    # salva su Excel
    if output_dir:
        with pd.ExcelWriter(os.path.join(output_dir, "SVM_Performance.xlsx")) as writer:
            pd.DataFrame([metrics_test],  index=["Test"]).to_excel(writer, sheet_name="Test Metrics")
            pd.DataFrame([metrics_train], index=["Train"]).to_excel(writer, sheet_name="Train Metrics")

    print("SVM results saved")


def train_xgboost(x_train, y_train, x_test, y_test, feature_columns, class_weights: dict, cfg: dict = None):
    """
    Randomized Search su XGBoost con griglia estesa e gestione sbilanciamento.

    Parametri letti da config['XGBoost']:
      - enabled: bool
      - output_dir: str
      - param_grid: dict
      - n_iter: int
      - cv: int
      - n_jobs: int
      - verbose: int
      - random_state: int

    Lo sbilanciamento è gestito tramite scale_pos_weight = w_neg / w_pos.
    """
    # 1) carica cfg
    if cfg is None:
        cfg = load_config().get("XGBoost", {})

    # 2) preparazione output
    output_dir = cfg.get("output_dir", "")
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # 3) iperparam grid (default o da config)
    default_grid = {
        "n_estimators": [100, 200, 500, 1000],
        "learning_rate": [0.01, 0.05, 0.1, 0.2],
        "max_depth": [3, 5, 7, 10],
        "subsample": [0.5, 0.7, 0.9, 1.0],
        "colsample_bytree": [0.5, 0.7, 0.9, 1.0],
        "gamma": [0, 0.1, 0.2, 0.5, 1.0],
        "min_child_weight": [1, 3, 5, 10],
        "reg_alpha": [0, 0.1, 0.5, 1.0],
        "reg_lambda": [1.0, 1.5, 2.0, 3.0]
    }
    param_grid   = cfg.get("param_grid", default_grid)
    n_iter       = cfg.get("n_iter", 100)
    cv_splits    = cfg.get("cv", 5)
    n_jobs       = cfg.get("n_jobs", -1)
    verbose      = cfg.get("verbose", 1)
    random_state = cfg.get("random_state", 42)

    # 4) gestione sbilanciamento

    scale_pos_weight = class_weights.get(1, 1.0)

    # 5) scorer
    scorer = make_scorer(f1_score)

    # 6) modello base
    base_clf = XGBClassifier(
        objective="binary:logistic",
        use_label_encoder=False,
        scale_pos_weight=scale_pos_weight,
        random_state=random_state,
        verbosity=0
    )

    # 7) RandomizedSearchCV
    cv = StratifiedKFold(n_splits=cv_splits, shuffle=True, random_state=random_state)
    search = RandomizedSearchCV(
        estimator=base_clf,
        param_distributions=param_grid,
        n_iter=n_iter,
        scoring=scorer,
        cv=cv,
        n_jobs=n_jobs,
        verbose=verbose,
        random_state=random_state
    )

    # 8) fit
    y_train_xgb = y_train.replace(-1,0)
    y_test_xgb = y_test.replace(-1,0)
    search.fit(x_train, y_train_xgb)

    model = search.best_estimator_

    # 9) calcolo metriche
    def compute_metrics(y_true, y_pred, y_prob):
        cm = confusion_matrix(y_true, y_pred)
        return {
            'TN': cm[0,0], 'FP': cm[0,1], 'FN': cm[1,0], 'TP': cm[1,1],
            'ROC auc': roc_auc_score(y_true, y_prob),
            'PR auc': average_precision_score(y_true, y_prob),
            'Accuracy': accuracy_score(y_true, y_pred),
            'Recall': recall_score(y_true, y_pred),
            'Precision': precision_score(y_true, y_pred),
            'f1': f1_score(y_true, y_pred),
            'f2': fbeta_score(y_true, y_pred, beta=2)
        }

    y_pred_test  = model.predict(x_test)
    y_prob_test  = model.predict_proba(x_test)[:, 1]
    y_pred_train = model.predict(x_train)
    y_prob_train = model.predict_proba(x_train)[:, 1]

    metrics_test  = compute_metrics(y_test_xgb,  y_pred_test,  y_prob_test)
    metrics_train = compute_metrics(y_train_xgb, y_pred_train, y_prob_train)

    # 10) salva i risultati
    if output_dir:
        with pd.ExcelWriter(os.path.join(output_dir, "XGBoost_Performance.xlsx")) as writer:
            pd.DataFrame([metrics_test],  index=["Test"]).to_excel(writer, sheet_name="Test Metrics")
            pd.DataFrame([metrics_train], index=["Train"]).to_excel(writer, sheet_name="Train Metrics")

    print("XGBoost results saved")


def train_autogluon(x_train, y_train, x_test, y_test, feature_columns, cfg: dict = None):
    """
    Esegue training e valutazione con AutoGluon TabularPredictor.

    Parametri letti da config['AutoGluon']:
      - enabled: bool
      - output_dir: str
      - time_limit: int (sec)
      - eval_metric: str (es. "f1", "roc_auc")
      - num_bag_folds: int
      - num_stack_levels: int
      - sample_weight: bool  # se True aggiunge colonna sample_weight
      - weight_evaluation: bool

    class_weights è un dict {1: w_pos, -1: w_neg}
    """
    # 1) Load config
    if cfg is None:
        cfg = load_config().get("AutoGluon", {})

    # 2) Setup output dir
    output_dir = cfg.get("output_dir", "autogluon")
    os.makedirs(output_dir, exist_ok=True)

    # 3) Build DataFrames per AutoGluon
    label_col = "target"
    train_data = x_train.copy()
    train_data["target"] = y_train.values
    test_data = x_test.copy()
    test_data["target"] = y_test.values

    # 4) Sample weights
    if cfg.get("sample_weight", True):
        # Calcola i pesi per le classi in modo bilanciato
        classes = np.unique(train_data['target'])
        weights = compute_class_weight('balanced', classes=classes, y=train_data['target'])
        weight_dict = dict(zip(classes, weights))
        train_data["sample_weight"] = train_data["target"].map(weight_dict)
        test_data["sample_weight"]  = test_data["target"].map(weight_dict)

    # 5) Predictor init params
    predictor_params = {
        "label": "target",
        "path": output_dir,
        "eval_metric": cfg.get("eval_metric", "f1"),
    }
    if cfg.get("sample_weight", True):
        predictor_params["sample_weight"]     = "sample_weight"
        predictor_params["weight_evaluation"] = cfg.get("weight_evaluation", True)

    # 6) Fit
    print(f">>> [AutoGluon] training with params: time_limit={cfg.get('time_limit',3600)}, "
          f"bag_folds={cfg.get('num_bag_folds',5)}, stack_levels={cfg.get('num_stack_levels',1)}")
    predictor = TabularPredictor(**predictor_params).fit(
        train_data,
        time_limit      = cfg.get("time_limit", 3600),
        num_bag_folds   = cfg.get("num_bag_folds", 5),
        num_stack_levels= cfg.get("num_stack_levels", 1),
    )

    # 7) Metrics function
    def compute_metrics(y_true, y_pred, y_prob):
        cm = confusion_matrix(y_true, y_pred)
        return {
            "TN": cm[0,0], "FP": cm[0,1], "FN": cm[1,0], "TP": cm[1,1],
            "ROC auc": roc_auc_score(y_true, y_prob),
            "PR auc": average_precision_score(y_true, y_prob),
            "Accuracy": accuracy_score(y_true, y_pred),
            "Recall": recall_score(y_true, y_pred),
            "Precision": precision_score(y_true, y_pred),
            "f1": f1_score(y_true, y_pred),
            "f2": fbeta_score(y_true, y_pred, beta=2),
        }

    # 8) Predict & compute
    y_pred_train = predictor.predict(train_data)
    # restituisce un DataFrame di shape (n_samples, 2) con colonne [0, 1]
    proba_df_train = predictor.predict_proba(train_data)
    # prendi la colonna indice 1
    y_prob_train = proba_df_train.iloc[:, 1]
    y_pred_test  = predictor.predict(test_data)
    proba_df_test = predictor.predict_proba(test_data)
    # prendi la colonna indice 1
    y_prob_test = proba_df_test.iloc[:, 1]

    metrics_train = compute_metrics(y_train, y_pred_train, y_prob_train)
    metrics_test  = compute_metrics(y_test,  y_pred_test,  y_prob_test)

    # 9) Save Excel
    if output_dir:
        with pd.ExcelWriter(os.path.join(output_dir, "AutoGluon_Performance.xlsx")) as writer:
            pd.DataFrame([metrics_train], index=["Train"]).to_excel(writer, sheet_name="Train Metrics")
            pd.DataFrame([metrics_test],  index=["Test"]).to_excel(writer, sheet_name="Test Metrics")

    print("[AutoGluon] results saved")


from sklearn.inspection import permutation_importance

def svm_undersampling_algorithm(x_train, y_train, x_test, y_test,
                                feature_columns: list,
                                class_weights: dict,
                                cfg: dict, target_col: str):
    """
    Esegue RandomizedSearchCV su SVM e usa i free support vectors dei top-10
    modelli come downsampling. Restituisce il DataFrame dei free support vectors
    (con colonna <target_col>) e la lista dei loro indici originali.

    cfg keys:
      - output_dir: str
      - param_grid: dict
      - n_iter: int
      - cv: int
      - random_state: int
      - n_jobs: int
      - verbose: int
      - n_free_models: int        # quanti modelli considerare (default 10)
    """
    # --- leggi config ---
    output_dir      = cfg.get("output_dir", "SVM_Downsampling")
    param_grid      = cfg.get("param_grid", {
        'kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
        'C': [0.1, 1, 10, 100],
        'degree': [2, 3, 4],
        'gamma': ['scale', 'auto', 0.01, 0.1, 1],
        'coef0': [0, 0.1, 0.5, 1]
    })
    n_iter          = cfg.get("n_iter", 100)
    cv_splits       = cfg.get("cv", 3)
    random_state    = cfg.get("random_state", 42)
    n_jobs          = cfg.get("n_jobs", -1)
    verbose         = cfg.get("verbose", 3)
    n_free_models   = cfg.get("n_free_models", 10)

    # --- setup ---
    os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())
    os.makedirs(output_dir, exist_ok=True)
    f1_scorer = make_scorer(f1_score)
    svc = SVC(probability=True,
              class_weight={1: class_weights[1], -1: class_weights[-1]})
    search = RandomizedSearchCV(
        estimator=svc,
        param_distributions=param_grid,
        n_iter=n_iter,
        scoring=f1_scorer,
        cv=cv_splits,
        n_jobs=n_jobs,
        verbose=verbose,
        random_state=random_state
    )
    # --- fit RandomSearch ---
    search.fit(x_train, y_train)
    cvres   = pd.DataFrame(search.cv_results_)
    top_k   = cvres.sort_values("rank_test_score").head(n_free_models)
    top_k.to_excel(os.path.join(output_dir, "top_models.xlsx"), index=False)

    # --- alleniamo in parallelo i top-k modelli ---
    def train_model(params):
        m = SVC(**params,
                probability=True,
                class_weight={1: class_weights[1], -1: class_weights[-1]},
                verbose=0)
        m.fit(x_train, y_train)
        return m

    models = Parallel(n_jobs=os.cpu_count()-1)(
        delayed(train_model)(p) for p in top_k["params"]
    )

    # --- raccogli free support vectors unici ---
    unique_free_sv_idx = set()
    for m in models:
        sv_idx = m.support_
        free_idx = [
            sv_idx[i] for i in range(len(sv_idx))
            if abs(m.dual_coef_[0][i]) < m.C
        ]
        unique_free_sv_idx.update(free_idx)

    # --- crea DataFrame risultato ---
    free_support_vector_indices_list = sorted(unique_free_sv_idx)
    free_sv_df = x_train.iloc[free_support_vector_indices_list].copy()
    free_sv_df[target_col] = y_train.iloc[free_support_vector_indices_list].values

    # --- salva lista indici e DF ---
    free_sv_df.to_excel(
        os.path.join(output_dir, "free_support_vectors_unique.xlsx"),
        index=False
    )
    return free_sv_df, free_support_vector_indices_list


def fcca_with_brf_validation(
    x_train_down_fcca, y_train_down_fcca, x_test_fcca, y_test_fcca,
    feature_columns, fcca_cfg: dict, brf_fcca_cfg: dict
):
    """
    1) Fit di un target BRF via RandomizedSearchCV (solo su x_train_down_fcca, y_train_down_fcca)
    2) Grid search FCCA: per ogni (lambda0, p0, Q)
       – discretizza train/test
       – salva dataset compressi e metriche di compressione
       – su ciascun train_discr valora una BRF (stessa CV+griglia del target) e salva i risultati
    """
    # make deep copies so FCCA never writes into a view
    x_train_down_fcca_copy = pd.DataFrame(
        x_train_down_fcca.values,
        columns=x_train_down_fcca.columns
    )
    y_train_down_fcca_copy = pd.Series(
        y_train_down_fcca.values,
        name=y_train_down_fcca.name
    )
    x_test_fcca_copy = pd.DataFrame(
        x_test_fcca.values,
        columns=x_test_fcca.columns
    )
    y_test_fcca_copy = pd.Series(
        y_test_fcca.values,
        name=y_test_fcca.name
    )

    # --- 1) TRAIN TARGET MODEL PER FCCA
    os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())
    # parametri BRF
    param_grid   = brf_fcca_cfg.get("param_grid", {})
    n_iter       = brf_fcca_cfg.get("n_iter", 100)
    scoring      = brf_fcca_cfg.get("scoring", "f1")
    cv_splits    = brf_fcca_cfg.get("cv_splits", 5)
    cv_shuffle   = brf_fcca_cfg.get("cv_shuffle", True)
    random_state = brf_fcca_cfg.get("random_state", None)
    n_jobs       = brf_fcca_cfg.get("n_jobs", -1)
    # init estimator + CV
    base_clf = BalancedRandomForestClassifier(
        replacement=brf_fcca_cfg.get("replacement", False),
        sampling_strategy=brf_fcca_cfg.get("sampling_strategy", "auto"),
        random_state=random_state
    )
    cv = StratifiedKFold(n_splits=cv_splits, shuffle=cv_shuffle, random_state=random_state)
    search = RandomizedSearchCV(
        estimator=base_clf,
        param_distributions=param_grid,
        n_iter=n_iter,
        scoring=scoring,
        cv=cv,
        n_jobs=n_jobs,
        random_state=random_state,
        verbose=1
    )
    print("▶️ Training target BRF for FCCA...")
    search.fit(x_train_down_fcca_copy, y_train_down_fcca_copy)
    target_model = search.best_estimator_
    print(f"✅ Target BRF ready (best_params={search.best_params_})")

    # --- 2) GRID SEARCH FCCA + BRF VALIDATION
    out_base = fcca_cfg.get("output_dir", "FCCA_results")
    os.makedirs(out_base, exist_ok=True)

    lambda0_values = fcca_cfg.get("lambda0_values", [])
    p0_values      = fcca_cfg.get("p0_values", [])
    tao_q_values   = fcca_cfg.get("tao_q_values", [])

    # parametri addizionali per FCCA
    # to this:
    p1_values = fcca_cfg.get("p1_values", [])
    lambda1_values = fcca_cfg.get("lambda1_values", [])
    lambda2_values = fcca_cfg.get("lambda2_values", [])

    for lambda0 in lambda0_values:
        for p0 in p0_values:
            for p1 in p1_values:
                for lambda1 in lambda1_values:
                    for lambda2 in lambda2_values:
                        # init discretizer
                        discretizer = FCCA(
                            target_model,
                            p0=p0, p1=p1,
                            lambda0=lambda0, lambda1=lambda1, lambda2=lambda2
                        )
                        # fit sui downsampled
                        x_tr_d, y_tr_d = discretizer.fit_transform(x_train_down_fcca_copy, y_train_down_fcca_copy)
                        # trasformazione preliminare del test (senza soglie)
                        x_te_d, y_te_d = discretizer.transform(x_test_fcca_copy, y_test_fcca_copy)

                        for tao_q in tao_q_values:
                            cfg_name = f"λ0_{lambda0}_λ1_{lambda1}_λ2_{lambda2}_p0_{p0}_p1_{p1}_Q_{tao_q}"
                            out_dir = os.path.join(out_base, cfg_name)
                            os.makedirs(out_dir, exist_ok=True)

                            # seleziona soglie e trasforma
                            thresholds = discretizer.selectThresholds(tao_q)
                            x_tr_q, y_tr_q = discretizer.transform(x_train_down_fcca_copy, y_train_down_fcca_copy, thresholds)
                            x_te_q, y_te_q = discretizer.transform(x_test_fcca_copy,       y_test_fcca_copy,       thresholds)

                            # salva i dataset discretizzati
                            x_tr_q.to_excel (os.path.join(out_dir, "x_train_discr.xlsx"), index=False)
                            y_tr_q.to_excel (os.path.join(out_dir, "y_train_discr.xlsx"), index=False)
                            x_te_q.to_excel (os.path.join(out_dir, "x_test_discr.xlsx"),  index=False)
                            y_te_q.to_excel (os.path.join(out_dir, "y_test_discr.xlsx"),  index=False)

                            # metriche di compressione
                            cr = discretizer.compression_rate(x_test_fcca_copy, y_test_fcca_copy, thresholds)
                            ir = discretizer.inconsistency_rate(x_test_fcca_copy, y_test_fcca_copy, thresholds)
                            with open(os.path.join(out_dir, "compression_metrics.txt"), "w") as f:
                                f.write(f"Compression rate: {cr}\nInconsistency rate: {ir}\n")
                            brf_fcca_cfg_tmp = brf_fcca_cfg.copy()
                            brf_fcca_cfg_tmp['output_dir'] = out_dir
                            # valida BRF su train discreto + test originale
                            print(f"🔎 Validating BRF on FCCA set {cfg_name} …")
                            train_brf(
                                x_tr_q, y_tr_q,
                                x_te_q, y_te_q,
                                x_tr_q.columns.tolist(),
                                brf_fcca_cfg_tmp
                            )

    print("🏁 FCCA grid search + BRF validation completed.")



def plot_fcca_results(fcca_cfg):
    """
    Reads all subfolders in 'FCCA_results' matching the pattern
    'lambda0_<λ0>_Q_<τ_q>_p0_<p0>' and produces:
      1) Line‐plot of compression_rate & inconsistency_rate vs. configuration
      2) Line‐plot of BRF train/test Accuracy, Recall, Precision vs. configuration

    Saves:
      - discretization_lineplot_metrics.png
      - brf_lineplot_metrics.png
    """
    main_folder = fcca_cfg.get("output_dir", "FCCA_results")
    folder_pattern = re.compile(
        r"λ0_([\d\.]+)"
        r"_λ1_([\d\.]+)"
        r"_λ2_([\d\.]+)"
        r"_p0_([\d\.]+)"
        r"_p1_([\d\.]+)"
        r"_Q_([\d\.]+)"
    )

    rows_discr = []
    rows_brf = []

    for folder_name in os.listdir(main_folder):
        folder_path = os.path.join(main_folder, folder_name)
        if not os.path.isdir(folder_path):
            continue

        m = folder_pattern.match(folder_name)
        if not m:
            continue

        lambda0_val = float(m.group(1))
        l1_val = float(m.group(2))
        l2_val = float(m.group(3))
        p0_val = float(m.group(4))
        p1_val = float(m.group(5))
        tau_q_val = float(m.group(6))


        # --- compression & inconsistency ---
        metrics_path = os.path.join(folder_path, "compression_metrics.txt")
        if os.path.isfile(metrics_path):
            comp_rate = None
            incons_rate = None
            with open(metrics_path, "r") as f:
                for line in f:
                    if line.startswith("Compression rate:"):
                        comp_rate = float(line.split(":",1)[1].strip())
                    elif line.startswith("Inconsistency rate:"):
                        incons_rate = float(line.split(":",1)[1].strip())
            if comp_rate is not None and incons_rate is not None:
                rows_discr.append({
                    "folder": folder_name,
                    "compression_rate": comp_rate,
                    "inconsistency_rate": incons_rate,
                    "λ0": lambda0_val,
                    "λ1": l1_val,
                    "λ2": l2_val,
                    "p0": p0_val,
                    "p1": p1_val,
                    "Q": tau_q_val
                })

        # --- BRF performance ---
        brf_path = os.path.join(folder_path, "BRF_Performance.xlsx")
        if os.path.isfile(brf_path):
            try:
                df_train = pd.read_excel(brf_path, sheet_name="Train Metrics")
                df_test  = pd.read_excel(brf_path, sheet_name="Test Metrics")
                rows_brf.append({
                    "folder": folder_name,
                    "train_accuracy":  df_train["Accuracy"].iloc[0],
                    "train_recall":    df_train["Recall"].iloc[0],
                    "train_precision": df_train["Precision"].iloc[0],
                    "test_accuracy":   df_test["Accuracy"].iloc[0],
                    "test_recall":     df_test["Recall"].iloc[0],
                    "test_precision":  df_test["Precision"].iloc[0],
                    "λ0": lambda0_val,
                    "λ1": l1_val,
                    "λ2": l2_val,
                    "p0": p0_val,
                    "p1": p1_val,
                    "Q": tau_q_val
                })
            except Exception as e:
                print(f"Failed to read BRF performance in {folder_name}: {e}")

    df_discr = pd.DataFrame(rows_discr)
    df_brf  = pd.DataFrame(rows_brf)

    # -------- Plot 1: Discretization Performance --------
    dfd = df_discr.sort_values("Q")
    dfd["config"] = pd.Categorical(
        dfd["folder"],
        categories=dfd["folder"].unique(),
        ordered=True
    )
    long1 = dfd.melt(
        id_vars=["config", "Q"],
        value_vars=["compression_rate", "inconsistency_rate"],
        var_name="metric",
        value_name="value"
    )

    plt.figure(figsize=(18, 9))
    sns.lineplot(
        data=long1,
        x="config", y="value", hue="metric",
        marker="o", palette="Set1"
    )
    plt.title("Discretization Performance: Compression & Inconsistency Rate")
    plt.xlabel("Configuration (ordered by Q)")
    plt.ylabel("Value")
    plt.xticks(rotation=60, fontsize=8, ha="right")
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    out_path_line = os.path.join(main_folder, "FCCA_discretization_lineplot_metrics.png")
    plt.savefig(out_path_line, dpi=250)
    plt.close()

    # -------- Plot 2: BRF Performance --------
    dfb = df_brf.sort_values("Q")
    dfb["config"] = pd.Categorical(
        dfb["folder"],
        categories=dfb["folder"].unique(),
        ordered=True
    )
    long2 = dfb.melt(
        id_vars=["config", "Q"],
        value_vars=[
            "train_accuracy", "train_recall", "train_precision",
            "test_accuracy",  "test_recall",  "test_precision"
        ],
        var_name="metric",
        value_name="value"
    )

    plt.figure(figsize=(18, 9))
    sns.lineplot(
        data=long2,
        x="config", y="value", hue="metric",
        marker="o"
    )
    plt.title("BRF Performance: Train and Test (Accuracy, Recall, Precision)")
    plt.xlabel("Configuration (ordered by Q)")
    plt.ylabel("Metric Value")
    plt.xticks(rotation=60, fontsize=8, ha="right")
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    out_path_line2 = os.path.join(main_folder, "FCCA_brf_lineplot_metrics.png")
    plt.savefig(out_path_line2, dpi=250)
    plt.close()

def _compute_gosdt_metrics(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    if cm.size == 4:
        tn, fp, fn, tp = cm.ravel()
    else:
        tn = fp = fn = tp = 0
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    f2 = fbeta_score(y_true, y_pred, beta=2, zero_division=0)
    return {"TP": tp, "TN": tn, "FP": fp, "FN": fn,
            "Accuracy": acc, "Precision": prec, "Recall": rec,
            "F1": f1, "F2": f2, "Confusion Matrix": cm}


def _add_counts_to_tree(node, X, y, feature_names, condition=lambda df: df):
    """
    Aggiunge al dizionario dell'albero (node) il conteggio dei campioni che vi raggiungono,
    filtrando X (pandas DataFrame) secondo le condizioni accumulate.
    I conteggi vengono salvati in "n_neg" e "n_pos".

    Parameters:
      node: dict
         Nodo dell'albero (JSON) come prodotto da GOSDT.
      X: pd.DataFrame
         DataFrame dei dati di training (le colonne sono le feature binarizzate).
      y: pd.Series
         Etichette corrispondenti (0 per negativo, 1 per positivo).
      feature_names: list
         Lista dei nomi delle feature, in ordine.
      condition: funzione, opzionale
         Funzione che filtra X in base alle condizioni accumulate.

    Returns:
      Il nodo aggiornato (con chiavi "n_neg", "n_pos" e, per nodi interni, "feature_name").
    """
    # Filtra X secondo la condizione accumulata
    X_sub = condition(X)
    # Se non ci sono campioni, assegna 0
    if X_sub.shape[0] == 0:
        node["n_neg"] = 0
        node["n_pos"] = 0
    else:
        # I campioni corrispondenti (assumendo che X e y abbiano gli stessi index)
        sub_y = y.loc[X_sub.index]
        node["n_neg"] = int((sub_y == 0).sum())
        node["n_pos"] = int((sub_y == 1).sum())

    # Se il nodo è interno (ha la chiave "feature"), aggiungi il nome della feature e processa i figli
    if "feature" in node:
        feat_idx = node["feature"]
        feat_name = feature_names[feat_idx] if feat_idx < len(feature_names) else str(feat_idx)
        node["feature_name"] = feat_name

        # Definisci la condizione per il ramo "true": feature deve essere 1
        true_condition = lambda df: df[df[feat_name] == 1]
        # Condizione per il ramo "false": feature deve essere 0
        false_condition = lambda df: df[df[feat_name] == 0]

        node["true"] = _add_counts_to_tree(
            node["true"], X, y, feature_names,
            lambda df: true_condition(condition(df))
        )
        node["false"] = _add_counts_to_tree(
            node["false"], X, y, feature_names,
            lambda df: false_condition(condition(df))
        )
    return node


def _tree_to_dot(node, node_id=0, dot_lines=None):
    """
    Converte l'albero arricchito (con conteggi e nomi delle feature) in formato DOT.

    Parameters:
      node: dict
         Nodo dell'albero con le chiavi "feature_name" (per nodi interni) o "prediction" (per foglie),
         e "n_neg", "n_pos" con i conteggi dei campioni.
      node_id: int, opzionale
         ID univoco del nodo corrente.
      dot_lines: list, opzionale
         Lista di righe DOT accumulate.

    Returns:
      (dot_lines, next_id) dove dot_lines è la lista completa di righe DOT e next_id il contatore aggiornato.
    """
    if dot_lines is None:
        dot_lines = []

    current_id = node_id
    if "prediction" in node:
        # Nodo foglia
        label = f"Leaf\\n[{node.get('n_neg', '?')}, {node.get('n_pos', '?')}]\\nPred: {node.get('prediction', '?')}"
        dot_lines.append(f'  node{current_id} [shape=box, label="{label}"];')
        next_id = current_id + 1
    else:
        # Nodo interno: mostra il nome della feature e i conteggi
        label = f"{node.get('feature_name', '?')}\\n[{node.get('n_neg', '?')}, {node.get('n_pos', '?')}]"
        dot_lines.append(f'  node{current_id} [label="{label}"];')
        next_id = current_id + 1

        # Processa il ramo "true"
        true_id = next_id
        dot_lines, next_id = _tree_to_dot(node["true"], true_id, dot_lines)
        dot_lines.append(f'  node{current_id} -> node{true_id} [label="True"];')

        # Processa il ramo "false"
        false_id = next_id
        dot_lines, next_id = _tree_to_dot(node["false"], false_id, dot_lines)
        dot_lines.append(f'  node{current_id} -> node{false_id} [label="False"];')
    return dot_lines, next_id


def _generate_stylish_dot(enhanced_tree, feature_names):
    """
    Genera una stringa DOT per l'albero arricchito con conteggi e nomi delle feature,
    utilizzando un layout più stilizzato per una presentazione "più figa".

    I nodi mostreranno:
      - Per i nodi interni: il nome della feature (non l'indice) e il conteggio [n_neg, n_pos].
      - Per le foglie: l'etichetta "Leaf", il conteggio per ogni classe e la predizione.

    Restituisce la stringa DOT.
    """
    # Header stilizzato
    dot_lines = [
        'digraph GOSDT_Tree_Stylish {',
        '  graph [splines=polyline, nodesep=0.8, ranksep=0.7, bgcolor="white"];',
        '  node [shape=box, style="filled", fillcolor="lightgoldenrod1", fontname="Helvetica", fontsize=10];',
        '  edge [color="gray", fontname="Helvetica", fontsize=8];'
    ]

    def recurse(node, node_id, dot_lines):
        current_id = node_id
        if "prediction" in node:
            # Nodo foglia
            label = f"Leaf\\n[{node.get('n_neg', '?')}, {node.get('n_pos', '?')}]\\nPred: {node.get('prediction', '?')}"
            dot_lines.append(f'  node{current_id} [label="{label}"];')
            next_id = current_id + 1
        else:
            # Nodo interno: usa il nome della feature (già aggiunto come "feature_name")
            label = f"{node.get('feature_name', '?')}\\n[{node.get('n_neg', '?')}, {node.get('n_pos', '?')}]"
            dot_lines.append(f'  node{current_id} [label="{label}"];')
            next_id = current_id + 1

            # Processa ramo "true"
            true_id = next_id
            next_id = recurse(node["true"], true_id, dot_lines)
            dot_lines.append(f'  node{current_id} -> node{true_id} [label="True"];')

            # Processa ramo "false"
            false_id = next_id
            next_id = recurse(node["false"], false_id, dot_lines)
            dot_lines.append(f'  node{current_id} -> node{false_id} [label="False"];')
        return next_id

    # Avvia la ricorsione partendo dal nodo radice con ID 0
    recurse(enhanced_tree, 0, dot_lines)
    dot_lines.append("}")
    return "\n".join(dot_lines)


def descale_feature_names(df: pd.DataFrame, scaler_path: str) -> pd.DataFrame:
    """
    Read a MinMaxScaler from `scaler_path`, invert the scaling of each numeric threshold
    in the column names of `df`, and return a new DataFrame with updated column names.

    Expects column names like "feature<=0.1234", "feature>=0.1234" or "feature=0.1234".
    """
    # load scaler
    scaler_path = Path(scaler_path)
    if not scaler_path.is_file():
        raise FileNotFoundError(f"Scaler not found at {scaler_path}")
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)

    feature_names = list(scaler.feature_names_in_)
    data_min = scaler.data_min_
    data_max = scaler.data_max_

    new_cols = []
    pattern = re.compile(r"(.+?)(<=|>=|=)([\d\.eE+-]+)")
    for col in df.columns:
        m = pattern.match(col)
        if m:
            feat, op, sval = m.groups()
            if feat not in feature_names:
                # unknown feature, leave as‐is
                new_cols.append(col)
                continue
            idx = feature_names.index(feat)
            scaled_thresh = float(sval)
            orig_thresh = scaled_thresh * (data_max[idx] - data_min[idx]) + data_min[idx]
            # format back to reasonable precision
            orig_str = f"{orig_thresh:.2f}"
            new_cols.append(f"{feat}{op}{orig_str}")
        else:
            new_cols.append(col)

    df = df.copy()
    df.columns = new_cols
    return df

def run_gosdt(gosdt_cfg):
    """
    legge la sezione GOSDT da config, carica da input_dir i file
    x_train_discr.xlsx, y_train_discr.xlsx, x_test_discr.xlsx, y_test_discr.xlsx,
    allena GOSDTClassifier, salva metriche, alberi DOT e PNG in output_dir.
    """

    inp = gosdt_cfg.get("input_dir", "")
    out = gosdt_cfg.get("output_dir", "logs/gosdt")
    os.makedirs(out, exist_ok=True)

    # 1) carica
    x_train = pd.read_excel(os.path.join(inp, "x_train_discr.xlsx"))
    y_train = pd.read_excel(os.path.join(inp, "y_train_discr.xlsx")).iloc[:,0]
    x_test  = pd.read_excel(os.path.join(inp, "x_test_discr.xlsx"))
    y_test  = pd.read_excel(os.path.join(inp, "y_test_discr.xlsx")).iloc[:,0]
    #DESCALING THRESHOLDS IN FEATURE NAMES FOR FINAL PLOTS
    scaler_file = Path.cwd() / "minmax_scaler.pkl"
    x_train = descale_feature_names(x_train, scaler_file)
    x_test = descale_feature_names(x_test, scaler_file)

    # 2) estrai params GOSDT (escludi input/output)
    params = {k:v for k,v in gosdt_cfg.items() if k not in ("enabled","input_dir","output_dir")}

    # 3) fit
    clf = GOSDTClassifier(**params)
    t0 = time.time()
    clf.fit(x_train, y_train, input_features=x_train.columns.tolist())
    print(f"[GOSDT] training in {time.time()-t0:.1f}s")

    # 4) metriche
    y_tr_pred = clf.predict(x_train)
    y_te_pred = clf.predict(x_test)
    met_tr = _compute_gosdt_metrics(y_train, y_tr_pred)
    met_te = _compute_gosdt_metrics(y_test,  y_te_pred)
    pd.DataFrame([met_tr]).to_excel(os.path.join(out, "GOSDT_Train_Metrics.xlsx"), index=False)
    pd.DataFrame([met_te]).to_excel(os.path.join(out, "GOSDT_Test_Metrics.xlsx"),  index=False)

    # 5) estrai e arricchisci albero
    tree0 = json.loads(clf.result_.model)[0]
    enhanced_tree_train = _add_counts_to_tree(tree0, x_train, y_train, x_train.columns.tolist())
    with open(os.path.join(out, "optimal_tree_enhanced.json"), "w") as f:
        json.dump(enhanced_tree_train, f, indent=2)

    # 6) genera PNG stylish

    dot_data_stylish_train = _generate_stylish_dot(enhanced_tree_train, x_train.columns.tolist())
    dot_stylish_train = graphviz.Source(dot_data_stylish_train)
    output_filename_stylish_train = "optimal_tree_graph_stylish_train"
    dot_stylish_train.render(output_filename_stylish_train, format="png", cleanup=True)
    enhanced_tree_test = _add_counts_to_tree(tree0, x_test, y_test, x_test.columns.tolist())
    dot_data_stylish_test = _generate_stylish_dot(enhanced_tree_test, x_test.columns.tolist())
    dot_stylish_test = graphviz.Source(dot_data_stylish_test)
    output_filename_stylish_test = "optimal_tree_graph_stylish_test"
    dot_stylish_test.render(output_filename_stylish_test, format="png", cleanup=True)

    print(f"[GOSDT] results saved in {out}")



def run_pipeline(config_path: str = None):
    # 1) Carica config
    cfg = load_config(config_path)

    # 2) Data ingestion
    di_cfg = cfg.get("Data_Ingestion", {})
    if di_cfg.get("enabled", False):
        X_train, y_train, X_test, y_test, feat_cols = data_ingestion(di_cfg)

        # 3) Calcolo pesi classi per SVM/XGBoost/AutoGluon
        n_neg = np.sum(y_train == -1)
        n_pos = np.sum(y_train ==  1)
        w_neg, w_pos = 1.0, n_neg / n_pos if n_pos else 1.0
        class_weights = {-1: w_neg, 1: w_pos}
        print(f"[Weights] neg: {w_neg:.3f}, pos: {w_pos:.3f}")

        # 4) Esecuzione modelli
        # SVM
        svm_cfg = cfg.get("SVM", {})
        if svm_cfg.get("enabled", False):
            train_svm(X_train, y_train, X_test, y_test, feat_cols, class_weights, svm_cfg)

        # Balanced RF
        brf_cfg = cfg.get("Balanced_Random_Forest", {})
        if brf_cfg.get("enabled", False):
            train_brf(X_train, y_train, X_test, y_test, feat_cols, brf_cfg)

        # XGBoost
        xgb_cfg = cfg.get("XGBoost", {})
        if xgb_cfg.get("enabled", False):
            train_xgboost(X_train, y_train, X_test, y_test, feat_cols, class_weights, xgb_cfg)

        # AutoGluon
        ag_cfg = cfg.get("AutoGluon", {})
        if ag_cfg.get("enabled", False):
            train_autogluon(X_train, y_train, X_test, y_test, feat_cols, ag_cfg)


        #SVM-Based Downsampling
        ds_cfg = cfg.get("SVM_Downsampling", {})
        output_dir = ds_cfg.get("output_dir", "SVM_Downsampling")
        os.makedirs(output_dir, exist_ok=True)
        # file di pickle standard
        df_pickle = os.path.join(output_dir, "free_sv_df.pkl")
        idxs_pickle = os.path.join(output_dir, "free_sv_idxs.pkl")
        # 1) se enabled, eseguo l'algoritmo
        target_col = di_cfg.get("target_column")
        if ds_cfg.get("enabled", False):
            free_sv_df, free_sv_idxs = svm_undersampling_algorithm(
                X_train, y_train, X_test, y_test,
                feat_cols, class_weights, ds_cfg, target_col
            )
            # e se voglio salvare, serializzo qui
            if ds_cfg.get("save_output", False):
                with open(df_pickle, "wb") as f: pickle.dump(free_sv_df, f)
                with open(idxs_pickle, "wb") as f: pickle.dump(free_sv_idxs, f)
            # Otteniamo quindi i nuovi dati di train downsampled
            X_train_downsample = free_sv_df.drop(columns=[target_col])
            y_train_downsample = free_sv_df[target_col]

        # 2) se voglio caricare dai pickle, eseguo questo blocco
        if ds_cfg.get("load_saved_output", False):
            with open(df_pickle, "rb") as f:
                free_sv_df = pickle.load(f)
            with open(idxs_pickle, "rb") as f:
                free_sv_idxs = pickle.load(f)
            # Otteniamo quindi i nuovi dati di train downsampled
            X_train_downsample = free_sv_df.drop(columns=[target_col])
            y_train_downsample = free_sv_df[target_col]
        if ((not ds_cfg.get("enabled", False)) and (not ds_cfg.get("load_saved_output", False))):
            print("SVM_Downsampling: both enable and load_saved_output are set to False! FCCA and GOSDT might be highly time-consuming with the full dataset!")
            X_train_downsample = free_sv_df.drop(columns=[target_col])
            y_train_downsample = free_sv_df[target_col]

        # Balanced RF per validare la procedura di downsampling
        brf_validation_cfg = cfg.get("BRF_Validation_Undersampling", {})
        if brf_cfg.get("enabled", False):
            train_brf(X_train_downsample, y_train_downsample, X_test, y_test, feat_cols, brf_validation_cfg)

        # XGBoost
        xgb_validation_cfg = cfg.get("XGBoost_Validation_Undersampling", {})
        if xgb_cfg.get("enabled", False):
            train_xgboost(X_train_downsample, y_train_downsample, X_test, y_test, feat_cols, class_weights, xgb_validation_cfg)

        # AutoGluon
        ag_validation_cfg = cfg.get("AutoGluon_Validation_Undersampling", {})
        if ag_cfg.get("enabled", False):
            train_autogluon(X_train_downsample, y_train_downsample, X_test, y_test, feat_cols, ag_validation_cfg)

        '''If performance drop after downsampling exceeds a user-defined threshold, a warning message is sent to the user'''

        drop_thr = ds_cfg.get("percentage_performance_drop_threshold")
        drop_metric = ds_cfg.get("percentage_performance_drop_metric")
        if drop_thr is not None and drop_metric:
            # map config metric name to Excel column
            metric_map = {
                "accuracy": "Accuracy",
                "recall": "Recall",
                "precision": "Precision",
                "f1": "f1",
                "f2": "f2"
            }
            col = metric_map.get(drop_metric.lower())
            if col is None:
                raise ValueError(f"Unknown percentage_performance_drop_metric: {drop_metric}")

            # paths to the two BRF_Performance files
            orig_file = os.path.join(brf_cfg.get("output_dir", ""), "BRF_Performance.xlsx")
            new_file = os.path.join(brf_validation_cfg.get("output_dir", ""), "BRF_Performance.xlsx")

            # load train‐set metrics (we compare training performance pre/post)
            orig_df = pd.read_excel(orig_file, sheet_name="Train Metrics")
            new_df = pd.read_excel(new_file, sheet_name="Train Metrics")

            orig_val = orig_df[col].iloc[0]
            new_val = new_df[col].iloc[0]

            # compute percentage drop
            drop_pct = (orig_val - new_val) / orig_val * 100

            # if drop positive and exceeds threshold, warn
            if drop_pct > drop_thr:
                print(f"\033[91mWarning: {col} dropped by {drop_pct:.1f}% (> {drop_thr}%) after downsampling.\033[0m")
            else:
                print(f"{col} change after downsampling: {drop_pct:.1f}% (threshold = {drop_thr}%)")
        '''End of the "warning" part'''



        # dopo la validazione undersampling --> FCCA
        y_train_fcca = y_train_downsample.replace(-1, 0)
        y_test_fcca = y_test.replace(-1, 0)
        fcca_cfg = cfg.get("FCCA", {})
        brf_fcca_cfg = cfg.get("BRF_FCCA", {})
        if fcca_cfg.get("enabled", False):
            fcca_with_brf_validation(
                X_train_downsample, y_train_fcca,
                X_test, y_test_fcca,
                feat_cols,
                fcca_cfg,
                brf_fcca_cfg
            )

        plot_fcca_results(fcca_cfg)

    gosdt_cfg = cfg.get("GOSDT", {})
    if gosdt_cfg.get("enabled", False):
        run_gosdt(gosdt_cfg)

    print("✅ Pipeline execution finished.")

