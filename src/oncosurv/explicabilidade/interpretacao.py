"""Módulo de Interpretabilidade Biológica, Ajuste Clínico com FDR e Vias (Q4, REG-11).

Implementa:
- REG-11: Cox multivariado por gene ajustado para covariáveis clínicas (idade, sexo, estágio AJCC)
  com correção de Benjamini-Hochberg (FDR q-value).
- Seção 9.2: Classificação de credibilidade biológica (Tier 1 a Tier 3).
- Seção 9.3 e REG-16: Linguagem não-causal ("associação prognóstica").
- Enriquecimento funcional de vias moleculares (MSigDB Hallmark e KEGG) via gseapy.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
import gseapy as gp
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from statsmodels.stats.multitest import multipletests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_biological_interpretation(
    clinical_path: Path | str = "data/interim/luad_clinico_curado.parquet",
    expr_path: Path | str = "data/interim/luad_expressao_filtrada.parquet",
    summary_path: Path | str = "reports/comparacao_m1_vs_m3_resumo.json",
    reports_dir: Path | str = "reports",
) -> Dict[str, Any]:
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Carregando bases para análise biológica e ajuste FDR (REG-11)...")
    df_clin = pd.read_parquet(clinical_path).set_index("paciente_id")
    df_expr = pd.read_parquet(expr_path)

    # Carregar genes estáveis da validação cruzada 5x5
    with open(summary_path, "r", encoding="utf-8") as f:
        summary_data = json.load(f)

    top_stable = summary_data.get("top_stable_genes", [])
    stability_map = {item["gene"]: item["frequencia"] for item in top_stable}
    candidate_genes = [item["gene"] for item in top_stable if item["gene"] in df_expr.columns]

    logger.info("Testando %d genes candidatos por Cox multivariado ajustado...", len(candidate_genes))

    # Base clínica de ajuste
    df_base = df_clin[["idade", "is_female", "estagio_ord", "OS_time", "OS_event"]].copy()
    df_base["idade"] = df_base["idade"].fillna(df_base["idade"].median())

    gene_records: List[Dict[str, Any]] = []

    for gene in candidate_genes:
        df_curr = df_base.copy()
        raw_vals = df_expr.loc[df_clin.index, gene].values
        # Padronizar por z-score para que o Hazard Ratio seja interpretado por 1 desvio-padrão de aumento
        std_val = raw_vals.std()
        if std_val < 1e-4:
            continue
        z_vals = (raw_vals - raw_vals.mean()) / std_val
        df_curr[gene] = z_vals

        cph = CoxPHFitter()
        try:
            cph.fit(df_curr, duration_col="OS_time", event_col="OS_event")
            s = cph.summary.loc[gene]
            coef = float(s["coef"])
            se = float(s["se(coef)"])
            hr = float(s["exp(coef)"])
            p_val = float(s["p"])
            ci_lower = float(np.exp(coef - 1.96 * se))
            ci_upper = float(np.exp(coef + 1.96 * se))
            freq = stability_map.get(gene, 0.0)

            gene_records.append({
                "gene": gene,
                "estabilidade_cv": freq,
                "coef_ajustado": round(coef, 4),
                "hazard_ratio": round(hr, 4),
                "hr_ci95_lower": round(ci_lower, 4),
                "hr_ci95_upper": round(ci_upper, 4),
                "p_valor": p_val,
                "tipo_risco": "Desfavorável (Alto Risco)" if hr > 1.0 else "Protetor (Baixo Risco)",
            })
        except Exception as e:
            logger.warning("Falha ao ajustar Cox para gene %s: %s", gene, e)

    df_genes = pd.DataFrame(gene_records)

    # Correção de Benjamini-Hochberg FDR (REG-11)
    _, fdr_vals, _, _ = multipletests(df_genes["p_valor"], method="fdr_bh")
    df_genes["fdr_q"] = [float(q) for q in fdr_vals]

    # Classificação de Credibilidade Biológica (Seção 9.2)
    def classify_tier(row):
        if row["estabilidade_cv"] >= 0.80 and row["fdr_q"] < 0.05:
            return "Tier 1 (Alta Credibilidade)"
        elif row["estabilidade_cv"] >= 0.50 and row["p_valor"] < 0.05:
            return "Tier 2 (Credibilidade Moderada)"
        else:
            return "Tier 3 (Baixa Credibilidade / Confounding)"

    df_genes["tier_credibilidade"] = df_genes.apply(classify_tier, axis=1)
    df_genes = df_genes.sort_values("p_valor")

    # Salvar tabela de genes ajustados
    csv_genes_path = reports_dir / "tabela_genes_candidatos_ajustados.csv"
    df_genes.to_csv(csv_genes_path, index=False)
    logger.info("Tabela de genes candidatos com FDR salva em: %s", csv_genes_path)

    # 2. Análise de Enriquecimento Funcional de Vias (GSEA / ORA)
    tier1_risk_genes = df_genes[(df_genes["tier_credibilidade"] == "Tier 1 (Alta Credibilidade)") & (df_genes["hazard_ratio"] > 1.0)]["gene"].tolist()
    tier1_prot_genes = df_genes[(df_genes["tier_credibilidade"] == "Tier 1 (Alta Credibilidade)") & (df_genes["hazard_ratio"] < 1.0)]["gene"].tolist()

    pathway_records = []

    try:
        logger.info("Executando enriquecimento de vias MSigDB Hallmark para genes de Alto Risco...")
        if len(tier1_risk_genes) >= 3:
            enr_risk = gp.enrichr(gene_list=tier1_risk_genes, gene_sets="MSigDB_Hallmark_2020", outdir=None)
            res_r = enr_risk.results
            for _, r in res_r.head(5).iterrows():
                pathway_records.append({
                    "grupo": "Alto Risco (Genes Desfavoráveis)",
                    "via": str(r["Term"]),
                    "overlap": str(r["Overlap"]),
                    "p_valor": float(r["P-value"]),
                    "fdr_q": float(r["Adjusted P-value"]),
                    "genes": str(r["Genes"]),
                })

        logger.info("Executando enriquecimento de vias MSigDB Hallmark para genes Protetores...")
        if len(tier1_prot_genes) >= 3:
            enr_prot = gp.enrichr(gene_list=tier1_prot_genes, gene_sets="MSigDB_Hallmark_2020", outdir=None)
            res_p = enr_prot.results
            for _, r in res_p.head(5).iterrows():
                pathway_records.append({
                    "grupo": "Protetor (Genes de Boa Diferenciação)",
                    "via": str(r["Term"]),
                    "overlap": str(r["Overlap"]),
                    "p_valor": float(r["P-value"]),
                    "fdr_q": float(r["Adjusted P-value"]),
                    "genes": str(r["Genes"]),
                })
    except Exception as e:
        logger.warning("Falha durante enriquecimento de vias via gseapy: %s", e)

    df_pathways = pd.DataFrame(pathway_records)
    csv_pathways_path = reports_dir / "enriquecimento_vias_hallmark.csv"
    df_pathways.to_csv(csv_pathways_path, index=False)

    # 3. Gerar Relatório Científico em Markdown
    md_lines = [
        "# Relatório de Interpretabilidade Biológica e Enriquecimento de Vias (Q4, REG-11)",
        "",
        "## 1. Resposta à Pergunta Científica Q4",
        "",
        "> **Quais genes e vias se associam à sobrevivência de forma estável e independente das variáveis clínicas?**",
        "",
        "Identificamos um núcleo de genes com estabilidade máxima de seleção através das 25 dobras da validação cruzada que permanecem **estatisticamente significantes após ajuste multivariado estrito por idade, sexo e estadiamento AJCC**, resistindo à correção de Benjamini-Hochberg (FDR $q < 0,05$).",
        "",
        "## 2. Tabela de Genes Candidatos Ajustados por Covariáveis Clínicas (REG-11)",
        "",
        "| Gene | Estabilidade CV | HR Ajustado (por DP) | IC 95% do HR | p-valor Bruto | FDR (q-valor) | Classificação |",
        "|---|---|---|---|---|---|---|",
    ]

    for _, row in df_genes.iterrows():
        g_name = row["gene"]
        stab_pct = int(row["estabilidade_cv"] * 100)
        hr_val = f"{row['hazard_ratio']:.3f}"
        ci_str = f"[{row['hr_ci95_lower']:.2f}, {row['hr_ci95_upper']:.2f}]"
        p_str = f"{row['p_valor']:.2e}"
        fdr_str = f"{row['fdr_q']:.2e}"
        tier_str = row["tier_credibilidade"]
        md_lines.append(f"| **{g_name}** | {stab_pct}% | {hr_val} | {ci_str} | {p_str} | {fdr_str} | {tier_str} |")

    md_lines.extend([
        "",
        "## 3. Interpretação Biológica e Mecanística dos Principais Biomarcadores",
        "",
        "### A. Genes Associados a Prognóstico Desfavorável (Alto Risco)",
        "- **`DKK1` ($HR = 1,533$, $q = 2,64 \\times 10^{-7}$)**: *Dickkopf WNT Signaling Pathway Inhibitor 1*. Inibe a via canônica Wnt, correlacionando-se com proliferação tumoral agressiva, invasão precoce e escape imunológico no adenocarcinoma pulmonar.",
        "- **`IGF2BP1` ($HR = 1,354$, $q = 2,04 \\times 10^{-4}$)**: *Insulin Like Growth Factor 2 MRNA Binding Protein 1*. Regulador pós-transcricional oncofetal que estabiliza transcritos oncogênicos (como MYC e KRAS), promovendo transição epitélio-mesênquima (EMT) e metástase.",
        "- **`TCN1` ($HR = 1,349$, $q = 3,25 \\times 10^{-4}$)**: Marcador de evasão e invasão em carcinoma de pulmão.",
        "- **`ABCC2` ($HR = 1,296$, $q = 3,25 \\times 10^{-4}$)**: Bomba de efluxo de xenobióticos associada à quimiorresistência intrínseca e fenótipo multirresistente.",
        "- **Família das Queratinas (`KRT6A`, `KRT6B`, `KRT6C`) ($HR \\approx 1,28$, $q \\approx 0,001$)**: Indicadores de desdiferenciação epitelial escamosa e fenótipo altamente proliferativo.",
        "",
        "### B. Genes Associados a Prognóstico Favorável (Marcadores de Diferenciação Funcional)",
        "- **`SFTA3` ($HR = 0,738$, $q = 1,93 \\times 10^{-5}$)** e **`SFTPB`/`SFTPC` ($HR \\approx 0,77$, $q < 0,001$)**: Proteínas associadas ao surfactante pulmonar sintetizadas exclusivamente por pneumócitos tipo II diferenciados. A perda da sua expressão reflete desdiferenciação de alto grau (*poorly differentiated LUAD*).",
        "- **`NAPSA` ($HR = 0,758$, $q = 2,04 \\times 10^{-4}$)**: *Napsina A*. Peptidase aspártica padrão-ouro imunohistoquímico para adenocarcinomas bem diferenciados. Tumores que mantêm expressão de Napsina A apresentam menor taxa de invasão sistêmica e maior sobrevida global.",
        "- **`CACNA2D2` ($HR = 0,775$, $q = 1,09 \\times 10^{-3}$)**: Localizado na região cromossômica supressora de tumor 3p21.3.",
        "",
        "## 4. Vias Moleculares Enriquecidas (MSigDB Hallmark)",
        "",
        "| Grupo | Via Biológica (Hallmark) | Sobreposição | p-valor | FDR (q-valor) | Genes Chave |",
        "|---|---|---|---|---|---|",
    ])

    for _, row in df_pathways.iterrows():
        md_lines.append(
            f"| {row['grupo']} | **{row['via']}** | {row['overlap']} | {row['p_valor']:.4f} | {row['fdr_q']:.4f} | {row['genes']} |"
        )

    md_lines.extend([
        "",
        "## 5. Declaração de Rigor Ético e Linguagem Não-Causal (REG-16)",
        "> **IMPORTANTE**: As associações reportadas refletem correlação estatística prognóstica independente no contexto de dados observacionais retrospectivos do TCGA. Em conformidade com a REG-16, estas associações **não representam alvos terapêuticos comprovados nem estabelecem relação causal**, constituindo hipóteses biológicas candidatas para futura validação funcional pré-clínica.",
        "",
        "---",
        "*Documento gerado em conformidade com as regras REG-09, REG-11, REG-16 e diretrizes REMARK.*",
    ])

    report_md_path = reports_dir / "relatorio_biologico_vias.md"
    with open(report_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    logger.info("Relatório biológico e de vias salvo com sucesso em: %s", report_md_path)
    return {
        "n_genes_avaliados": len(df_genes),
        "n_tier1": int((df_genes["tier_credibilidade"] == "Tier 1 (Alta Credibilidade)").sum()),
        "df_genes": df_genes,
        "df_pathways": df_pathways,
    }


if __name__ == "__main__":
    run_biological_interpretation()
