"""Módulo de Seleção de Variáveis Moleculares Intra-Fold (E2).

Implementa:
- REG-03: Ajustado estritamente dentro da dobra de treino.
- Teste de escore de Cox / Log-rank vetorizado ultrarrápido para ranqueamento de genes prognósticos.
"""
from typing import List, Tuple
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class FastCoxScoreSelector(BaseEstimator, TransformerMixin):
    """Selecionador univariado de genes baseado na estatística de escore de Cox (Score Test).

    Calcula a estatística de log-rank univariada de forma vetorizada, garantindo
    velocidade e estrita conformidade anti-vazamento (ajustado apenas no treino).
    """

    def __init__(self, top_k: int = 100):
        self.top_k = top_k
        self.selected_genes_: List[str] = []
        self.scores_: np.ndarray | None = None

    def fit(self, X: pd.DataFrame, y: np.ndarray) -> "FastCoxScoreSelector":
        """Calcula as pontuações de escore de Cox para cada gene usando os dados de treino."""
        gene_names = np.array(X.columns)
        X_mat = X.values.astype(np.float64)
        time_arr = y["time"].astype(np.float64)
        event_arr = y["event"].astype(bool)

        # Ordenar amostras em ordem decrescente de tempo para cálculo do conjunto sob risco
        order = np.argsort(time_arr)[::-1]
        X_sorted = X_mat[order]
        event_sorted = event_arr[order]

        # Média ponderada do conjunto sob risco em cada instante de evento
        cum_sum = np.cumsum(X_sorted, axis=0)
        n_risk = np.arange(1, len(time_arr) + 1)[:, None]
        risk_means = cum_sum / n_risk

        # Estatística de escore univariada U = sum_i delta_i * (x_ij - mean_j(t_i))
        scores = np.abs(np.sum(event_sorted[:, None] * (X_sorted - risk_means), axis=0))
        self.scores_ = scores

        # Selecionar os top_k genes com maior estatística de escore
        k_eff = min(self.top_k, len(gene_names))
        top_indices = np.argsort(scores)[::-1][:k_eff]
        self.selected_genes_ = list(gene_names[top_indices])

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Filtra as colunas do DataFrame para os genes selecionados no treino."""
        return X[self.selected_genes_]

    def fit_transform(self, X: pd.DataFrame, y: np.ndarray) -> pd.DataFrame:
        return self.fit(X, y).transform(X)

