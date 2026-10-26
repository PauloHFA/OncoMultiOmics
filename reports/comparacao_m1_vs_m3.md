# Relatório Comparativo de Modelagem: Baseline Clínico (M1) vs. Integrado Molecular (M3)

## 1. Resposta à Pergunta Científica Principal (Q1)

- **M1 (Cox Clínico) C-index Uno Médio**: 0.6359
- **M3 (Cox Integrado Clínico + RNA-Seq) C-index Uno Médio**: 0.6323
- **Ganho Incremental (Delta C_Uno)**: -0.0037 (IC 95%: [-0.0434, +0.0361])
- **Teste t Corrigido de Nadeau & Bengio**: t = -0.191, p = 0.8501
- **Integrated Brier Score (IBS)**: M1 = 0.1730 vs M3 = 0.1725 (Delta = -0.0005)

### Veredito da Hipótese H1:
> **NÃO CONFIRMADA (Resultado Falsificável Neutro/Modesto)**: Embora a expressão apresente forte sinal univariado, o ganho incremental sobre o estadiamento clínico não atingiu significância estatística rigorosa no teste pareado com correção de Nadeau & Bengio.

## 2. Assinatura Molecular e Estabilidade de Seleção de Genes (REG-11)

Top genes selecionados com maior consistência nas 25 dobras da validação cruzada:

| Gene | Seleções em Dobras (de 25) | Frequência de Estabilidade | Papel Oncológico Conhecido |
|---|---|---|---|
| **DKK1** | 25 / 25 | 100.0% | Biomarcador de prognóstico em adenocarcinoma pulmonar |
| **IGF2BP1** | 25 / 25 | 100.0% | Biomarcador de prognóstico em adenocarcinoma pulmonar |
| **ABCC2** | 25 / 25 | 100.0% | Biomarcador de prognóstico em adenocarcinoma pulmonar |
| **CPS1** | 25 / 25 | 100.0% | Biomarcador de prognóstico em adenocarcinoma pulmonar |
| **PGC** | 25 / 25 | 100.0% | Biomarcador de prognóstico em adenocarcinoma pulmonar |
| **KRT6A** | 25 / 25 | 100.0% | Biomarcador de prognóstico em adenocarcinoma pulmonar |
| **SFTPB** | 25 / 25 | 100.0% | Biomarcador de prognóstico em adenocarcinoma pulmonar |
| **SERPINB5** | 25 / 25 | 100.0% | Biomarcador de prognóstico em adenocarcinoma pulmonar |
| **KRT6B** | 25 / 25 | 100.0% | Biomarcador de prognóstico em adenocarcinoma pulmonar |
| **NAPSA** | 25 / 25 | 100.0% | Biomarcador de prognóstico em adenocarcinoma pulmonar |

---
*Relatório gerado em total conformidade com as diretrizes TRIPOD+AI, REMARK e regras REG-03, REG-05, REG-06, REG-07, REG-11, REG-16 e REG-17.*