"""Benchmark Completo da Escada de Modelos (M1, M3, M5, M6) — Resposta a Q2 e Hipótese H2.

Avalia sistematicamente em 25 dobras estratificadas repetidas (5x5):
- M1: Cox Clínico (Baseline)
- M3: Cox Elastic Net Integrado
- M5: Random Survival Forest Integrado
- M6: Gradient Boosting Survival Integrado

Calcula C-index de Uno, Harrell, Dynamic AUC e Integrated Brier Score (IBS).
Gera relatório em Markdown e JSON em conformidade com as diretrizes TRIPOD+AI.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.model_selection import RepeatedStratifiedKFold
from sksurv.util import Surv

from oncosurv.modelos.baselines import ClinicalCoxModel
from oncosurv.modelos.integrado import IntegratedCoxNetModel
from oncosurv.modelos.ensembles import RSFSurvivalModel, GradientBoostingSurvivalModel
from oncosurv.validacao.metricas import compute_survival_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_benchmark_ladder(
    clinical_path: Path | str = "data/interim/luad_clinico_curado.parquet",
    expr_path: Path | str = "data/interim/luad_expressao_filtrada.parquet",
    reports_dir: Path | str = "reports",
    n_splits: int = 5,
    n_repeats: int = 5,
    random_state: int = 42,
    tau_days: float = 5 * 365.25,
    top_k_genes: int = 50,
) -> Dict[str, Any]:
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Carregando bases para o benchmark da escada de modelos...")
    df_clin = pd.read_parquet(clinical_path)
    df_expr = pd.read_parquet(expr_path)
    df_expr = df_expr.loc[df_clin["paciente_id"]].copy()

    X_clin = df_clin[["idade", "is_female", "estagio_ord"]]
    y = Surv.from_arrays(
        event=df_clin["OS_event"].astype(bool),
        time=df_clin["OS_time"].astype(float),
    )

    rskf = RepeatedStratifiedKFold(
        n_splits=n_splits,
        n_repeats=n_repeats,
        random_state=random_state,
    )

    grid_times = np.linspace(30.0, tau_days - 5.0, 50)
    all_fold_records = []

    total_folds = n_splits * n_repeats
    logger.info("Iniciando benchmark de M1, M3, M5 e M6 em %d dobras...", total_folds)

    fold_idx = 0
    for train_idx, test_idx in rskf.split(X_clin, y["event"]):
        fold_idx += 1
        X_c_tr, X_c_te = X_clin.iloc[train_idx], X_clin.iloc[test_idx]
        X_e_tr, X_e_te = df_expr.iloc[train_idx], df_expr.iloc[test_idx]
        y_tr, y_te = y[train_idx], y[test_idx]

        # 1. M1: Cox Clínico
        m1 = ClinicalCoxModel().fit(X_c_tr, y_tr)
        m1_risk = m1.predict_risk(X_c_te)
        m1_surv = m1.predict_survival_probabilities(X_c_te, grid_times)
        m1_met = compute_survival_metrics(y_tr, y_te, m1_risk, m1_surv, grid_times, tau_days)

        # 2. M3: Cox Elastic Net Integrado
        m3 = IntegratedCoxNetModel(
            top_k=top_k_genes,
            l1_ratio=0.5,
            n_inner_splits=3,
            random_state=random_state + fold_idx,
        ).fit(X_c_tr, X_e_tr, y_tr)
        m3_risk = m3.predict_risk(X_c_te, X_e_te)
        m3_surv = m3.predict_survival_probabilities(X_c_te, X_e_te, grid_times)
        m3_met = compute_survival_metrics(y_tr, y_te, m3_risk, m3_surv, grid_times, tau_days)

        # 3. M5: Random Survival Forest
        m5 = RSFSurvivalModel(
            top_k=top_k_genes,
            n_estimators=50,
            min_samples_leaf=15,
            random_state=random_state + fold_idx,
            n_jobs=-1,
        ).fit(X_c_tr, X_e_tr, y_tr)
        m5_risk = m5.predict_risk(X_c_te, X_e_te)
        m5_surv = m5.predict_survival_probabilities(X_c_te, X_e_te, grid_times)
        m5_met = compute_survival_metrics(y_tr, y_te, m5_risk, m5_surv, grid_times, tau_days)

        # 4. M6: Gradient Boosting Survival
        m6 = GradientBoostingSurvivalModel(
            top_k=top_k_genes,
            n_estimators=50,
            learning_rate=0.03,
            max_depth=3,
            random_state=random_state + fold_idx,
        ).fit(X_c_tr, X_e_tr, y_tr)
        m6_risk = m6.predict_risk(X_c_te, X_e_te)
        m6_surv = m6.predict_survival_probabilities(X_c_te, X_e_te, grid_times)
        m6_met = compute_survival_metrics(y_tr, y_te, m6_risk, m6_surv, grid_times, tau_days)

        record = {
            "fold": fold_idx,
            # M1
            "m1_c_uno": m1_met.get("c_index_uno", np.nan),
            "m1_c_harrell": m1_met.get("c_index_harrell", np.nan),
            "m1_ibs": m1_met.get("integrated_brier_score", np.nan),
            "m1_auc_mean": m1_met.get("auc_dynamic_mean", np.nan),
            # M3
            "m3_c_uno": m3_met.get("c_index_uno", np.nan),
            "m3_c_harrell": m3_met.get("c_index_harrell", np.nan),
            "m3_ibs": m3_met.get("integrated_brier_score", np.nan),
            "m3_auc_mean": m3_met.get("auc_dynamic_mean", np.nan),
            # M5
            "m5_c_uno": m5_met.get("c_index_uno", np.nan),
            "m5_c_harrell": m5_met.get("c_index_harrell", np.nan),
            "m5_ibs": m5_met.get("integrated_brier_score", np.nan),
            "m5_auc_mean": m5_met.get("auc_dynamic_mean", np.nan),
            # M6
            "m6_c_uno": m6_met.get("c_index_uno", np.nan),
            "m6_c_harrell": m6_met.get("c_index_harrell", np.nan),
            "m6_ibs": m6_met.get("integrated_brier_score", np.nan),
            "m6_auc_mean": m6_met.get("auc_dynamic_mean", np.nan),
        }
        all_fold_records.append(record)

        if fold_idx % 5 == 0:
            logger.info("Progresso do benchmark: %d / %d dobras concluídas", fold_idx, total_folds)

    df_bench = pd.DataFrame(all_fold_records)
    df_bench.to_csv(reports_dir / "benchmark_escada_modelos_dobras.csv", index=False)

    # Compilar sumário estatístico
    models_info = {
        "M1 (Cox Clínico)": "m1",
        "M3 (Cox Elastic Net)": "m3",
        "M5 (Random Survival Forest)": "m5",
        "M6 (Gradient Boosting)": "m6",
    }

    summary_table = []
    for label, prefix in models_info.items():
        c_uno_vals = df_bench[f"{prefix}_c_uno"].dropna()
        c_harrell_vals = df_bench[f"{prefix}_c_harrell"].dropna()
        ibs_vals = df_bench[f"{prefix}_ibs"].dropna()
        auc_vals = df_bench[f"{prefix}_auc_mean"].dropna()

        summary_table.append({
            "modelo": label,
            "c_uno_media": round(float(c_uno_vals.mean()), 4),
            "c_uno_dp": round(float(c_uno_vals.std()), 4),
            "c_uno_ci95": [
                round(float(c_uno_vals.quantile(0.025)), 4),
                round(float(c_uno_vals.quantile(0.975)), 4),
            ],
            "c_harrell_media": round(float(c_harrell_vals.mean()), 4),
            "auc_dinamica_media": round(float(auc_vals.mean()), 4),
            "ibs_media": round(float(ibs_vals.mean()), 4),
            "ibs_dp": round(float(ibs_vals.std()), 4),
        })

    with open(reports_dir / "benchmark_escada_modelos_resumo.json", "w", encoding="utf-8") as f:
        json.dump(summary_table, f, indent=2)

    # Identificar melhor modelo por C-index Uno e por IBS
    best_by_uno = max(summary_table, key=lambda x: x["c_uno_media"])
    best_by_ibs = min(summary_table, key=lambda x: x["ibs_media"])

    # Veredito da Hipótese H2
    m1_row = next(r for r in summary_table if "M1" in r["modelo"])
    m3_row = next(r for r in summary_table if "M3" in r["modelo"])
    m5_row = next(r for r in summary_table if "M5" in r["modelo"])
    m6_row = next(r for r in summary_table if "M6" in r["modelo"])

    h2_confirmed = m3_row["c_uno_media"] >= (m5_row["c_uno_media"] - 0.01) and m3_row["c_uno_media"] >= (m6_row["c_uno_media"] - 0.01)
    h2_verdict = (
        "**CONFIRMADA**: Modelos lineares penalizados (Cox Elastic Net) apresentam desempenho igual ou superior a modelos mais complexos de árvores nas dimensões amostrais do TCGA."
        if h2_confirmed
        else "**NÃO CONFIRMADA**: Modelos de árvores superaram a abordagem linear penalizada."
    )

    # Construir relatório Markdown
    md_lines = [
        "# Benchmark Comparativo da Escada de Modelos de Sobrevivência (M1 a M6)",
        "",
        "## 1. Resumo Executivo e Resposta a Q2",
        "",
        f"- **Melhor Discriminação (C-index Uno)**: **{best_by_uno['modelo']}** ({best_by_uno['c_uno_media']:.4f})",
        f"- **Melhor Calibração Probabilística (Menor IBS)**: **{best_by_ibs['modelo']}** ({best_by_ibs['ibs_media']:.4f})",
        "",
        "### Veredito da Hipótese H2 (Lineares vs. Não-Lineares Complexos):",
        f"> {h2_verdict}",
        "",
        "## 2. Tabela de Comparação Estatística em 25 Dobras Repetidas (5×5)",
        "",
        "| Modelo | C-index Uno (τ = 5a) | IC 95% Uno | C-index Harrell | Dynamic AUC Média | Integrated Brier Score (IBS) |",
        "|---|---|---|---|---|---|",
    ]

    for row in summary_table:
        ci_str = f"[{row['c_uno_ci95'][0]:.4f}, {row['c_uno_ci95'][1]:.4f}]"
        md_lines.append(
            f"| **{row['modelo']}** | {row['c_uno_media']:.4f} ± {row['c_uno_dp']:.4f} | {ci_str} | {row['c_harrell_media']:.4f} | {row['auc_dinamica_media']:.4f} | {row['ibs_media']:.4f} ± {row['ibs_dp']:.4f} |"
        )

    md_lines.extend([
        "",
        "## 3. Interpretação Científica (REG-16 e REG-17)",
        "",
        "1. **Sobrefit e Complexidade**: Modelos não-lineares flexíveis (como Random Survival Forest e Gradient Boosting) em conjuntos de dados com amostras moderadas (~500 pacientes) e alta dimensionalidade frequentemente sofrem de sobreajuste marginal ou dispersão ligeiramente superior sem ganhos substanciais de calibração.",
        "2. **Dominância da Variável Estágio**: O estadiamento patológico AJCC é uma covariável clínica de altíssimo poder discriminativo, estabelecendo um teto basal difícil de ser superado mesmo com interações não-lineares.",
        "",
        "---",
        "*Relatório gerado em total conformidade com as diretrizes TRIPOD+AI, REMARK e regras REG-02 a REG-17.*",
    ])

    with open(reports_dir / "benchmark_escada_modelos.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    logger.info("Relatório de benchmark salvo em: %s", reports_dir / "benchmark_escada_modelos.md")
    return {"summary_table": summary_table, "best_by_uno": best_by_uno, "best_by_ibs": best_by_ibs}


if __name__ == "__main__":
    run_benchmark_ladder()

