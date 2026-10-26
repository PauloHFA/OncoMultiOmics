"""Teste automatizado para verificação da regra REG-05 (Calibração e IBS).

REG-05: Reportar C-index de Uno, AUC dependente do tempo, IBS e calibração.
"""
import json
from pathlib import Path
import pytest

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
CALIB_JSON = REPORTS_DIR / "calibracao_nomograma_resumo.json"
CALIB_MD = REPORTS_DIR / "relatorio_calibracao_nomograma.md"
FIG_CALIB = REPORTS_DIR / "figures" / "calibracao_multi_horizontes_m3.png"
FIG_NOMO = REPORTS_DIR / "figures" / "nomograma_pesos_m3.png"


def test_reg05_arquivos_calibracao_gerados():
    assert CALIB_JSON.exists(), f"Resumo de calibração não encontrado: {CALIB_JSON}"
    assert CALIB_MD.exists(), f"Relatório de calibração não encontrado: {CALIB_MD}"
    assert FIG_CALIB.exists() and FIG_CALIB.stat().st_size > 10000, "Figura de calibração ausente ou inválida!"
    assert FIG_NOMO.exists() and FIG_NOMO.stat().st_size > 10000, "Figura de nomograma ausente ou inválida!"


def test_reg05_metricas_calibracao_slopes():
    with open(CALIB_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    calib_dict = data["calibracao_horizontes"]
    for horizon, metrics in calib_dict.items():
        slope = metrics["calibration_slope"]
        ici = metrics["mean_absolute_error_ici"]

        # Inclinação deve estar na faixa aceitável [0.5, 2.0] (ideal = 1.0)
        assert 0.5 <= slope <= 2.0, f"Inclinação de calibração fora da faixa em {horizon}: {slope}!"
        # Erro médio absoluto deve ser < 25%
        assert ici < 0.25, f"Erro médio de calibração (ICI) excessivo em {horizon}: {ici}!"

