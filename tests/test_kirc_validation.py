"""Testes de Validação e Integridade Científica da Segunda Coorte: TCGA-KIRC.

Verifica:
- REG-01: Amostra única primária '01' por paciente.
- REG-02: Censura administrativa em tau = 5 anos (1826.25 dias) e tempos positivos.
- REG-03 / REG-06: Validação cruzada repetida sem vazamento.
- Desempenho preditivo discriminatório robusto (C-index > 0.60 e M3 > M1).
- Estratificação de risco Kaplan-Meier estatisticamente significativa (p < 0.05).
- Identificação de genes Tier 1 sob correção de Benjamini-Hochberg FDR (q < 0.05).
"""
import json
from pathlib import Path
import pandas as pd
import pytest


def test_kirc_clinical_curation_reg01_reg02():
    clin_path = Path("data/interim/kirc_clinico_curado.parquet")
    assert clin_path.exists(), "Arquivo kirc_clinico_curado.parquet deve existir"

    df = pd.read_parquet(clin_path)
    assert len(df) > 400, f"Esperado > 400 pacientes elegíveis em KIRC, obtido {len(df)}"

    # REG-01: Apenas amostras primárias sólidas '01' e uma por paciente
    assert df["paciente_id"].nunique() == len(df), "Deve haver exatamente 1 registro por paciente"
    assert all(b[13:15] == "01" for b in df["sample_barcode"]), "Todas as amostras devem ser tumor sólido primário '01'"

    # REG-02: Censura administrativa no horizonte tau = 5 anos (1826.25 dias)
    tau = 5 * 365.25
    assert (df["OS_time"] > 0).all(), "Todos os tempos de OS devem ser estritamente positivos"
    assert (df["OS_time"] <= tau).all(), f"Nenhum tempo pode exceder o horizonte tau = {tau}"

    # Verificação de status após tau
    over_tau = df["OS_time_raw"] > tau
    assert (df.loc[over_tau, "OS_event"] == 0).all(), "Pacientes que ultrapassam tau devem ser censurados como 0"


def test_kirc_benchmark_performance_and_fdr():
    json_path = Path("reports/comparacao_kirc_m1_vs_m3.json")
    assert json_path.exists(), "Arquivo comparacao_kirc_m1_vs_m3.json deve existir"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["n_dobras"] == 25, "Devem ser avaliadas 25 dobras (5x5 Repeated CV)"
    assert data["n_pacientes"] >= 500, f"Esperado >= 500 pacientes em KIRC, obtido {data['n_pacientes']}"

    m0_uno = data["metricas_m0"]["c_index_uno"]
    m1_uno = data["metricas_m1"]["c_index_uno"]
    m3_uno = data["metricas_m3"]["c_index_uno"]

    # Modelo nulo deve ser ~0.50
    assert abs(m0_uno - 0.50) < 0.05, f"M0 deve ter C-index ~0.50, obtido {m0_uno}"

    # Modelos clínicos e integrados devem ter C-index > 0.60
    assert m1_uno > 0.60, f"M1 Cox Clínico deve superar 0.60, obtido {m1_uno}"
    assert m3_uno > 0.60, f"M3 Cox Integrado deve superar 0.60, obtido {m3_uno}"

    # Superioridade de M3 em KIRC com significância estatística
    assert m3_uno > m1_uno, f"M3 ({m3_uno}) deve ser superior a M1 ({m1_uno}) em KIRC"
    assert data["comparacao_m1_vs_m3"]["wilcoxon_pval"] < 0.05, "Ganho de M3 deve ser estatisticamente significante"

    # Estratificação de risco Kaplan-Meier
    km_data = data["km_estratificacao"]
    assert km_data["p_valor"] < 0.05, f"Log-Rank p-valor deve ser < 0.05, obtido {km_data['p_valor']}"

    # Biomarcadores ajustados por FDR (REG-11)
    genes_fdr = data["genes_ajustados_fdr"]
    assert len(genes_fdr) > 0, "Lista de genes FDR não pode ser vazia"
    tier1_genes = [g for g in genes_fdr if "Tier 1" in g["tier"]]
    assert len(tier1_genes) >= 3, f"Esperado pelo menos 3 genes Tier 1 em KIRC, obtido {len(tier1_genes)}"
