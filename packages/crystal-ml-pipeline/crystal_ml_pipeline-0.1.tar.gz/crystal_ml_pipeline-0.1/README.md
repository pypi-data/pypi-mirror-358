# crystal-ml

An **end-to-end interpretable binary‐classification pipeline**.  
`crystal-ml` provides configurable data ingestion, model training (SVM, Balanced Random Forest, XGBoost, AutoGluon),  
SVM‐based downsampling algorithm, supervised discretization (FCCA), and optimal decision‐tree induction (GOSDT).

---

## 🚀 Features

- **Data ingestion** from CSV/XLSX, with train/test split or pre-split datasets  
- **Balanced Random Forest**, **SVM**, **XGBoost**, and **AutoGluon** model training with hyperparameter search  
- **SVM‐based undersampling**: identify “free” support vectors for downsampling training set (+ validation)
- **FCCA discretization** 
- **GOSDT** (Optimal Sparse Decision Trees) for interpretable optimal decision tree
- Fully **YAML‐driven configuration**

---

## 🛠️ Prerequisites

- Python **3.7** – **3.12** (recommended **3.10**)  
- `git`, `pip`, and optionally `conda`  

---

## 📦 Installation

### From PyPI

```bash
# (Optional) Create & activate a fresh conda env with Python 3.10
conda create -n crystal_ml python=3.10 -y
conda activate crystal_ml

# Install
pip install crystal_ml_pipeline

### From source
git clone https://github.com/yourusername/crystal-ml.git
cd crystal-ml
pip install .

⚙️ Configuration

All pipeline options live in a single config.yaml at your project root. Copy the template in the repo ([text](https://gitlab.com/mraffaele87/crystal-ml/-/blob/master/config.yaml?ref_type=heads)) and tweak sections as needed.

🎯 Quickstart

1. Create a script, e.g. run.py:

from crystal_ml.pipeline import run_pipeline

if __name__ == "__main__":
    run_pipeline("config.yaml")


2. Prepare config.yaml and place your train/test files alongside.
3. Execute:

python run.py (alternatively, use your favourite IDE to run the project)

4. Inspect the logs/ folder for:
- Excel reports (*_Performance.xlsx, *_Results.xlsx)
- Pickled objects (.pkl)
- PNG charts (*.png)
- Optimal tree tree diagrams

📄 License
crystal_ml_pipeline is released under the MIT License. See LICENSE for details.

Built with ❤️ by Raffaele Mariosa
GitHub · PyPI
