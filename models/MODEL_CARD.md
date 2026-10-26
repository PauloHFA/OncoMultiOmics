# Model Card — OncoMultiOmics Survival Engine — M3 Cox Elastic Net Integrado (v1.0.0)

## 1. Visão Geral do Modelo
- **Data de Liberação**: 2026-10-26
- **Tipo de Algoritmo**: Regularized Cox Proportional Hazards Model (Elastic Net: L1=0.5)
- **Bibliotecas Centrais**: `scikit-survival` v0.28.0 e `scikit-learn` v1.9.1
- **Licença de Uso**: MIT (Open Source for Research)

## 2. Uso Pretendido e Escopo (REG-16)
- **Aplicação Principal**: Estratificação e predição de risco prognóstico em adenocarcinoma de pulmão (LUAD) para pesquisa translacional e biomédica.
- **Limitações e Fora de Escopo**: Uso como dispositivo médico de diagnóstico clínico ou direcionamento terapêutico individualizado sem aprovação de agências regulatórias (ANVISA/FDA).

## 3. Dados de Treinamento e Curadoria (REG-01, REG-02)
- **Coorte de Treino**: TCGA-LUAD (The Cancer Genome Atlas - Lung Adenocarcinoma)
- **Pacientes Elegíveis**: 494
- **Desfecho**: Sobrevida Global (OS) com horizonte administrativo tau=5 anos (1826.25 dias)
- **Óbitos Observados**: 170 (34.4%)

## 4. Desempenho e Validação Independente (REG-05, REG-08)
- **Validação Cruzada Interna 5×5 (25 dobras)**:
  - C-index de Uno (τ = 5a): **0.6366**
  - C-index de Harrell: 0.6767
  - Dynamic AUC Média: 0.6838
  - Integrated Brier Score (IBS): 0.1721
- **Validação Externa Independente (GSE31210 / Microarray Affymetrix)**:
  - Pacientes: 204
  - C-index de Uno (τ = 5a): **0.6364** (Perda de generalização: 0.0002)
  - Valor Incremental Molecular: **+0.1232 (+12.3%)**
  - Separação Log-Rank: **p = 0.0072**

## 5. Variáveis de Entrada e Coeficientes Ativos

| Atributo | Coeficiente Log-Hazard (β) | Hazard Ratio (HR) |
|---|---|---|
| **idade** | +0.0829 | 1.086 |
| **is_female** | +0.0310 | 1.031 |
| **estagio_ord** | +0.4812 | 1.618 |
| **DKK1** | +0.2051 | 1.228 |
| **IGF2BP1** | +0.0755 | 1.078 |
| **SFTPC** | -0.0099 | 0.990 |
| **SERPINB5** | +0.0014 | 1.001 |
| **SFTPB** | -0.0940 | 0.910 |
| **TCN1** | +0.1387 | 1.149 |
| **CPS1** | +0.1158 | 1.123 |
| **KIAA0408** | -0.0184 | 0.982 |
| **SFTA3** | -0.0187 | 0.981 |

## 6. Como Carregar e Utilizar o Modelo Serializado
```python
import joblib
import pandas as pd

# Carregar modelo integrado treinado
model = joblib.load('models/m3_coxnet_integrado.joblib')

# Predizer escore de risco relativo
# risk = model.predict_risk(X_clin, X_expr)
```

---
*Model Card gerado em conformidade com as diretrizes internacionais de IA biomédica e TRIPOD+AI.*