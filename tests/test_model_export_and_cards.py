"""Teste automatizado para verificação da exportação de modelos e Model Cards (Seção 17)."""
from pathlib import Path
import joblib
import pandas as pd
import pytest

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
M1_PATH = MODELS_DIR / "m1_cox_clinico.joblib"
M3_PATH = MODELS_DIR / "m3_coxnet_integrado.joblib"
CARD_JSON = MODELS_DIR / "model_card_m3.json"
CARD_MD = MODELS_DIR / "MODEL_CARD.md"
DEPS_JSON = MODELS_DIR / "dependencies.json"


def test_model_files_exist():
    assert M1_PATH.exists(), f"Arquivo M1 não encontrado em {M1_PATH}"
    assert M3_PATH.exists(), f"Arquivo M3 não encontrado em {M3_PATH}"
    assert CARD_JSON.exists(), f"Model Card JSON não encontrado em {CARD_JSON}"
    assert CARD_MD.exists(), f"Model Card MD não encontrado em {CARD_MD}"
    assert DEPS_JSON.exists(), f"Lista de dependências não encontrada em {DEPS_JSON}"


def test_serialized_model_inference():
    m3 = joblib.load(M3_PATH)
    assert hasattr(m3, "predict_risk"), "O modelo M3 serializado não possui método predict_risk!"
    assert len(m3.selected_genes_) > 0, "Nenhum gene selecionado no modelo M3!"

    # Teste de inferência
    dummy_clin = pd.DataFrame({
        "idade": [60.0],
        "is_female": [1],
        "estagio_ord": [2],
    })
    dummy_expr = pd.DataFrame({g: [1.0] for g in m3.selected_genes_})

    risk = m3.predict_risk(dummy_clin, dummy_expr)
    assert len(risk) == 1, "A predição deve retornar exatamente 1 valor para 1 amostra!"
    assert not pd.isna(risk[0]), "Predição retornou valor nulo/NaN!"
