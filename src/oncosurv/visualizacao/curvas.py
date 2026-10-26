"""Módulo de Visualização Científica: Estratificação de Risco (Q5, REG-12) e Curvas KM.

Implementa:
- REG-12: Ponto de corte (mediana) calculado EXCLUSIVAMENTE no conjunto de treino.
- Plotagem de curvas de Kaplan-Meier com intervalos de confiança e teste log-rank.
- Salvamento em reports/figures/.
"""
from pathlib import Path
from typing import Dict, Any, Tuple
import matplotlib
matplotlib.use("Agg")  # Backend não-interativo para geração de figuras
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test


def plot_risk_stratification_km(
    train_risk: np.ndarray,
    test_risk: np.ndarray,
    test_time: np.ndarray,
    test_event: np.ndarray,
    output_path: Path | str = "reports/figures/km_estratificacao_risco.png",
    model_name: str = "Modelo Integrado (M3)",
) -> Dict[str, Any]:
    """Estratifica pacientes de teste em Alto e Baixo Risco usando o ponto de corte do treino (REG-12)."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # REG-12: Ponto de corte definido estritamente no treino
    cutoff_threshold = float(np.median(train_risk))

    # Aplicar o ponto de corte ao teste
    is_high_risk = test_risk > cutoff_threshold

    # Teste Log-Rank no teste
    lr_res = logrank_test(
        durations_A=test_time[is_high_risk],
        durations_B=test_time[~is_high_risk],
        event_observed_A=test_event[is_high_risk],
        event_observed_B=test_event[~is_high_risk],
    )

    # Plotar Curvas Kaplan-Meier
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)

    km_high = KaplanMeierFitter()
    km_high.fit(
        test_time[is_high_risk] / 365.25,
        test_event[is_high_risk],
        label=f"Alto Risco (n={is_high_risk.sum()})",
    )
    km_high.plot_survival_function(ax=ax, color="#d9534f", lw=2, ci_alpha=0.15)

    km_low = KaplanMeierFitter()
    km_low.fit(
        test_time[~is_high_risk] / 365.25,
        test_event[~is_high_risk],
        label=f"Baixo Risco (n={(~is_high_risk).sum()})",
    )
    km_low.plot_survival_function(ax=ax, color="#0275d8", lw=2, ci_alpha=0.15)

    p_val_text = f"p < 0.0001" if lr_res.p_value < 0.0001 else f"p = {lr_res.p_value:.4f}"
    ax.set_title(
        f"Estratificação de Risco no Conjunto de Teste — {model_name}\nLog-Rank: {p_val_text}",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax.set_xlabel("Tempo desde o Diagnóstico (Anos)", fontsize=11)
    ax.set_ylabel("Probabilidade de Sobrevida Global S(t)", fontsize=11)
    ax.set_ylim(0, 1.05)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="lower left", frameon=True, fontsize=10)

    plt.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)

    return {
        "ponto_de_corte_treino": cutoff_threshold,
        "n_alto_risco": int(is_high_risk.sum()),
        "n_baixo_risco": int((~is_high_risk).sum()),
        "logrank_stat": float(lr_res.test_statistic),
        "p_valor": float(lr_res.p_value),
        "figura_salva": str(output_path.as_posix()),
    }

