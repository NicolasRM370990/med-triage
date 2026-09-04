"""
Funções para fazer o loader das bases de dados
"""

from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data" / "raw"

def load_train() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "medical_tc_train.csv")

def load_test() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "medical_tc_test.csv")

def load_labels() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "medical_tc_labels.csv")