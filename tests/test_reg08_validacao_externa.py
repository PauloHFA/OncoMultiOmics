"""Teste automatizado para verificação da regra REG-08 (Validação Externa Independente).

REG-08: Validação externa antes de qualquer alegação de generalização.
"""
import json
from pathlib import Path
import pytest

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
EXT_JSON = REPORTS_DIR / "validacao_externa_gse31210.json"
EXT_MD = REPORTS_DIR / "validacao_externa_gse31210.md"
FIG_KM = REPORTS_DIR / "figures" / "km_estratificacao_externa_gse31210.png"


def test_reg08_arquivos_validacao_externa_gerados():
    assert EXT_JSON.exists(), f"Arquivo de resultado externo não encontrado: {EXT_JSON}"
    assert EXT_MD.exists(), f"Relatório de validação externa não encontrado: {EXT_MD}"
    assert FIG_KM.exists(), f"Figura de Kaplan-Meier externa não encontrada: {FIG_KM}"


def test_reg08_metricas_generalizacao_e_estratificacao():
    with open(EXT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Validar presença de coorte externa
    assert data["n_pacientes_externos"] >= 100, "Tamanho de amostra da coorte externa insuficiente!"
    assert data["n_eventos_externos"] >= 10, "Número insuficiente de eventos na coorte externa!"

    # Validar C-index no intervalo biológico razoável [0.5, 1.0]
    assert 0.50 <= data["m3_c_uno_externo"] <= 1.0, "C-index Uno de M3 na coorte externa inválido!"

    # Validar que a estratificação por ponto de corte congelado foi significante (p < 0.05)
    assert data["estratificacao_logrank_p"] < 0.05, "Estratificação de risco no teste externo não alcançou significância (p >= 0.05)!"
    assert data["estratificacao_separacao_significante"] is True

