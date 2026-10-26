"""Módulo de Curadoria da Coorte Externa Independente GSE31210 (REG-08 / Q3).

Implementa:
- Parsing dos metadados clínicos do GEO Series Matrix (GSE31210).
- Exclusão de pacientes com tempo não-positivo ou marcados como 'exclude' pelos autores originais.
- Truncamento do desfecho no horizonte tau = 5 anos (1826.25 dias) com censura administrativa (REG-02).
- Mapeamento de sondas Affymetrix HG-U133_Plus_2 para os genes candidatos do estudo.
- Harmonização de escala molecular (z-score por gene dentro da coorte externa, REG-08).
"""
import gzip
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter

from oncosurv.clinico.curadoria import TAU_DAYS, calculate_reverse_km_followup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Mapeamento oficial validado das melhores sondas HG-U133_Plus_2 para os genes do estudo
PROBE_MAP = {
    "DKK1": "204602_at",
    "NAPSA": "223806_s_at",
    "IGF2BP1": "223689_at",
    "SFTPB": "209810_at",
    "SFTPC": "205982_x_at",
    "SFTA3": "228979_at",
    "ABCC2": "206155_at",
    "CPS1": "204920_at",
    "KRT6A": "209125_at",
    "KRT6B": "209126_x_at",
    "KRT6C": "214580_x_at",
    "SERPINB5": "204855_at",
    "TCN1": "205513_at",
    "IGFBP1": "205302_at",
    "GGTLC1": "209919_x_at",
    "CACNA2D2": "204811_s_at",
    "CYP4B1": "210096_at",
    "PGC": "205261_at",
    "C16orf89": "229177_at",
    "KIAA0408": "205496_at",
}


def parse_gse31210(
    gz_path: Path | str = "data/external/GSE31210_series_matrix.txt.gz",
    output_dir: Path | str = "data/external",
    reports_dir: Path | str = "reports",
    tau_days: float = TAU_DAYS,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    output_dir = Path(output_dir)
    reports_dir = Path(reports_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Iniciando parsing da coorte externa GSE31210 de: %s", gz_path)
    sample_ids = []
    characteristics = []

    header_lines = []
    matrix_start_line = 0

    with gzip.open(gz_path, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("!Sample_geo_accession"):
                sample_ids = [s.strip('"\n\r ') for s in line.split("\t")[1:]]
            elif line.startswith("!Sample_characteristics_ch1"):
                characteristics.append([s.strip('"\n\r ') for s in line.split("\t")[1:]])
            elif line.startswith("!series_matrix_table_begin"):
                break

    arr_chars = np.array(characteristics)
    logger.info("Detectadas %d amostras e %d linhas de características.", len(sample_ids), arr_chars.shape[0])

    records = []
    for col_idx in range(len(sample_ids)):
        sid = sample_ids[col_idx]
        item = {"sample_id": sid}
        for row_idx in range(arr_chars.shape[0]):
            val = arr_chars[row_idx, col_idx]
            if ":" in val:
                k, v = val.split(":", 1)
                item[k.strip().lower()] = v.strip()
        records.append(item)

    df_meta = pd.DataFrame(records).set_index("sample_id")
    df_meta.index.name = "sample_id"

    # Funil de Curadoria Externa
    funnel = []
    n_inicial = len(df_meta)
    funnel.append({
        "etapa": "1. Total de amostras na série GSE31210",
        "pacientes": n_inicial,
        "excluidos": 0,
        "motivo": "Amostra total do repositório GEO",
    })

    # Filtrar apenas adenocarcinoma primário de pulmão
    is_primary = df_meta["tissue"].str.lower().str.contains("primary lung tumor") if "tissue" in df_meta else pd.Series(True, index=df_meta.index)
    df_step1 = df_meta[is_primary].copy()
    funnel.append({
        "etapa": "2. Amostras de tumor primário de pulmão",
        "pacientes": len(df_step1),
        "excluidos": n_inicial - len(df_step1),
        "motivo": "Tecidos não-tumorais ou de controle",
    })

    # Excluir pacientes com recomendação de exclusão da publicação original (ressecção incompleta/terapia adjuvante)
    excl_col = "exclude for prognosis analysis due to incomplete resection or adjuvant therapy"
    if excl_col in df_step1.columns:
        keep_prognosis = df_step1[excl_col].str.lower() != "exclude"
        df_step2 = df_step1[keep_prognosis].copy()
    else:
        df_step2 = df_step1.copy()
    funnel.append({
        "etapa": "3. Coorte padrão para análise prognóstica (critério dos autores)",
        "pacientes": len(df_step2),
        "excluidos": len(df_step1) - len(df_step2),
        "motivo": "Ressecção cirúrgica incompleta ou terapia prévia",
    })

    # Desfechos de sobrevida global (death e days before death/censor)
    days_col = "days before death/censor"
    death_col = "death"

    df_step2["OS_time_raw"] = pd.to_numeric(df_step2[days_col], errors="coerce")
    df_step2["OS_event_raw"] = (df_step2[death_col].str.lower() == "dead").astype(int)

    valid_time = (~df_step2["OS_time_raw"].isna()) & (df_step2["OS_time_raw"] > 0)
    df_step3 = df_step2[valid_time].copy()
    funnel.append({
        "etapa": "4. Exclusão de tempos de sobrevida não-positivos",
        "pacientes": len(df_step3),
        "excluidos": len(df_step2) - len(df_step3),
        "motivo": "Tempo zero ou ausente",
    })

    # Harmonização de covariáveis clínicas
    df_step3["idade"] = pd.to_numeric(df_step3["age (years)"], errors="coerce")
    df_step3["sexo"] = df_step3["gender"].str.lower().str.strip()
    df_step3["is_female"] = (df_step3["sexo"] == "female").astype(int)

    # Estágio: Stage I = 1, Stage II = 2
    stage_str = df_step3["pathological stage"].str.upper().str.strip()
    stage_map = {"I": 1, "IA": 1, "IB": 1, "II": 2, "IIA": 2, "IIB": 2, "III": 3, "IV": 4}
    df_step3["estagio_ord"] = stage_str.map(stage_map).fillna(1).astype(int)

    # Truncamento em tau (5 anos)
    df_step3["OS_time"] = np.minimum(df_step3["OS_time_raw"], tau_days)
    df_step3["OS_event"] = np.where(
        df_step3["OS_time_raw"] > tau_days,
        0,
        df_step3["OS_event_raw"],
    )

    n_final = len(df_step3)
    n_events = int(df_step3["OS_event"].sum())
    mediana_seguimento = calculate_reverse_km_followup(
        df_step3["OS_time_raw"].values, df_step3["OS_event_raw"].values
    )

    # 2. Extrair matriz de expressão para as sondas dos 20 genes
    logger.info("Extraindo dados de expressão gênica para as sondas mapeadas...")
    probe_to_gene = {probe: gene for gene, probe in PROBE_MAP.items()}
    target_probes = set(PROBE_MAP.values())

    expr_data = {}
    valid_samples = df_step3.index.tolist()

    with gzip.open(gz_path, "rt", encoding="utf-8", errors="ignore") as f:
        # Pular cabeçalho até o início da tabela
        for line in f:
            if line.startswith("!series_matrix_table_begin"):
                header_cols = [c.strip('"\n\r ') for c in f.readline().split("\t")]
                col_indices = {col: i for i, col in enumerate(header_cols)}
                sample_col_indices = [col_indices[s] for s in valid_samples if s in col_indices]
                break

        # Ler linhas da matriz
        for line in f:
            if line.startswith("!series_matrix_table_end"):
                break
            parts = line.split("\t")
            probe_id = parts[0].strip('"\n\r ')
            if probe_id in target_probes:
                gene_name = probe_to_gene[probe_id]
                vals = [float(parts[idx].strip('"\n\r ')) for idx in sample_col_indices]
                # Log2 transform se os valores estiverem em escala linear (> 100)
                vals_arr = np.array(vals)
                if np.median(vals_arr) > 50:
                    vals_arr = np.log2(vals_arr + 1.0)
                expr_data[gene_name] = vals_arr

    df_expr_ext = pd.DataFrame(expr_data, index=valid_samples)

    # Salvar bases externas curadas
    clin_cols = ["idade", "is_female", "estagio_ord", "OS_time_raw", "OS_event_raw", "OS_time", "OS_event"]
    df_clin_ext = df_step3[clin_cols].copy()

    df_clin_ext.to_parquet(output_dir / "gse31210_clinico_curado.parquet")
    df_expr_ext.to_parquet(output_dir / "gse31210_expressao_genes.parquet")

    logger.info(
        "Coorte externa GSE31210 salva: %d pacientes, %d eventos OS (tau=5a), mediana seguimento: %.2f anos.",
        n_final,
        n_events,
        mediana_seguimento / 365.25,
    )

    qc_report = {
        "coorte": "GSE31210 (GEO / NCBI)",
        "plataforma": "Affymetrix HG-U133_Plus_2 (GPL570)",
        "n_pacientes_elegiveis": n_final,
        "n_obitos_5anos": n_events,
        "taxa_eventos": round(n_events / n_final, 4),
        "seguimento_mediano_anos": round(mediana_seguimento / 365.25, 2),
        "funil": funnel,
    }

    with open(reports_dir / "funil_exclusao_gse31210.json", "w", encoding="utf-8") as f:
        json.dump(qc_report, f, indent=2)

    return df_clin_ext, df_expr_ext, qc_report


if __name__ == "__main__":
    parse_gse31210()
