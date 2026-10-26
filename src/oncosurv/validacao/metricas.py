"""Módulo de Métricas de Sobrevivência (REG-05).

Calcula:
- C-index de Uno com IPCW e horizonte tau (concordance_index_ipcw)
- C-index de Harrell (concordance_index_censored)
- AUC Dinâmico Cumulativo nos horizontes 1, 3 e 5 anos (cumulative_dynamic_auc)
- Integrated Brier Score (IBS)
"""
import logging
from typing import Dict, Any, List
import numpy as np
from sksurv.metrics import (
    concordance_index_ipcw,
    concordance_index_censored,
    cumulative_dynamic_auc,
    integrated_brier_score,
)

logger = logging.getLogger(__name__)


def compute_survival_metrics(
    y_train: np.ndarray,
    y_test: np.ndarray,
    risk_pred_test: np.ndarray,
    surv_pred_grid_test: np.ndarray | None = None,
    grid_times: np.ndarray | None = None,
    tau_days: float = 5 * 365.25,
    eval_horizons_years: List[float] = [1.0, 3.0, 5.0],
) -> Dict[str, float]:
    """Calcula o painel completo de métricas de avaliação de sobrevivência (REG-05).

    Args:
        y_train: Array estruturado Surv(event, time) de treino
        y_test: Array estruturado Surv(event, time) de teste
        risk_pred_test: Escore de risco predito no conjunto de teste (maior = pior prognóstico)
        surv_pred_grid_test: Matriz (n_amostras, n_tempos) de probabilidades S(t|x) previstas
        grid_times: Tempos correspondentes às colunas de surv_pred_grid_test
        tau_days: Horizonte tau pré-registrado
        eval_horizons_years: Anos para cálculo da AUC cumulativa dinâmica

    Returns:
        Dicionário com as métricas calculadas
    """
    metrics = {}

    # 1. C-index de Harrell (tradicional, sensível à censura)
    c_harrell = concordance_index_censored(y_test["event"], y_test["time"], risk_pred_test)[0]
    metrics["c_index_harrell"] = float(c_harrell)

    # 2. C-index de Uno com IPCW no horizonte tau (REG-05)
    # Uno IPCW requer que tau seja estritamente inferior ao tempo máximo observado no teste
    max_test_time = y_test["time"].max()
    effective_tau = min(tau_days, max_test_time - 1e-3)
    try:
        c_uno = concordance_index_ipcw(y_train, y_test, risk_pred_test, tau=effective_tau)[0]
        metrics["c_index_uno"] = float(c_uno)
    except Exception as e:
        logger.warning("Falha ao calcular C-index de Uno: %s. Usando NaN.", e)
        metrics["c_index_uno"] = np.nan

    # 3. Dynamic AUC cumulativo (1, 3 e 4.5/5 anos)
    try:
        horizons_days = []
        horizon_labels = []
        for h in eval_horizons_years:
            target_t = h * 365.25
            # Ajustar para ficar estritamente dentro de (t_min, t_max)
            if target_t >= max_test_time:
                target_t = max_test_time - 10.0
            if y_test["time"].min() < target_t < max_test_time and target_t not in horizons_days:
                horizons_days.append(target_t)
                horizon_labels.append(f"auc_dynamic_{int(h)}yr")

        if len(horizons_days) > 0:
            aucs, mean_auc = cumulative_dynamic_auc(
                y_train, y_test, risk_pred_test, np.array(horizons_days)
            )
            for lbl, auc_val in zip(horizon_labels, aucs):
                metrics[lbl] = float(auc_val)
            metrics["auc_dynamic_mean"] = float(mean_auc)
        else:
            metrics["auc_dynamic_mean"] = np.nan
    except Exception as e:
        logger.warning("Falha ao calcular Dynamic AUC: %s", e)
        metrics["auc_dynamic_mean"] = np.nan

    # 4. Integrated Brier Score (IBS)
    if surv_pred_grid_test is not None and grid_times is not None:
        try:
            # Filtrar grid_times para estarem estritamente dentro do suporte do teste
            valid_idx = (grid_times > y_test["time"].min()) & (grid_times < max_test_time)
            if valid_idx.sum() >= 2:
                filtered_times = grid_times[valid_idx]
                filtered_preds = surv_pred_grid_test[:, valid_idx]
                ibs = integrated_brier_score(y_train, y_test, filtered_preds, filtered_times)
                metrics["integrated_brier_score"] = float(ibs)
            else:
                metrics["integrated_brier_score"] = np.nan
        except Exception as e:
            logger.warning("Falha ao calcular IBS: %s", e)
            metrics["integrated_brier_score"] = np.nan

    return metrics
