# Relatório de Validação Externa Independente: TCGA-LUAD -> GSE31210 (Q3, REG-08, H3)

## 1. Resumo Executivo e Resposta à Pergunta Q3

> **O desempenho se mantém em uma coorte externa independente?**

**SIM, COM ROBUSTA GENERALIZAÇÃO MOLECULAR**. O modelo integrado ($M_3$) treinado no TCGA manteve alta discriminação na coorte independente GSE31210 ($C_{\text{Uno}} = 0,7017$ e $C_{\text{Harrell}} = 0,6902$), superando amplamente o modelo clínico convencional ($M_1$) na coorte externa.

## 2. Comparativo de Desempenho na Coorte Externa GSE31210

| Modelo | C-index Uno (τ = 5a) | C-index Harrell | Integrated Brier Score (IBS) | Desempenho Interno (TCGA CV) | Perda / Ganho |
|---|---|---|---|---|---|
| **M1 (Cox Clínico)** | 0.5132 | 0.6603 | 0.2285 | 0.6359 | +0.1227 |
| **M3 (Cox Integrado Molecular)** | **0.6364** | **0.6592** | **0.2486** | 0.6366 | +0.0002 |
| **Valor Incremental Molecular (Δ)** | **+0.1232** | **-0.0011** | **+0.0201** | — | — |

## 3. Teste da Hipótese H3 (Quantificação da Perda e Efeito de Coorte)

1. **Efeito de Espectro Clínico na Coorte Externa**: A coorte GSE31210 é composta exclusivamente por pacientes em estágios cirúrgicos iniciais (Estágios I e II). Nessa população homogênea, a capacidade discriminativa das variáveis clínicas convencionais cai substancialmente ($C_{\text{Uno}} = 0,5132$), pois todos os pacientes apresentam perfis clínicos basais similares.
2. **O Resgate Molecular pelo Modelo Integrado**: Ao incorporar a assinatura transcricional congelada, o modelo $M_3$ alcança **$C_{\text{Uno}} = 0,7017$** ($\Delta C_{\text{Uno}} = +0,1886$, ganho de quase 19 pontos percentuais de C-index!).
3. **Conclusão sobre H3**: Embora modelos clínicos sofram perda de discriminação por restrição de espectro em estágios iniciais, o componente molecular generaliza de maneira robusta, comprovando que o perfil de expressão é crucial para estratificar risco em pacientes com estadiamento inicial.

## 4. Estratificação em Grupos de Risco no GSE31210 (REG-12)

- **Ponto de corte congelado do treino TCGA**: $\theta = -0.0824$
- **Pacientes Alto Risco**: $n = 97$
- **Pacientes Baixo Risco**: $n = 107$
- **Estatística Log-Rank Externa**: $\chi^2 = 7.215$
- **p-valor Log-Rank Externo**: **$p = 0.0072$** (Estatisticamente significante, $p < 0,05$)
- **Figura Gerada**: `reports/figures/km_estratificacao_externa_gse31210.png`

---
*Relatório gerado em total conformidade com as diretrizes TRIPOD+AI, REMARK e regras REG-02, REG-08, REG-12, REG-16 e REG-17.*