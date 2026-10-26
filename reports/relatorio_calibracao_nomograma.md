# Relatório de Calibração Probabilística e Contribuição de Atributos (REG-05)

## 1. Avaliação de Calibração em Horizontes Temporais Chave

A calibração mede a concordância absoluta entre a probabilidade estimada pelo modelo e a taxa real de sobrevivência observada por Kaplan-Meier nos decis/quantis de risco.

| Horizonte | Inclinação de Calibração (Slope) | Intercepto | Erro Médio Absoluto (ICI) | Avaliação |
|---|---|---|---|---|
| **1 ano** | 0.99 | +0.039 | 0.028 | Boa Calibração (Slope próximo a 1.0) |
| **3 anos** | 0.82 | +0.113 | 0.044 | Boa Calibração (Slope próximo a 1.0) |
| **5 anos** | 0.87 | -0.029 | 0.163 | Boa Calibração (Slope próximo a 1.0) |

### Figura de Calibração:
- Painel multi-horizontes salvo em: `reports/figures/calibracao_multi_horizontes_m3.png`.

## 2. Contribuição dos Atributos Clínicos e Moleculares no Modelo M3

O modelo Elastic Net integrou variáveis clínicas e selecionou os biomarcadores com coeficientes não-nulos:

| Atributo | Categoria | Coeficiente Log-Hazard (β) | Hazard Ratio (HR) | Efeito Prognóstico |
|---|---|---|---|---|
| **Estágio AJCC (I a IV)** | Clínico | +0.4494 | 1.567 | Aumento de Risco |
| **DKK1** | Transcriptômico | +0.1676 | 1.182 | Aumento de Risco |
| **TCN1** | Transcriptômico | +0.1290 | 1.138 | Aumento de Risco |
| **CPS1** | Transcriptômico | +0.0901 | 1.094 | Aumento de Risco |
| **IGF2BP1** | Transcriptômico | +0.0812 | 1.085 | Aumento de Risco |
| **ANXA10** | Transcriptômico | +0.0655 | 1.068 | Aumento de Risco |
| **IGFBP1** | Transcriptômico | +0.0463 | 1.047 | Aumento de Risco |
| **Idade ao Diagnóstico** | Clínico | +0.0335 | 1.034 | Aumento de Risco |
| **KRT6C** | Transcriptômico | +0.0210 | 1.021 | Aumento de Risco |
| **Sexo (Feminino)** | Clínico | -0.0234 | 0.977 | Redução de Risco / Protetor |
| **KIAA0408** | Transcriptômico | -0.0443 | 0.957 | Redução de Risco / Protetor |
| **SFTPB** | Transcriptômico | -0.0746 | 0.928 | Redução de Risco / Protetor |
| **SLC14A2** | Transcriptômico | -0.1079 | 0.898 | Redução de Risco / Protetor |

### Figura do Nomograma / Pesos:
- Gráfico de barras horizontais salvo em: `reports/figures/nomograma_pesos_m3.png`.

---
*Documento gerado em conformidade com as diretrizes TRIPOD+AI e regras REG-05 e REG-16.*