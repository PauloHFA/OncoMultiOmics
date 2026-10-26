"""Teste automatizado anti-vazamento (REG-03).

Garante que nenhuma etapa de pré-processamento (imputação, padronização, seleção)
utiliza informações do conjunto de teste ou do desfecho do conjunto de teste.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from sksurv.util import Surv

from oncosurv.modelos.baselines import ClinicalCoxModel

CLINICAL_FILE = Path(__file__).resolve().parent.parent / "data" / "interim" / "luad_clinico_curado.parquet"


@pytest.fixture(scope="module")
def clinical_data():
    df = pd.read_parquet(CLINICAL_FILE)
    X = df[["idade", "is_female", "estagio_ord"]]
    y = Surv.from_arrays(event=df["OS_event"].astype(bool), time=df["OS_time"].astype(float))
    return X, y


def test_reg03_parametros_estatisticos_independentes_do_teste(clinical_data):
    """Verifica se as estatísticas de normalização e imputação são derivadas exclusivamente do treino."""
    X, y = clinical_data

    # Divisão artificial treino (80%) e teste (20%)
    n_train = int(len(X) * 0.8)
    X_train = X.iloc[:n_train].copy()
    y_train = y[:n_train]
    X_test = X.iloc[n_train:].copy()

    # Treinar modelo clínico M1
    model = ClinicalCoxModel().fit(X_train, y_train)

    # 1. Mediana aprendida no imputer deve ser igual à mediana exata de X_train
    expected_medians = X_train.median(axis=0).values
    actual_imputer_medians = model.imputer.statistics_
    np.testing.assert_allclose(
        actual_imputer_medians,
        expected_medians,
        rtol=1e-5,
        err_msg="Vazamento detectado: O imputer calculou estatísticas fora do conjunto de treino!",
    )

    # 2. Média e variância aprendidas no scaler devem ser iguais às de X_train (com imputação)
    X_train_imp = X_train.fillna(X_train.median())
    expected_means = X_train_imp.mean(axis=0).values
    actual_scaler_means = model.scaler.mean_
    np.testing.assert_allclose(
        actual_scaler_means,
        expected_means,
        rtol=1e-5,
        err_msg="Vazamento detectado: O padronizador aprendeu médias fora do conjunto de treino!",
    )


def test_reg03_invariancia_do_modelo_a_perturbacoes_no_teste(clinical_data):
    """Verifica que modificar dados de teste não altera em nada o modelo já ajustado."""
    X, y = clinical_data
    n_train = int(len(X) * 0.8)
    X_train = X.iloc[:n_train].copy()
    y_train = y[:n_train]
    X_test = X.iloc[n_train:].copy()

    model = ClinicalCoxModel().fit(X_train, y_train)
    coefs_original = model.cox.coef_.copy()

    # Perturbação extrema no conjunto de teste (valores fora de escala)
    X_test_perturbed = X_test.copy()
    X_test_perturbed["idade"] = 9999.0
    _ = model.predict_risk(X_test_perturbed)

    # Coeficientes do modelo não podem mudar
    np.testing.assert_array_equal(
        model.cox.coef_,
        coefs_original,
        err_msg="Vazamento grave: Predição no teste alterou parâmetros internos do modelo!",
    )

