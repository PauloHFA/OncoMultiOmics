"""Módulo de Modelos Não-Lineares de Sobrevivência (M5: RSF e M6: Gradient Boosting).

Implementa:
- M5: Random Survival Forest (Ishwaran et al., 2008). Captura interações e não-linearidades complexas.
- M6: Gradient Boosting Survival Analysis. Ensemble sequencial de árvores com regularização e subsampling.
- Isolamento estrito anti-vazamento (REG-03) via transformadores e seleção de genes ajustados somente no treino.
"""
import logging
from typing import List, Literal
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sksurv.ensemble import RandomSurvivalForest, GradientBoostingSurvivalAnalysis

from oncosurv.features.selecao import FastCoxScoreSelector

logger = logging.getLogger(__name__)


class RSFSurvivalModel(BaseEstimator):
    """Modelo M5: Random Survival Forest integrando clínica e expressão gênica."""

    def __init__(
        self,
        top_k: int = 50,
        n_estimators: int = 100,
        min_samples_leaf: int = 15,
        max_features: Literal["sqrt", "log2"] | float = "sqrt",
        random_state: int = 42,
        n_jobs: int = -1,
    ):
        self.top_k = top_k
        self.n_estimators = n_estimators
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.random_state = random_state
        self.n_jobs = n_jobs

        self.imputer_clin = SimpleImputer(strategy="median")
        self.scaler_clin = StandardScaler()
        self.gene_selector = FastCoxScoreSelector(top_k=top_k)
        self.scaler_expr = StandardScaler()

        self.rsf_: RandomSurvivalForest | None = None
        self.selected_genes_: List[str] = []

    def _prepare_features(
        self,
        X_clin: pd.DataFrame,
        X_expr: pd.DataFrame,
        fit: bool = False,
        y: np.ndarray | None = None,
    ) -> np.ndarray:
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
    ) -> "RSFSurvivalModel":
        X_comb = self._prepare_features(X_clin, X_expr, fit=True, y=y)
        self.rsf_ = RandomSurvivalForest(
            n_estimators=self.n_estimators,
            min_samples_leaf=self.min_samples_leaf,
            max_features=self.max_features,
            random_state=self.random_state,
            n_jobs=self.n_jobs,
        )
        self.rsf_.fit(X_comb, y)
        return self

    def predict_risk(self, X_clin: pd.DataFrame, X_expr: pd.DataFrame) -> np.ndarray:
        """Estima o escore de risco cumulativo acumulado (maior valor = pior sobrevida)."""
        X_comb = self._prepare_features(X_clin, X_expr, fit=False)
        return self.rsf_.predict(X_comb)

    def predict_survival_probabilities(
        self,
        X_clin: pd.DataFrame,
        X_expr: pd.DataFrame,
        times: np.ndarray,
    ) -> np.ndarray:
        """Prediz a probabilidade S(t|x) usando a função de sobrevivência estimada pelo ensemble."""
        X_comb = self._prepare_features(X_clin, X_expr, fit=False)
        surv_fns = self.rsf_.predict_survival_function(X_comb)
        grid = np.vstack([[fn(t) for t in times] for fn in surv_fns])
        return grid


class GradientBoostingSurvivalModel(BaseEstimator):
    """Modelo M6: Gradient Boosting Survival integrando clínica e expressão gênica."""

    def __init__(
        self,
        top_k: int = 50,
        n_estimators: int = 100,
        learning_rate: float = 0.03,
        max_depth: int = 3,
        subsample: float = 0.8,
        random_state: int = 42,
    ):
        self.top_k = top_k
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.subsample = subsample
        self.random_state = random_state

        self.imputer_clin = SimpleImputer(strategy="median")
        self.scaler_clin = StandardScaler()
        self.gene_selector = FastCoxScoreSelector(top_k=top_k)
        self.scaler_expr = StandardScaler()

        self.gb_: GradientBoostingSurvivalAnalysis | None = None
        self.selected_genes_: List[str] = []

    def _prepare_features(
        self,
        X_clin: pd.DataFrame,
        X_expr: pd.DataFrame,
        fit: bool = False,
        y: np.ndarray | None = None,
    ) -> np.ndarray:
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
    ) -> "GradientBoostingSurvivalModel":
        X_comb = self._prepare_features(X_clin, X_expr, fit=True, y=y)
        self.gb_ = GradientBoostingSurvivalAnalysis(
            n_estimators=self.n_estimators,
            learning_rate=self.learning_rate,
            max_depth=self.max_depth,
            subsample=self.subsample,
            random_state=self.random_state,
        )
        self.gb_.fit(X_comb, y)
        return self

    def predict_risk(self, X_clin: pd.DataFrame, X_expr: pd.DataFrame) -> np.ndarray:
        X_comb = self._prepare_features(X_clin, X_expr, fit=False)
        return self.gb_.predict(X_comb)

    def predict_survival_probabilities(
        self,
        X_clin: pd.DataFrame,
        X_expr: pd.DataFrame,
        times: np.ndarray,
    ) -> np.ndarray:
        X_comb = self._prepare_features(X_clin, X_expr, fit=False)
        surv_fns = self.gb_.predict_survival_function(X_comb)
        grid = np.vstack([[fn(t) for t in times] for fn in surv_fns])
        return grid

