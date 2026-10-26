"""Testes unitários e de integração para a interface do dashboard Streamlit (Item 3).

Verifica:
- Carregamento correto dos modelos serializados (LUAD e KIRC).
- Validação do cálculo de predição de curvas de sobrevida para pacientes simulados.
- Verificação do disclaimer de pesquisa (REG-16).
"""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
import pytest


def test_dashboard_models_availability():
    models_dir = Path("models")
    required_files = [
        "m1_cox_clinico.joblib",
        "m3_coxnet_integrado.joblib",
        "model_card_m3.json",
        "m1_kirc_cox_clinico.joblib",
        "m3_kirc_coxnet_integrado.joblib",
        "model_card_kirc_m3.json",
    ]
    for rf in required_files:
        assert (models_dir / rf).exists(), f"Arquivo essencial do modelo não encontrado: {rf}"


def test_dashboard_prediction_pipeline():
    # Testar predição para LUAD
    m1_luad = joblib.load("models/m1_cox_clinico.joblib")
    m3_luad = joblib.load("models/m3_coxnet_integrado.joblib")

    df_clin = pd.DataFrame([{"idade": 65.0, "is_female": 1, "estagio_ord": 2}])
    df_expr = pd.DataFrame([{g: 0.0 for g in m3_luad.selected_genes_}])

    times = np.array([365.25, 3 * 365.25, 5 * 365.25])

    surv_m1 = m1_luad.predict_survival_probabilities(df_clin, times)[0]
    surv_m3 = m3_luad.predict_survival_probabilities(df_clin, df_expr, times)[0]

    assert len(surv_m1) == 3
    assert len(surv_m3) == 3
    # Probabilidades devem ser decrescentes no tempo e limitadas entre 0 e 1
    assert (surv_m1 >= 0.0).all() and (surv_m1 <= 1.0).all()
    assert (surv_m3 >= 0.0).all() and (surv_m3 <= 1.0).all()
    assert surv_m1[0] >= surv_m1[1] >= surv_m1[2]
    assert surv_m3[0] >= surv_m3[1] >= surv_m3[2]


def test_dashboard_disclaimer_present():
    dashboard_file = Path("app/dashboard.py")
    assert dashboard_file.exists(), "app/dashboard.py deve existir"

    content = dashboard_file.read_text(encoding="utf-8").upper()
    assert "REG-16" in content, "Dashboard deve conter menção explícita a REG-16"
    assert "PESQUISA" in content or "RESEARCH" in content, "Dashboard deve conter aviso de pesquisa exclusiva"
    assert "DISPOSITIVO" in content, "Dashboard deve conter disclaimer de não ser dispositivo médico"
