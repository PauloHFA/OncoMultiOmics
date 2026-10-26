"""Teste automatizado para verificação estrita da regra REG-01 e integridade clínica.

REG-01: Uma amostra tumoral primária por paciente; sem duplicatas.
REG-02: Desfecho e horizonte tau definidos antes de modelar.
"""
from pathlib import Path
import pandas as pd
import pytest

CLINICAL_FILE = Path(__file__).resolve().parent.parent / "data" / "interim" / "luad_clinico_curado.parquet"


@pytest.fixture(scope="module")
def clinical_df():
    assert CLINICAL_FILE.exists(), f"Arquivo curado não encontrado em {CLINICAL_FILE}. Execute a curadoria primeiro."
    return pd.read_parquet(CLINICAL_FILE)


def test_reg01_uma_amostra_primaria_por_paciente(clinical_df):
    """Garante que não existem duplicatas de paciente e que todas as amostras são tumor primário ('01')."""
    # 1. Sem duplicatas de paciente
    assert clinical_df["paciente_id"].is_unique, "REG-01 violada: existem pacientes duplicados na base curada!"

    # 2. Todas as amostras são '01' (tumor sólido primário)
    sample_types = clinical_df["sample_barcode"].str[13:15]
    assert (sample_types == "01").all(), "REG-01 violada: existem amostras não-primárias (ex: 11 normal ou 06 metástase)!"


def test_reg02_consistencia_desfecho_e_tau(clinical_df):
    """Garante que tempos são estritamente positivos e horizonte tau está devidamente aplicado."""
    # Tempos estritamente positivos
    assert (clinical_df["OS_time_raw"] > 0).all(), "Existem tempos não-positivos (OS.time <= 0)!"
    assert (clinical_df["OS_time"] > 0).all(), "Existem tempos truncados não-positivos!"

    # Truncamento em tau (5 anos = 1826.25 dias)
    tau = 5 * 365.25
    assert (clinical_df["OS_time"] <= tau + 1e-5).all(), "Existem tempos superiores a tau no desfecho truncado!"

    # Censura administrativa em tau
    censored_at_tau = clinical_df["OS_time_raw"] > tau
    assert (clinical_df.loc[censored_at_tau, "OS_event"] == 0).all(), "Pacientes que faleceram após tau devem ser censurados em tau!"


def test_consistencia_estagio_e_covariaveis(clinical_df):
    """Garante que estágios estão harmonizados em I-IV e sexo está binário."""
    valid_stages = {"Stage I", "Stage II", "Stage III", "Stage IV"}
    assert set(clinical_df["estagio_ajcc"].unique()).issubset(valid_stages), "Estágios AJCC contêm valores não-harmonizados!"

    assert set(clinical_df["is_female"].unique()).issubset({0, 1}), "is_female deve ser estritamente binário (0 ou 1)!"

