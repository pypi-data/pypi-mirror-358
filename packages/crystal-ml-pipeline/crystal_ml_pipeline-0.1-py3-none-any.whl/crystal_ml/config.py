# src/crystal_ml/config.py
import yaml
from pathlib import Path
from typing import Optional
from importlib.resources import files

DEFAULT_CONFIG = "config.yaml"

def load_config(path: Optional[str] = None) -> dict:
    """
    Load pipeline config.
    - If `path` is given, read that file.
    - Otherwise read the bundled config.yaml inside the crystal_ml package.
    """
    if path:
        cfg_path = Path(path)
        if not cfg_path.is_file():
            print("Config file path is not correct! Used default config.yaml instead!")
            # this will locate src/crystal_ml/config.yaml in your installed package
            pkg_cfg = files("crystal_ml").joinpath(DEFAULT_CONFIG)
            text = pkg_cfg.read_text()
            return yaml.safe_load(text)
        text = cfg_path.read_text()
        return yaml.safe_load(text)
    else:
        # this will locate src/crystal_ml/config.yaml in your installed package
        pkg_cfg = files("crystal_ml").joinpath(DEFAULT_CONFIG)
        text = pkg_cfg.read_text()
        return yaml.safe_load(text)
