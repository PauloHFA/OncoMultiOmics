"""Teste automatizado para verificação da regra REG-09 (Diagnóstico de Efeito de Lote).

REG-09: Diagnóstico de lote e de TSS com análise de sensibilidade.
"""
import json
from pathlib import Path
import pytest

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
BATCH_JSON = REPORTS_DIR / "diagnostico_lote_tss.json"
BATCH_MD = REPORTS_DIR / "diagnostico_lote_tss.md"
FIG_PCA = REPORTS_DIR / "figures" / "pca_diagnostico_lote_tss.png"


def test_reg09_arquivos_diagnostico_lote():
    assert BATCH_JSON.exists(), f"Arquivo de resultado de lote não encontrado: {BATCH_JSON}"
    assert BATCH_MD.exists(), f"Relatório de lote não encontrado: {BATCH_MD}"
    assert FIG_PCA.exists(), f"Figura de PCA por lote não encontrada: {FIG_PCA}"


def test_reg09_estabilidade_analise_sensibilidade():
    with open(BATCH_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Validar número de centros avaliados
    assert data["n_centros_avaliados"] >= 5, "Número insuficiente de centros TSS avaliados!"

    # Validar que a variância percentual dos HRs é baixa (< 10%)
    for gene_entry in data["sensibilidade_genes_tss"]:
        diff = gene_entry["diferenca_percentual_hr"]
        assert diff < 10.0, f"Gene {gene_entry['gene']} com instabilidade excessiva por TSS: {diff}%!"
        assert gene_entry["hr_estratificado_tss"] > 0.0, "Hazard Ratio estratificado inválido!"

