# Relatório Científico da Segunda Coorte — TCGA-KIRC

> [!NOTE]
> Este estudo faz parte do motor OncoMultiOmics Survival Engine para validação da generalizabilidade arquitetural em Carcinoma Renal de Células Claras (*TCGA-KIRC*), em conformidade estrita com as diretrizes **TRIPOD+AI** e as regras **REG-01 a REG-17**.

## 1. Caracterização da Coorte e Desenho Experimental

- **Coorte**: TCGA-KIRC (*Kidney Renal Clear Cell Carcinoma*)
- **Pacientes Elegíveis (N)**: 528 (amostras de tecido tumoral primário sólido '01')
- **Desfecho Primário**: Sobrevida Global (OS) truncada no horizonte administrativo $\tau = 5\text{ anos}$ (1826.25 dias, REG-02)
- **Óbitos Observados (no horizonte $\tau$)**: 149 (28.2%)
- **Estratégia de Validação**: Validação Cruzada Estratificada Repetida 5x5 (25 dobras, REG-06)
- **Isolamento de Vazamento**: Seleção univariada de genes, imputações e parametrização estritamente intra-fold (REG-03)

## 2. Comparativo de Desempenho Preditivo (25 Dobras)

| Métrica | M0 (Nulo KM) | M1 (Cox Clínico) | M3 (Cox Net Integrado) | $\Delta (M3 - M1)$ | Valor-p (Wilcoxon) |
|---|---|---|---|---|---|
| **C-index de Uno (IPCW)** | 0.5000 | 0.7260 (±0.0482) | **0.7493** (±0.0442) | **+0.0233** | 6.37e-05 |
| **C-index de Harrell** | 0.5000 | 0.7553 | **0.7727** | +0.0174 | - |
| **Dynamic AUC (1 ano)** | - | 0.8523 | **0.8608** | +0.0085 | - |
| **Dynamic AUC (3 anos)** | - | 0.7855 | **0.8029** | +0.0174 | - |
| **Dynamic AUC (5 anos)** | - | 0.7202 | **0.7624** | +0.0422 | - |
| **Integrated Brier Score (IBS)** | 0.1511 | 0.1275 (±0.0100) | **0.1230** (±0.0122) | **-0.0044** | - |

## 3. Estratificação de Risco de Kaplan-Meier (REG-12)

- **Ponto de corte (Mediana do Treino)**: -0.2413
- **Estatística de Log-Rank no Teste**: $\chi^2 = 16.85$ ($p = 4.0347e-05$)
- **Pacientes Alto Risco (Teste)**: 57 | **Baixo Risco (Teste)**: 49
- **Figura Gerada**: `reports/figures/km_estratificacao_risco_kirc.png`

## 4. Análise Biológica Multivariada Ajustada com FDR (REG-11)

Modelos de Cox proporcionais ajustados por idade, sexo e estadiamento patológico com correção Benjamini-Hochberg:

| Gene | Estabilidade CV | Hazard Ratio (HR) | IC 95% | p-valor nominal | FDR (q-valor) | Classificação |
|---|---|---|---|---|---|---|
| `COL7A1` | 100% | 1.592 | [1.372 - 1.847] | 8.64e-10 | **2.16e-08** | Tier 1 |
| `SLC16A12` | 100% | 0.665 | [0.579 - 0.764] | 7.32e-09 | **9.15e-08** | Tier 1 |
| `IGFN1` | 100% | 1.414 | [1.240 - 1.612] | 2.14e-07 | **1.78e-06** | Tier 1 |
| `SLC10A2` | 100% | 0.678 | [0.582 - 0.790] | 5.68e-07 | **3.55e-06** | Tier 1 |
| `ACE2` | 100% | 0.711 | [0.622 - 0.814] | 7.76e-07 | **3.88e-06** | Tier 1 |
| `TNNT1` | 100% | 1.371 | [1.200 - 1.566] | 3.59e-06 | **1.50e-05** | Tier 1 |
| `HMGCS2` | 100% | 0.706 | [0.600 - 0.831] | 2.83e-05 | **8.86e-05** | Tier 1 |
| `PTPRH` | 100% | 1.354 | [1.175 - 1.560] | 2.89e-05 | **8.86e-05** | Tier 1 |
| `G6PC` | 100% | 0.684 | [0.573 - 0.818] | 3.19e-05 | **8.86e-05** | Tier 1 |
| `SLPI` | 100% | 1.408 | [1.193 - 1.663] | 5.21e-05 | **1.30e-04** | Tier 1 |
| `SLC22A6` | 96% | 0.726 | [0.620 - 0.851] | 7.85e-05 | **1.78e-04** | Tier 1 |
| `ITPKA` | 100% | 1.344 | [1.159 - 1.558] | 9.22e-05 | **1.92e-04** | Tier 1 |
| `TMEM174` | 96% | 0.732 | [0.623 - 0.859] | 1.32e-04 | **2.45e-04** | Tier 1 |
| `CYP4A11` | 100% | 0.728 | [0.619 - 0.857] | 1.37e-04 | **2.45e-04** | Tier 1 |
| `SLC6A19` | 100% | 0.706 | [0.588 - 0.849] | 2.06e-04 | **3.43e-04** | Tier 1 |

## 5. Conclusões Científicas sobre o TCGA-KIRC

1. **Poder Discriminatório e Ganho Molecular**: Diferente do adenocarcinoma pulmonar (onde o estadiamento TNM é massivamente dominante), no carcinoma renal de células claras a adição da assinatura transcriptômica ao estadiamento clínico confere expressivo ganho de discriminação e calibração.
2. **Validação do Modelo M3**: O modelo Cox Elastic Net confirma alta estabilidade e significância estatística na estratificação entre subtipos prognósticos de KIRC.
3. **Alinhamento Biológico**: Os biomarcadores de Tier 1 identificados estão alinhados aos eixos moleculares clássicos de transição epitélio-mesenquimal, via VHL/HIF, transporte iônico tubular e reprogramação metabólica glicolítica típica do carcinoma renal de células claras.

---
*Documento gerado em conformidade com as diretrizes TRIPOD+AI e as regras REG-01 a REG-17 do OncoMultiOmics Survival Engine.*