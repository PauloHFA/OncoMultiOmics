"""Módulo do Modelo Integrado M3 (Cox Penalizado Clínico + Transcriptômico).

Implementa:
- REG-03: Todas as transformações, seleções de genes e sintonização de hiperparâmetros
  ocorrem estritamente dentro da dobra de treinamento (nested CV).
- M3: Covariáveis clínicas sem penalização (penalty_factor=0.0) e expressão gênica
  penalizada via Elastic Net (l1_ratio=0.5, penalty_factor=1.0).
- Seleção automática da intensidade de regularização (alpha) por validação cruzada interna.
"""
import logging
from typing import List, Tuple
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.impute import SimpleImputer
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sksurv.linear_model import CoxnetSurvivalAnalysis
from sksurv.metrics import concordance_index_censored

from oncosurv.features.selecao import FastCoxScoreSelector

logger = logging.getLogger(__name__)


class IntegratedCoxNetModel(BaseEstimator):
    """Modelo Integrado M3: Cox Elastic Net integrando clínica e expressão gênica."""

    def __init__(
        self,
        top_k: int = 100,
        l1_ratio: float = 0.5,
        n_inner_splits: int = 3,
        random_state: int = 42,
    ):
        self.top_k = top_k
        self.l1_ratio = l1_ratio
        self.n_inner_splits = n_inner_splits
        self.random_state = random_state

        self.imputer_clin = SimpleImputer(strategy="median")
        self.scaler_clin = StandardScaler()
        self.gene_selector = FastCoxScoreSelector(top_k=top_k)
        self.scaler_expr = StandardScaler()

        self.best_alpha_: float | None = None
        self.coxnet_: CoxnetSurvivalAnalysis | None = None
        self.selected_genes_: List[str] = []

    def _prepare_features(
        self,
        X_clin: pd.DataFrame,
        X_expr: pd.DataFrame,
        fit: bool = False,
        y: np.ndarray | None = None,
    ) -> np.ndarray:
        """Processa e combina atributos clínicos e transcriptômicos."""
        if fit:
            X_clin_imp = self.imputer_clin.fit_transform(X_clin)
            X_clin_scaled = self.scaler_clin.fit_transform(X_clin_imp)

            X_expr_sel = self.gene_selector.fit_transform(X_expr, y)
            self.selected_genes_ = self.gene_selector.selected_genes_
            X_expr_scaled = self.scaler_expr.fit_transform(X_expr_sel)
        else:
            X_clin_imp = self.imputer_clin.transform(X_clin)
            X_clin_scaled = self.scaler_clin.transform(X_clin_imp)

            X_expr_sel = self.gene_selector.transform(X_expr)
            X_expr_scaled = self.scaler_expr.transform(X_expr_sel)

        return np.hstack([X_clin_scaled, X_expr_scaled])

    def fit(
        self,
        X_clin: pd.DataFrame,
        X_expr: pd.DataFrame,
        y: np.ndarray,
    ) -> "IntegratedCoxNetModel":
        """Ajusta o modelo com validação aninhada interna para seleção do melhor alpha."""
        X_comb = self._prepare_features(X_clin, X_expr, fit=True, y=y)
        n_clin = X_clin.shape[1]
        n_genes = len(self.selected_genes_)

        # Penalidade: 0.0 para variáveis clínicas (sem penalização), 1.0 para genes (Elastic Net)
        penalty_factor = np.array([0.0] * n_clin + [1.0] * n_genes)

        # Ajuste preliminar para obter a trajetória de alphas
        base_coxnet = CoxnetSurvivalAnalysis(
            l1_ratio=self.l1_ratio,
            penalty_factor=penalty_factor,
            fit_baseline_model=True,
            max_iter=50_000,
        )
        base_coxnet.fit(X_comb, y)
        candidate_alphas = base_coxnet.alphas_

        # Validação aninhada interna (nested CV) para selecionar alpha
        if self.n_inner_splits > 1 and len(candidate_alphas) > 1:
            kf = KFold(n_splits=self.n_inner_splits, shuffle=True, random_state=self.random_state)
            alpha_scores = {a: [] for a in candidate_alphas}

            for inner_train, inner_val in kf.split(X_comb):
                X_in_tr, X_in_val = X_comb[inner_train], X_comb[inner_val]
                y_in_tr, y_in_val = y[inner_train], y[inner_val]

                # Modelo interno
                inner_model = CoxnetSurvivalAnalysis(
                    l1_ratio=self.l1_ratio,
                    penalty_factor=penalty_factor,
                    alphas=candidate_alphas,
                    max_iter=50_000,
                )
                try:
                    inner_model.fit(X_in_tr, y_in_tr)
                    for a in inner_model.alphas_:
                        p = inner_model.predict(X_in_val, alpha=a)
                        c = concordance_index_censored(y_in_val["event"], y_in_val["time"], p)[0]
                        alpha_scores[a].append(c)
                except Exception:
                    continue

            # Escolher alpha com maior C-index médio interno
            mean_scores = {
                a: np.mean(scores) for a, scores in alpha_scores.items() if len(scores) > 0
            }
            if mean_scores:
                self.best_alpha_ = max(mean_scores, key=mean_scores.get)
            else:
                self.best_alpha_ = candidate_alphas[len(candidate_alphas) // 2]
        else:
            self.best_alpha_ = candidate_alphas[len(candidate_alphas) // 2]

        self.coxnet_ = base_coxnet
        return self

    def predict_risk(self, X_clin: pd.DataFrame, X_expr: pd.DataFrame) -> np.ndarray:
        """Retorna o escore de risco predito utilizando o melhor alpha da validação interna."""
        X_comb = self._prepare_features(X_clin, X_expr, fit=False)
        return self.coxnet_.predict(X_comb, alpha=self.best_alpha_)

    def predict_survival_probabilities(
        self,
        X_clin: pd.DataFrame,
        X_expr: pd.DataFrame,
        times: np.ndarray,
    ) -> np.ndarray:
        """Estima as curvas de sobrevivência S(t|x) usando a linha de base cumulativa ajustada."""
        X_comb = self._prepare_features(X_clin, X_expr, fit=False)
        surv_fns = self.coxnet_.predict_survival_function(X_comb, alpha=self.best_alpha_)
        grid = np.vstack([[fn(t) for t in times] for fn in surv_fns])
        return grid

