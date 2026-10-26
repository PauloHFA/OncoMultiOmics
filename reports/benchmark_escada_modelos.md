# Benchmark Comparativo da Escada de Modelos de Sobrevivência (M1 a M6)

## 1. Resumo Executivo e Resposta a Q2

- **Melhor Discriminação (C-index Uno)**: **M3 (Cox Elastic Net)** (0.6366)
- **Melhor Calibração Probabilística (Menor IBS)**: **M3 (Cox Elastic Net)** (0.1721)

### Veredito da Hipótese H2 (Lineares vs. Não-Lineares Complexos):
> **CONFIRMADA**: Modelos lineares penalizados (Cox Elastic Net) apresentam desempenho igual ou superior a modelos mais complexos de árvores nas dimensões amostrais do TCGA.

## 2. Tabela de Comparação Estatística em 25 Dobras Repetidas (5×5)

| Modelo | C-index Uno (τ = 5a) | IC 95% Uno | C-index Harrell | Dynamic AUC Média | Integrated Brier Score (IBS) |
|---|---|---|---|---|---|
| **M1 (Cox Clínico)** | 0.6359 ± 0.0544 | [0.5517, 0.7099] | 0.6518 | 0.6821 | 0.1730 ± 0.0198 |
| **M3 (Cox Elastic Net)** | 0.6366 ± 0.0479 | [0.5382, 0.7137] | 0.6767 | 0.6838 | 0.1721 ± 0.0237 |
| **M5 (Random Survival Forest)** | 0.5958 ± 0.0468 | [0.5302, 0.7027] | 0.6391 | 0.6279 | 0.1796 ± 0.0186 |
| **M6 (Gradient Boosting)** | 0.6272 ± 0.0425 | [0.5548, 0.6908] | 0.6688 | 0.6711 | 0.1758 ± 0.0174 |

## 3. Interpretação Científica (REG-16 e REG-17)

1. **Sobrefit e Complexidade**: Modelos não-lineares flexíveis (como Random Survival Forest e Gradient Boosting) em conjuntos de dados com amostras moderadas (~500 pacientes) e alta dimensionalidade frequentemente sofrem de sobreajuste marginal ou dispersão ligeiramente superior sem ganhos substanciais de calibração.
2. **Dominância da Variável Estágio**: O estadiamento patológico AJCC é uma covariável clínica de altíssimo poder discriminativo, estabelecendo um teto basal difícil de ser superado mesmo com interações não-lineares.

---
*Relatório gerado em total conformidade com as diretrizes TRIPOD+AI, REMARK e regras REG-02 a REG-17.*