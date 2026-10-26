"""Módulo de Execução de Validação Cruzada Estratificada Repetida (5x5).

Implementa:
- REG-03: Sem vazamento entre treino e teste.
- REG-05: Avaliação abrangente (Uno C-index, Harrell, Dynamic AUC 1/3/5 anos, IBS).
- REG-06: Validação cruzada repetida estratificada por evento.
"""
import logging
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.model_selection import RepeatedStratifiedKFold
from sksurv.util import Surv

from oncosurv.modelos.baselines import NullKaplanMeierModel, ClinicalCoxModel
from oncosurv.validacao.metricas import compute_survival_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def evaluate_baselines_repeated_cv(
    clinical_path: Path | str = "data/interim/luad_clinico_curado.parquet",
    n_splits: int = 5,
    n_repeats: int = 5,
    random_state: int = 42,
    tau_days: float = 5 * 365.25,
) -> Dict[str, Any]:
    """Executa a validação cruzada 5x5 estratificada para os modelos baselines M0 e M1."""
    clinical_path = Path(clinical_path)
    logger.info("Carregando base clínica curada de: %s", clinical_path)
    df_clin = pd.read_parquet(clinical_path)

    # Definir features clínicas de baseline (M1)
    # Variáveis clínicas recomendadas: idade, sexo (is_female), estágio AJCC ordinal
    clinical_feature_cols = ["idade", "is_female", "estagio_ord"]
    X_clin = df_clin[clinical_feature_cols]

    # Alvo de sobrevivência estruturado
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

    m0_results: List[Dict[str, float]] = []
    m1_results: List[Dict[str, float]] = []

    total_folds = n_splits * n_repeats
    logger.info(
        "Iniciando CV 5x5 (%d dobras) estratificada por evento para M0 e M1...",
        total_folds,
    )

    fold_idx = 0
    for train_idx, test_idx in rskf.split(X_clin, y["event"]):
        fold_idx += 1
        X_train, X_test = X_clin.iloc[train_idx], X_clin.iloc[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        # -------------------------------------------------------------
        # 1. Ajustar Modelo Nulo M0 (Kaplan-Meier)
        # -------------------------------------------------------------
        m0 = NullKaplanMeierModel().fit(y_train)
        m0_risk_pred = m0.predict_risk(len(X_test))
        m0_surv_grid = m0.predict_survival_probabilities(grid_times, len(X_test))

        m0_metrics = compute_survival_metrics(
            y_train=y_train,
            y_test=y_test,
            risk_pred_test=m0_risk_pred,
            surv_pred_grid_test=m0_surv_grid,
            grid_times=grid_times,
            tau_days=tau_days,
        )
        m0_metrics["fold"] = fold_idx
        m0_results.append(m0_metrics)

        # -------------------------------------------------------------
        # 2. Ajustar Modelo Clínico M1 (Cox PH)
        # -------------------------------------------------------------
        m1 = ClinicalCoxModel().fit(X_train, y_train)
        m1_risk_pred = m1.predict_risk(X_test)
        m1_surv_grid = m1.predict_survival_probabilities(X_test, grid_times)

        m1_metrics = compute_survival_metrics(
            y_train=y_train,
            y_test=y_test,
            risk_pred_test=m1_risk_pred,
            surv_pred_grid_test=m1_surv_grid,
            grid_times=grid_times,
            tau_days=tau_days,
        )
        m1_metrics["fold"] = fold_idx
        m1_results.append(m1_metrics)

    df_m0 = pd.DataFrame(m0_results)
    df_m1 = pd.DataFrame(m1_results)

    # Métricas agregadas
    summary = {
        "m0_null": {
            "c_uno_mean": float(df_m0["c_index_uno"].mean()),
            "c_uno_std": float(df_m0["c_index_uno"].std()),
            "c_harrell_mean": float(df_m0["c_index_harrell"].mean()),
            "ibs_mean": float(df_m0["integrated_brier_score"].mean()),
            "ibs_std": float(df_m0["integrated_brier_score"].std()),
        },
        "m1_clinical": {
            "c_uno_mean": float(df_m1["c_index_uno"].mean()),
            "c_uno_std": float(df_m1["c_index_uno"].std()),
            "c_uno_ci95": [
                float(df_m1["c_index_uno"].quantile(0.025)),
                float(df_m1["c_index_uno"].quantile(0.975)),
            ],
            "c_harrell_mean": float(df_m1["c_index_harrell"].mean()),
            "c_harrell_std": float(df_m1["c_index_harrell"].std()),
            "auc_1yr_mean": float(df_m1["auc_dynamic_1yr"].mean()) if "auc_dynamic_1yr" in df_m1 else np.nan,
            "auc_3yr_mean": float(df_m1["auc_dynamic_3yr"].mean()) if "auc_dynamic_3yr" in df_m1 else np.nan,
            "auc_5yr_mean": float(df_m1["auc_dynamic_5yr"].mean()) if "auc_dynamic_5yr" in df_m1 else np.nan,
            "auc_mean_mean": float(df_m1["auc_dynamic_mean"].mean()) if "auc_dynamic_mean" in df_m1 else np.nan,
            "ibs_mean": float(df_m1["integrated_brier_score"].mean()),
            "ibs_std": float(df_m1["integrated_brier_score"].std()),
        },
    }

    logger.info("=== Resultados da Validação Cruzada 5x5 ===")
    logger.info(
        "M0 Nulo - C-index Uno: %.4f | IBS: %.4f",
        summary["m0_null"]["c_uno_mean"],
        summary["m0_null"]["ibs_mean"],
    )
    logger.info(
        "M1 Clínico - C-index Uno: %.4f (DP: %.4f, IC95: [%.4f, %.4f])",
        summary["m1_clinical"]["c_uno_mean"],
        summary["m1_clinical"]["c_uno_std"],
        summary["m1_clinical"]["c_uno_ci95"][0],
        summary["m1_clinical"]["c_uno_ci95"][1],
    )
    logger.info(
        "M1 Clínico - Dynamic AUC 1 ano: %.4f | 3 anos: %.4f | 5 anos: %.4f (Média: %.4f)",
        summary["m1_clinical"]["auc_1yr_mean"],
        summary["m1_clinical"]["auc_3yr_mean"],
        summary["m1_clinical"]["auc_5yr_mean"],
        summary["m1_clinical"]["auc_mean_mean"],
    )
    logger.info(
        "M1 Clínico - IBS: %.4f (vs M0: %.4f, Redução de erro: %.2f%%)",
        summary["m1_clinical"]["ibs_mean"],
        summary["m0_null"]["ibs_mean"],
        (1 - summary["m1_clinical"]["ibs_mean"] / summary["m0_null"]["ibs_mean"]) * 100,
    )

    # Salvar resultados detalhados por dobra
    output_dir = Path("reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    df_m1.to_csv(output_dir / "m1_clinico_folds_5x5.csv", index=False)
    df_m0.to_csv(output_dir / "m0_nulo_folds_5x5.csv", index=False)

    return summary


if __name__ == "__main__":
    evaluate_baselines_repeated_cv()
