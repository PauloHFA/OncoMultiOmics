"""Módulo de Modelos Baselines (Fase 3): M0 (Kaplan-Meier Nulo) e M1 (Cox Clínico).

Implementa:
- M0: Referência empírica não-paramétrica sem preditores (C-index = 0.50).
- M1: Modelo de regressão de Cox proporcional utilizando exclusivamente variáveis clínicas basais (idade, sexo, estágio AJCC).
- Isolamento estrito de vazamento (REG-03) via pré-processador ajustado somente nos dados de treino.
"""
from typing import List
import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter
from sklearn.base import BaseEstimator
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sksurv.linear_model import CoxPHSurvivalAnalysis


class NullKaplanMeierModel:
    """Modelo Nulo M0 baseado puramente na curva marginal de Kaplan-Meier (sem preditores)."""

    def __init__(self):
        self.kmf = KaplanMeierFitter()

    def fit(self, y: np.ndarray) -> "NullKaplanMeierModel":
        self.kmf.fit(y["time"], y["event"])
        return self

    def predict_risk(self, n_samples: int) -> np.ndarray:
        """Retorna risco constante (0.0) para todas as amostras (C-index = 0.50)."""
        return np.zeros(n_samples, dtype=float)

    def predict_survival_probabilities(self, times: np.ndarray, n_samples: int) -> np.ndarray:
        """Retorna a probabilidade S(t) de Kaplan-Meier repetida para todas as amostras."""
        surv_t = np.array([self.kmf.survival_function_at_times(t).values[0] for t in times])
        return np.tile(surv_t, (n_samples, 1))


class ClinicalCoxModel(BaseEstimator):
    """Modelo M1: Cox Proportional Hazards clínico (Idade, Sexo, Estágio AJCC)."""

    def __init__(self, alpha: float = 0.0):
        self.alpha = alpha
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = StandardScaler()
        self.cox = CoxPHSurvivalAnalysis(alpha=alpha)
        self.feature_names_: List[str] = []

    def fit(self, X: pd.DataFrame, y: np.ndarray) -> "ClinicalCoxModel":
        self.feature_names_ = list(X.columns)
        X_imp = self.imputer.fit_transform(X)
        X_scaled = self.scaler.fit_transform(X_imp)
        self.cox.fit(X_scaled, y)
        return self

    def predict_risk(self, X: pd.DataFrame) -> np.ndarray:
        """Estima o escore de risco log-hazard (beta * X). Quanto maior, maior o risco."""
        X_imp = self.imputer.transform(X)
        X_scaled = self.scaler.transform(X_imp)
        return self.cox.predict(X_scaled)

    def predict_survival_probabilities(self, X: pd.DataFrame, times: np.ndarray) -> np.ndarray:
        """Estima a probabilidade de sobrevivência S(t|x) nos instantes de tempo especificados."""
        X_imp = self.imputer.transform(X)
        X_scaled = self.scaler.transform(X_imp)
        surv_fns = self.cox.predict_survival_function(X_scaled)
        grid = np.vstack([[fn(t) for t in times] for fn in surv_fns])
        return grid

