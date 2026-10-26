"""Teste automatizado para verificação da regra REG-11 (Ajuste Clínico com FDR).

REG-11: Testes por gene com FDR e ajuste clínico.
"""
from pathlib import Path
import pandas as pd
import pytest

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
GENES_CSV = REPORTS_DIR / "tabela_genes_candidatos_ajustados.csv"
REPORT_MD = REPORTS_DIR / "relatorio_biologico_vias.md"


def test_reg11_arquivos_gerados():
    assert GENES_CSV.exists(), f"Tabela de genes ajustados não encontrada em {GENES_CSV}"
    assert REPORT_MD.exists(), f"Relatório de vias não encontrado em {REPORT_MD}"


def test_reg11_integridade_estatistica_fdr():
    df = pd.read_csv(GENES_CSV)
    assert len(df) > 0, "A tabela de genes candidatos está vazia!"

    # P-valores e FDR q-valores válidos [0, 1]
    assert (df["p_valor"] >= 0.0).all() and (df["p_valor"] <= 1.0).all(), "P-valores fora do intervalo [0, 1]!"
    assert (df["fdr_q"] >= 0.0).all() and (df["fdr_q"] <= 1.0).all(), "FDR q-valores fora do intervalo [0, 1]!"

    # Hazard Ratios positivos
    assert (df["hazard_ratio"] > 0.0).all(), "Hazard Ratio deve ser estritamente positivo!"

    # Tier 1 deve respeitar estabilidade >= 80% e FDR < 0.05
    tier1 = df[df["tier_credibilidade"] == "Tier 1 (Alta Credibilidade)"]
    assert len(tier1) > 0, "Nenhum gene alcançou classificação Tier 1!"
    assert (tier1["estabilidade_cv"] >= 0.80).all(), "Gene Tier 1 com estabilidade inferior a 80%!"
    assert (tier1["fdr_q"] < 0.05).all(), "Gene Tier 1 com FDR superior a 0.05!"

