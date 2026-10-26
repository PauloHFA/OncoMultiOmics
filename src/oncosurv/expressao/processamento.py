"""Módulo de Pré-Processamento Molecular (RNA-Seq).

Implementa:
- Filtragem de amostras primárias ('01') harmonizadas com a base clínica.
- Filtro de baixa expressão não-supervisionado (>= 20% das amostras com log2(exp+1) > 1.0).
- Estruturação em formato amostras x genes (494 x n_genes) indexada por paciente_id.
- Conformidade com REG-03: nenhuma padronização/seleção supervisionada antes da CV!
"""
import logging
from pathlib import Path
from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def process_rna_seq(
    raw_rna_path: Path | str = "data/raw/TCGA_LUAD_HiSeqV2.gz",
    clinical_path: Path | str = "data/interim/luad_clinico_curado.parquet",
    output_path: Path | str = "data/interim/luad_expressao_filtrada.parquet",
    min_expression_threshold: float = 1.0,
    min_fraction_samples: float = 0.20,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Lê a matriz de expressão gênica bruta e aplica filtragem de controle de qualidade não-supervisionada."""
    raw_rna_path = Path(raw_rna_path)
    clinical_path = Path(clinical_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Carregando base clínica curada de: %s", clinical_path)
    clin = pd.read_parquet(clinical_path)
    eligible_barcodes = clin["sample_barcode"].tolist()
    barcode_to_patient = dict(zip(clin["sample_barcode"], clin["paciente_id"]))

    logger.info("Carregando matriz de expressão RNA-Seq de: %s", raw_rna_path)
    df_raw = pd.read_csv(raw_rna_path, sep="\t", index_col=0)
    n_genes_total, n_samples_raw = df_raw.shape
    logger.info("Dimensões brutas: %d genes x %d amostras", n_genes_total, n_samples_raw)

    # 1. Manter apenas amostras da coorte clínica curada
    matched_cols = [c for c in df_raw.columns if c in eligible_barcodes]
    df_sub = df_raw[matched_cols].copy()
    # Renomear colunas para paciente_id e reordenar conforme a base clínica
    df_sub.columns = [barcode_to_patient[c] for c in df_sub.columns]
    ordered_patients = clin["paciente_id"].tolist()
    df_sub = df_sub[ordered_patients]

    # 2. Filtro não-supervisionado de baixa expressão
    # Expressão > limiar em pelo menos X% das amostras
    fraction_expressed = (df_sub > min_expression_threshold).mean(axis=1)
    pass_filter = fraction_expressed >= min_fraction_samples
    df_filtered = df_sub.loc[pass_filter].copy()

    # 3. Remover genes com desvio padrão nulo
    gene_stds = df_filtered.std(axis=1)
    valid_var = gene_stds > 1e-4
    df_filtered = df_filtered.loc[valid_var]

    n_genes_final = len(df_filtered)
    logger.info("Genes após filtros: %d (removidos: %d)", n_genes_final, n_genes_total - n_genes_final)

    # 4. Transpor para o formato padrão do Scikit-Learn: (amostras, genes)
    df_samples_x_genes = df_filtered.T
    df_samples_x_genes.index.name = "paciente_id"

    # Salvar em parquet
    df_samples_x_genes.to_parquet(output_path)
    logger.info("Matriz molecular salva em: %s (Dimensões: %s)", output_path, df_samples_x_genes.shape)

    qc_report = {
        "n_genes_inicial": n_genes_total,
        "n_genes_final": n_genes_final,
        "n_genes_removidos_baixa_expressao": int((~pass_filter).sum()),
        "n_amostras_alinhadas": len(df_samples_x_genes),
        "limiar_expressao": min_expression_threshold,
        "fracao_minima_amostras": min_fraction_samples,
    }
    return df_samples_x_genes, qc_report


if __name__ == "__main__":
    process_rna_seq()

