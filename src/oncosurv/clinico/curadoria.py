"""Módulo de Curadoria Clínica e Desfechos (Fase 1).

Implementa:
- REG-01: Uma amostra primária ('01') por paciente.
- REG-02: Definição de desfecho e horizonte tau = 5 anos com censura administrativa.
- REG-13: Funil de exclusão detalhado com seguimento mediano via Kaplan-Meier Reverso.
"""
import gzip
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

TAU_DAYS = 5 * 365.25  # 1826.25 dias (5 anos)


def harmonize_ajcc_stage(stage_raw: Any) -> str | None:
    """Harmoniza subestágios do AJCC para os estágios clínicos principais I, II, III e IV."""
    if pd.isna(stage_raw):
        return None
    s = str(stage_raw).strip()
    if s in ["[Discrepancy]", "NA", "null", ""]:
        return None
    if s.startswith("Stage IV"):
        return "Stage IV"
    if s.startswith("Stage III"):
        return "Stage III"
    if s.startswith("Stage II"):
        return "Stage II"
    if s.startswith("Stage I"):
        return "Stage I"
    return None


def calculate_reverse_km_followup(time: np.ndarray, event: np.ndarray) -> float:
    """Calcula o seguimento mediano pelo método de Kaplan-Meier reverso (evento invertido)."""
    km_rev = KaplanMeierFitter()
    # No KM reverso, os censurados originais (0) viram eventos (1) e vice-versa
    km_rev.fit(time, 1 - event)
    return float(km_rev.median_survival_time_)


def run_clinical_curation(
    cdr_path: Path | str,
    rna_path: Path | str,
    cbioportal_sample_path: Path | str | None = None,
    output_dir: Path | str = "data/interim",
    reports_dir: Path | str = "reports",
    tau_days: float = TAU_DAYS,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Executa a curadoria clínica rigorosa e gera o funil de exclusão."""
    output_dir = Path(output_dir)
    reports_dir = Path(reports_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    funnel = []

    # 1. Carregar TCGA-CDR
    logger.info("Carregando TCGA-CDR de: %s", cdr_path)
    cdr = pd.read_csv(cdr_path, sep="\t")
    luad_cdr = cdr[cdr["cancer type abbreviation"] == "LUAD"].copy()
    n_inicial = len(luad_cdr)
    funnel.append({
        "etapa": "1. Total TCGA-LUAD no TCGA-CDR",
        "pacientes": n_inicial,
        "excluidos": 0,
        "motivo": "Amostra bruta do estudo",
    })

    # Deduplicar paciente no CDR se houver mais de uma linha clínica (manter primeira válida)
    luad_cdr = luad_cdr.drop_duplicates(subset=["_PATIENT"], keep="first")
    n_cdr_unique = len(luad_cdr)
    funnel.append({
        "etapa": "2. Pacientes únicos no TCGA-CDR",
        "pacientes": n_cdr_unique,
        "excluidos": n_inicial - n_cdr_unique,
        "motivo": "Duplicatas de registro no arquivo clínico",
    })

    # 2. Ler barcodes RNA-seq para filtrar amostras primárias '01' (REG-01)
    logger.info("Inspecionando barcodes RNA-Seq de: %s", rna_path)
    with gzip.open(rna_path, "rt") as f:
        rna_barcodes = f.readline().strip().split("\t")[1:]

    # REG-01: Filtrar apenas tumor sólido primário ('01')
    tumor_samples = {}
    for b in rna_barcodes:
        if len(b) >= 15:
            patient_id = b[:12]
            sample_type = b[13:15]
            if sample_type == "01":
                if patient_id not in tumor_samples:
                    tumor_samples[patient_id] = b

    # Intersecção clínica + molecular
    luad_matched = luad_cdr[luad_cdr["_PATIENT"].isin(tumor_samples.keys())].copy()
    luad_matched["sample_barcode"] = luad_matched["_PATIENT"].map(tumor_samples)
    n_matched = len(luad_matched)
    funnel.append({
        "etapa": "3. Pacientes com RNA-Seq tumoral primário ('01')",
        "pacientes": n_matched,
        "excluidos": n_cdr_unique - n_matched,
        "motivo": "Ausência de amostra tumoral primária (01) com RNA-Seq",
    })

    # 3. Exclusão por tempo não-positivo ou faltante (T <= 0 ou NaN)
    valid_time = (~luad_matched["OS.time"].isna()) & (luad_matched["OS.time"] > 0)
    luad_valid_time = luad_matched[valid_time].copy()
    n_valid_time = len(luad_valid_time)
    funnel.append({
        "etapa": "4. Exclusão de tempos de seguimento nulos ou não-positivos (OS.time <= 0)",
        "pacientes": n_valid_time,
        "excluidos": n_matched - n_valid_time,
        "motivo": "Seguimento zero ou tempo de evento inválido",
    })

    # 4. Harmonização de Estágio AJCC
    luad_valid_time["estagio_ajcc"] = luad_valid_time["ajcc_pathologic_tumor_stage"].apply(harmonize_ajcc_stage)
    valid_stage = ~luad_valid_time["estagio_ajcc"].isna()
    luad_final = luad_valid_time[valid_stage].copy()
    n_final = len(luad_final)
    funnel.append({
        "etapa": "5. Exclusão de estadiamento AJCC indefinido / discrepante",
        "pacientes": n_final,
        "excluidos": n_valid_time - n_final,
        "motivo": "Estágio patológico ausente ou [Discrepancy]",
    })

    # 5. Tratamento de variáveis clínicas
    luad_final["paciente_id"] = luad_final["_PATIENT"]
    luad_final["idade"] = pd.to_numeric(luad_final["age_at_initial_pathologic_diagnosis"], errors="coerce")
    luad_final["sexo"] = luad_final["gender"].str.upper().str.strip()
    luad_final["is_female"] = (luad_final["sexo"] == "FEMALE").astype(int)
    luad_final["tss_code"] = luad_final["paciente_id"].str[5:7]

    # Codificação ordinal do estágio AJCC (I=1, II=2, III=3, IV=4)
    stage_map = {"Stage I": 1, "Stage II": 2, "Stage III": 3, "Stage IV": 4}
    luad_final["estagio_ord"] = luad_final["estagio_ajcc"].map(stage_map)

    # 6. Desfechos com corte administrativo em tau (REG-02)
    luad_final["OS_time_raw"] = luad_final["OS.time"].astype(float)
    luad_final["OS_event_raw"] = luad_final["OS"].astype(int)

    # Truncamento administrativo em tau
    luad_final["OS_time"] = np.minimum(luad_final["OS_time_raw"], tau_days)
    luad_final["OS_event"] = np.where(
        luad_final["OS_time_raw"] > tau_days,
        0,  # Se faleceu após tau, considera-se censurado em tau
        luad_final["OS_event_raw"],
    )

    # PFI (Intervalo Livre de Progressão)
    luad_final["PFI_time_raw"] = pd.to_numeric(luad_final["PFI.time"], errors="coerce")
    luad_final["PFI_event_raw"] = pd.to_numeric(luad_final["PFI"], errors="coerce").fillna(0).astype(int)
    luad_final["PFI_time"] = np.minimum(luad_final["PFI_time_raw"].fillna(0), tau_days)
    luad_final["PFI_event"] = np.where(
        luad_final["PFI_time_raw"] > tau_days,
        0,
        luad_final["PFI_event_raw"],
    )

    # 7. Estatísticas da Coorte Final Curada
    total_eventos_raw = int(luad_final["OS_event_raw"].sum())
    total_eventos_tau = int(luad_final["OS_event"].sum())
    mediana_seguimento_rev_km = calculate_reverse_km_followup(
        luad_final["OS_time_raw"].values, luad_final["OS_event_raw"].values
    )

    metricas_coorte = {
        "n_pacientes": n_final,
        "eventos_OS_total": total_eventos_raw,
        "taxa_eventos_OS_total": round(total_eventos_raw / n_final, 4),
        "eventos_OS_tau_5anos": total_eventos_tau,
        "taxa_eventos_OS_tau_5anos": round(total_eventos_tau / n_final, 4),
        "seguimento_mediano_dias_km_reverso": round(mediana_seguimento_rev_km, 1),
        "seguimento_mediano_anos_km_reverso": round(mediana_seguimento_rev_km / 365.25, 2),
        "distribuicao_estagio": luad_final["estagio_ajcc"].value_counts().to_dict(),
        "distribuicao_sexo": luad_final["sexo"].value_counts().to_dict(),
        "idade_media": round(float(luad_final["idade"].mean()), 2),
        "idade_faltantes": int(luad_final["idade"].isna().sum()),
    }

    # Salvar resultados
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
        "PFI_time_raw",
        "PFI_event_raw",
        "PFI_time",
        "PFI_event",
    ]
    df_export = luad_final[cols_export].copy()

    parquet_path = output_dir / "luad_clinico_curado.parquet"
    tsv_path = output_dir / "luad_clinico_curado.tsv"
    df_export.to_parquet(parquet_path, index=False)
    df_export.to_csv(tsv_path, sep="\t", index=False)
    logger.info("Base clínica curada salva em: %s e %s", parquet_path, tsv_path)

    # Salvar funil e métricas em JSON e Markdown
    relatorio_funil = {
        "coorte": "TCGA-LUAD",
        "desfecho_primario": "OS (Overall Survival)",
        "horizonte_tau_dias": tau_days,
        "horizonte_tau_anos": tau_days / 365.25,
        "funil": funnel,
        "metricas_coorte": metricas_coorte,
    }
    with open(reports_dir / "funil_exclusao_luad.json", "w", encoding="utf-8") as f:
        json.dump(relatorio_funil, f, indent=2, ensure_ascii=False)

    md_funil = [
        "# Relatório de Curadoria Clínica e Funil de Exclusão — TCGA-LUAD",
        "",
        f"- **Coorte**: TCGA-LUAD (*Lung Adenocarcinoma*)",
        f"- **Desfecho Primário**: Sobrevida Global (OS) com horizonte $\\tau = 5\\text{{ anos}}$ ({tau_days:.1f} dias)",
        f"- **Seguimento Mediano (KM Reverso)**: {mediana_seguimento_rev_km/365.25:.2f} anos ({mediana_seguimento_rev_km:.1f} dias)",
        "",
        "## 1. Funil de Exclusão (REG-01, REG-13)",
        "",
        "| Etapa | Pacientes Restantes | Excluídos | Motivo da Exclusão |",
        "|---|---|---|---|",
    ]
    for row in funnel:
        md_funil.append(f"| {row['etapa']} | {row['pacientes']} | {row['excluidos']} | {row['motivo']} |")

    md_funil.extend([
        "",
        "## 2. Estatísticas da Coorte Final Elegível",
        "",
        f"- **Total de Pacientes Elegíveis**: {n_final}",
        f"- **Óbitos Observados (OS Bruto)**: {total_eventos_raw} ({total_eventos_raw/n_final*100:.1f}%)",
        f"- **Óbitos no Horizonte $\\tau$ (5 Anos)**: {total_eventos_tau} ({total_eventos_tau/n_final*100:.1f}%)",
        f"- **Distribuição de Estágio AJCC**:",
    ])
    for stg, cnt in luad_final["estagio_ajcc"].value_counts().items():
        md_funil.append(f"  - {stg}: {cnt} ({cnt/n_final*100:.1f}%)")

    md_funil.extend([
        f"- **Sexo**: Feminino = {int(luad_final['is_female'].sum())} ({luad_final['is_female'].mean()*100:.1f}%), Masculino = {int((1-luad_final['is_female']).sum())} ({(1-luad_final['is_female']).mean()*100:.1f}%)",
        f"- **Idade**: Média de {luad_final['idade'].mean():.1f} anos (Valores ausentes: {int(luad_final['idade'].isna().sum())} — serão imputados via mediana intra-fold)",
        "",
        "---",
        "*Documento gerado automaticamente pelo pipeline de curadoria em conformidade com REG-01 e REG-13.*",
    ])
    with open(reports_dir / "funil_exclusao_luad.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_funil))

    logger.info("Relatório de curadoria e funil salvo em: %s", reports_dir / "funil_exclusao_luad.md")
    return df_export, relatorio_funil


if __name__ == "__main__":
    run_clinical_curation(
        cdr_path="data/raw/TCGA_CDR_SupplementalTable_S1.tsv",
        rna_path="data/raw/TCGA_LUAD_HiSeqV2.gz",
    )
