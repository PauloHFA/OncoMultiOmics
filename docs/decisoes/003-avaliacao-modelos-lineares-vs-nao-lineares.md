# ADR 003: Avaliação Comparativa de Modelos Lineares Penalizados vs. Ensembles Não-Lineares (Q2, H2)

## Contexto
A literatura de Machine Learning frequentemente propõe o uso de algoritmos de árvores não-lineares (Random Survival Forest, Gradient Boosting Survival) ou redes neurais (DeepSurv) sob a premissa de capturar interações complexas entre genes. O documento metodológico definiu como hipótese testável $H_2$:
> "Modelos lineares penalizados (Cox elastic net) têm desempenho comparável ou superior a modelos mais complexos nas dimensões de amostra do TCGA."

## Decisão
Implementamos e comparamos em 25 dobras estratificadas repetidas (5×5):
1. **$M_1$ (Cox Clínico Baseline)**
2. **$M_3$ (Cox Elastic Net Integrado)**
3. **$M_5$ (Random Survival Forest)**
4. **$M_6$ (Gradient Boosting Survival)**

Todas as seleções e transformações foram estritamente isoladas intra-fold (REG-03), e a avaliação utilizou C-index de Uno com horizonte $\tau=5\text{ anos}$ e Integrated Brier Score (REG-05).

## Resultados Observados
- **$M_3$ (Cox Elastic Net)** obteve a melhor discriminação ($C_{\text{Uno}} = 0,6366$) e a melhor calibração ($\text{IBS} = 0,1721$).
- **$M_6$ (Gradient Boosting)** atingiu $C_{\text{Uno}} = 0,6272$ e $\text{IBS} = 0,1758$.
- **$M_5$ (Random Survival Forest)** atingiu $C_{\text{Uno}} = 0,5958$ e $\text{IBS} = 0,1796$.

## Consequências e Veredito
- **Hipótese $H_2$ CONFIRMADA**: Na escala amostral do TCGA ($N \approx 500$ pacientes), métodos lineares com penalização Elastic Net ($\ell_1 / \ell_2$) superam ensembles não-lineares. Modelos de árvore sofrem com alta variância e penalidade de esparsidade no regime $p \gg n$, enquanto a regularização linear penalizada preserva parcimônia, calibração probabilística e interpretabilidade direta dos coeficientes por gene.

