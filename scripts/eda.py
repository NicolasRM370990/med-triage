from pathlib import Path

import pandas as pd

"""
Caminhos Datasets
"""
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data" / "raw"

train = pd.read_csv(DATA_DIR / "medical_tc_train.csv")
test = pd.read_csv(DATA_DIR / "medical_tc_test.csv")
labels = pd.read_csv(DATA_DIR / "medical_tc_labels.csv")


print("\nDataset:")
print(f"TREINO: {train}")
print(f"TESTE: {test}")
print(f"LABELS: {labels}")

print("\n" + "=" * 70)

print("\nShape:")
print(f"TREINO: {train.shape}")
print(f"TESTE: {test.shape}")
print(f"LABELS: {labels.shape}")
print("\n" + "=" * 70)

print("\nColunas:")
print(f"TREINO: {train.columns.to_list()}")
print(f"TESTE: {test.columns.to_list()}")
print(f"LABELS: {labels.columns.to_list()}")

print("\n" + "=" * 70)
print("\nTipo:")
print(f"TREINO: {train.dtypes}")
print(f"TESTE: {test.dtypes}")
print(f"LABELS: {labels.dtypes}")

print("\n" + "=" * 70)
print("\nNulos")
print(f"TREINO: {train.isnull().sum()}")
print(f"TESTE: {test.isnull().sum()}")
print(f"LABELS: {labels.isnull().sum()}")

print("=" * 70)
print("DISTRIBUIÇÃO DAS CLASSES")

print("\nTRAIN:")
print(train["condition_label"].value_counts().sort_index())

print("\nTEST:")
print(test["condition_label"].value_counts().sort_index())



print("=" * 70)
print("DUPLICADOS")
print(f"TRAIN : {train.duplicated().sum():,}")
print(f"TEST  : {test.duplicated().sum():,}")

