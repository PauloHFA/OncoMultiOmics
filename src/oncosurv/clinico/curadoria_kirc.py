"""Módulo de Curadoria Clínica e Molecular da Segunda Coorte: TCGA-KIRC (Seção 3.3 / REG-01, REG-02).

Implementa:
- Curadoria clínica estrita do Carcinoma Renal de Células Claras (KIRC) a partir do TCGA-CDR.
- REG-01: Filtro de 1 amostra primária sólida ('01') por paciente.
- REG-02: Censura administrativa no horizonte tau = 5 anos (1826.25 dias).
- Filtragem não-supervisionada da matriz de expressão RNA-Seq (HiSeqV2).
- Exportação dos conjuntos curados em data/interim/ e geração do funil de exclusão em reports/.
"""
import gzip
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter

from oncosurv.clinico.curadoria import TAU_DAYS, harmonize_ajcc_stage, calculate_reverse_km_followup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_kirc_curation(
    cdr_path: Path | str = "data/raw/TCGA_CDR_SupplementalTable_S1.tsv",
    rna_path: Path | str = "data/raw/TCGA_KIRC_HiSeqV2.gz",
    output_dir: Path | str = "data/interim",
    reports_dir: Path | str = "reports",
    tau_days: float = TAU_DAYS,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    output_dir = Path(output_dir)
    reports_dir = Path(reports_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Iniciando curadoria clínica de TCGA-KIRC...")
    cdr = pd.read_csv(cdr_path, sep="\t")
    kirc_cdr = cdr[cdr["cancer type abbreviation"] == "KIRC"].copy()
    n_inicial = len(kirc_cdr)

    funnel = []
    funnel.append({
        "etapa": "1. Total TCGA-KIRC no TCGA-CDR",
        "pacientes": n_inicial,
        "excluidos": 0,
        "motivo": "Registros brutos do consórcio",
    })

    # Deduplicar paciente no CDR
    kirc_cdr = kirc_cdr.drop_duplicates(subset=["_PATIENT"], keep="first")
    n_cdr_unique = len(kirc_cdr)
    funnel.append({
        "etapa": "2. Pacientes únicos no TCGA-CDR",
        "pacientes": n_cdr_unique,
        "excluidos": n_inicial - n_cdr_unique,
        "motivo": "Duplicatas de registro clínico",
    })

    # Ler barcodes RNA-seq para filtrar amostras primárias '01'
    with gzip.open(rna_path, "rt") as f:
        rna_barcodes = f.readline().strip().split("\t")[1:]

    tumor_samples = {}
    for b in rna_barcodes:
        if len(b) >= 15 and b[13:15] == "01":
            patient_id = b[:12]
            if patient_id not in tumor_samples:
                tumor_samples[patient_id] = b

    kirc_matched = kirc_cdr[kirc_cdr["_PATIENT"].isin(tumor_samples.keys())].copy()
    kirc_matched["sample_barcode"] = kirc_matched["_PATIENT"].map(tumor_samples)
    n_matched = len(kirc_matched)
    funnel.append({
        "etapa": "3. Pacientes com RNA-Seq tumoral primário ('01')",
        "pacientes": n_matched,
        "excluidos": n_cdr_unique - n_matched,
        "motivo": "Ausência de RNA-Seq de tumor sólido primário (01)",
    })

    # Exclusão por tempo não-positivo
    valid_time = (~kirc_matched["OS.time"].isna()) & (kirc_matched["OS.time"] > 0)
    kirc_valid_time = kirc_matched[valid_time].copy()
    n_valid_time = len(kirc_valid_time)
    funnel.append({
        "etapa": "4. Exclusão de tempos de seguimento nulos ou não-positivos (OS.time <= 0)",
        "pacientes": n_valid_time,
        "excluidos": n_matched - n_valid_time,
        "motivo": "Seguimento zero ou inválido",
    })

    # Harmonização de estágio AJCC
    kirc_valid_time["estagio_ajcc"] = kirc_valid_time["ajcc_pathologic_tumor_stage"].apply(harmonize_ajcc_stage)
    valid_stage = ~kirc_valid_time["estagio_ajcc"].isna()
    kirc_final = kirc_valid_time[valid_stage].copy()
    n_final = len(kirc_final)
    funnel.append({
        "etapa": "5. Exclusão de estadiamento AJCC indefinido / [Discrepancy]",
        "pacientes": n_final,
        "excluidos": n_valid_time - n_final,
        "motivo": "Estágio não-classificável",
    })

    # Covariáveis clínicas
    kirc_final["paciente_id"] = kirc_final["_PATIENT"]
    kirc_final["idade"] = pd.to_numeric(kirc_final["age_at_initial_pathologic_diagnosis"], errors="coerce")
    kirc_final["sexo"] = kirc_final["gender"].str.upper().str.strip()
    kirc_final["is_female"] = (kirc_final["sexo"] == "FEMALE").astype(int)
    kirc_final["tss_code"] = kirc_final["paciente_id"].str[5:7]

    stage_map = {"Stage I": 1, "Stage II": 2, "Stage III": 3, "Stage IV": 4}
    kirc_final["estagio_ord"] = kirc_final["estagio_ajcc"].map(stage_map)

    # Desfechos de sobrevida com truncamento em tau (5 anos)
    kirc_final["OS_time_raw"] = kirc_final["OS.time"].astype(float)
    kirc_final["OS_event_raw"] = kirc_final["OS"].astype(int)

    kirc_final["OS_time"] = np.minimum(kirc_final["OS_time_raw"], tau_days)
    kirc_final["OS_event"] = np.where(
        kirc_final["OS_time_raw"] > tau_days,
        0,
        kirc_final["OS_event_raw"],
    )

    n_events_raw = int(kirc_final["OS_event_raw"].sum())
    n_events_tau = int(kirc_final["OS_event"].sum())
    mediana_seguimento = calculate_reverse_km_followup(
        kirc_final["OS_time_raw"].values, kirc_final["OS_event_raw"].values
    )

    # Exportar tabela clínica
    cols_export = [
        "paciente_id",
        "sample_barcode",
        "tss_code",
        "idade",
        "sexo",
        "is_female",
        "estagio_ajcc",
        "estagio_ord",
        "OS_time_raw",
        "OS_event_raw",
        "OS_time",
        "OS_event",
    ]
    df_clin_exp = kirc_final[cols_export].copy()
    df_clin_exp.to_parquet(output_dir / "kirc_clinico_curado.parquet", index=False)

    # 2. Pré-Processamento Molecular (RNA-Seq)
    logger.info("Processando matriz de expressão RNA-Seq do TCGA-KIRC...")
    df_raw_rna = pd.read_csv(rna_path, sep="\t", index_col=0)
    matched_cols = [c for c in df_raw_rna.columns if c in kirc_final["sample_barcode"].tolist()]
    df_sub_rna = df_raw_rna[matched_cols].copy()

    barcode_to_patient = dict(zip(kirc_final["sample_barcode"], kirc_final["paciente_id"]))
    df_sub_rna.columns = [barcode_to_patient[c] for c in df_sub_rna.columns]
    df_sub_rna = df_sub_rna[kirc_final["paciente_id"].tolist()]

    # Filtro não-supervisionado: expressão > 1.0 em >= 20% das amostras
    pass_filter = (df_sub_rna > 1.0).mean(axis=1) >= 0.20
    df_filt_rna = df_sub_rna.loc[pass_filter].copy()

    # Remover variância nula
    df_filt_rna = df_filt_rna.loc[df_filt_rna.std(axis=1) > 1e-4]
    df_expr_exp = df_filt_rna.T
    df_expr_exp.index.name = "paciente_id"
    df_expr_exp.to_parquet(output_dir / "kirc_expressao_filtrada.parquet")

    logger.info(
        "KIRC curado: %d pacientes, %d eventos tau=5a (%.1f%%), seguimento mediano: %.2f anos, %d genes filtrados.",
        n_final,
        n_events_tau,
        n_events_tau / n_final * 100,
        mediana_seguimento / 365.25,
        df_expr_exp.shape[1],
    )

    qc_report = {
        "coorte": "TCGA-KIRC (Kidney Renal Clear Cell Carcinoma)",
        "desfecho_primario": "OS (Overall Survival)",
        "horizonte_tau_dias": tau_days,
        "n_pacientes_elegiveis": n_final,
        "n_obitos_brutos": n_events_raw,
        "n_obitos_tau_5anos": n_events_tau,
        "taxa_obitos_5anos": round(n_events_tau / n_final, 4),
        "seguimento_mediano_anos": round(mediana_seguimento / 365.25, 2),
        "distribuicao_estagio": kirc_final["estagio_ajcc"].value_counts().to_dict(),
        "n_genes_filtrados": df_expr_exp.shape[1],
        "funil": funnel,
    }

    with open(reports_dir / "funil_exclusao_kirc.json", "w", encoding="utf-8") as f:
        json.dump(qc_report, f, indent=2, ensure_ascii=False)

    md_lines = [
        "# Relatório de Curadoria Clínica e Funil de Exclusão — TCGA-KIRC",
        "",
        "- **Coorte**: TCGA-KIRC (*Kidney Renal Clear Cell Carcinoma*)",
        f"- **Desfecho Primário**: Sobrevida Global (OS) com horizonte $\\tau = 5\\text{{ anos}}$ ({tau_days:.1f} dias)",
        f"- **Seguimento Mediano (KM Reverso)**: {mediana_seguimento/365.25:.2f} anos ({mediana_seguimento:.1f} dias)",
        "",
        "## 1. Funil de Exclusão (REG-01, REG-13)",
        "",
        "| Etapa | Pacientes Restantes | Excluídos | Motivo da Exclusão |",
        "|---|---|---|---|",
    ]
    for row in funnel:
        md_lines.append(f"| {row['etapa']} | {row['pacientes']} | {row['excluidos']} | {row['motivo']} |")

    md_lines.extend([
        "",
        "## 2. Estatísticas da Coorte Final Elegível",
        f"- **Total de Pacientes Elegíveis**: {n_final}",
        f"- **Óbitos Observados (OS Bruto)**: {n_events_raw} ({n_events_raw/n_final*100:.1f}%)",
        f"- **Óbitos no Horizonte $\\tau$ (5 Anos)**: {n_events_tau} ({n_events_tau/n_final*100:.1f}%)",
        "- **Distribuição por Estágio AJCC**:",
    ])
    for stg, cnt in kirc_final["estagio_ajcc"].value_counts().items():
        md_lines.append(f"  - {stg}: {cnt} ({cnt/n_final*100:.1f}%)")

    md_lines.extend([
        f"- **Sexo**: Feminino = {int(kirc_final['is_female'].sum())} ({kirc_final['is_female'].mean()*100:.1f}%), Masculino = {int((1-kirc_final['is_female']).sum())} ({(1-kirc_final['is_female']).mean()*100:.1f}%)",
        f"- **Idade**: Média de {kirc_final['idade'].mean():.1f} anos",
        f"- **Genes Expressos Mantidos**: {df_expr_exp.shape[1]} genes",
        "",
        "---",
        "*Documento gerado automaticamente pelo pipeline de curadoria em conformidade com REG-01 e REG-13.*",
    ])

    with open(reports_dir / "funil_exclusao_kirc.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    return df_clin_exp, df_expr_exp, qc_report


if __name__ == "__main__":
    run_kirc_curation()

