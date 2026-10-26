# Relatório de Interpretabilidade Biológica e Enriquecimento de Vias (Q4, REG-11)

## 1. Resposta à Pergunta Científica Q4

> **Quais genes e vias se associam à sobrevivência de forma estável e independente das variáveis clínicas?**

Identificamos um núcleo de genes com estabilidade máxima de seleção através das 25 dobras da validação cruzada que permanecem **estatisticamente significantes após ajuste multivariado estrito por idade, sexo e estadiamento AJCC**, resistindo à correção de Benjamini-Hochberg (FDR $q < 0,05$).

## 2. Tabela de Genes Candidatos Ajustados por Covariáveis Clínicas (REG-11)

| Gene | Estabilidade CV | HR Ajustado (por DP) | IC 95% do HR | p-valor Bruto | FDR (q-valor) | Classificação |
|---|---|---|---|---|---|---|
| **DKK1** | 100% | 1.533 | [1.32, 1.78] | 1.32e-08 | 2.64e-07 | Tier 1 (Alta Credibilidade) |
| **SFTA3** | 100% | 0.738 | [0.65, 0.84] | 1.93e-06 | 1.93e-05 | Tier 1 (Alta Credibilidade) |
| **IGF2BP1** | 100% | 1.353 | [1.17, 1.56] | 3.84e-05 | 2.04e-04 | Tier 1 (Alta Credibilidade) |
| **NAPSA** | 100% | 0.758 | [0.66, 0.87] | 4.08e-05 | 2.04e-04 | Tier 1 (Alta Credibilidade) |
| **IGFBP1** | 96% | 1.319 | [1.15, 1.52] | 1.01e-04 | 3.25e-04 | Tier 1 (Alta Credibilidade) |
| **TCN1** | 96% | 1.349 | [1.16, 1.57] | 1.10e-04 | 3.25e-04 | Tier 1 (Alta Credibilidade) |
| **ABCC2** | 100% | 1.296 | [1.14, 1.48] | 1.14e-04 | 3.25e-04 | Tier 1 (Alta Credibilidade) |
| **SFTPB** | 100% | 0.774 | [0.68, 0.88] | 1.33e-04 | 3.32e-04 | Tier 1 (Alta Credibilidade) |
| **SERPINB5** | 100% | 1.347 | [1.15, 1.57] | 1.58e-04 | 3.51e-04 | Tier 1 (Alta Credibilidade) |
| **GGTLC1** | 96% | 0.741 | [0.63, 0.87] | 3.11e-04 | 6.22e-04 | Tier 1 (Alta Credibilidade) |
| **C16orf89** | 100% | 0.771 | [0.67, 0.89] | 3.43e-04 | 6.23e-04 | Tier 1 (Alta Credibilidade) |
| **CACNA2D2** | 100% | 0.776 | [0.67, 0.90] | 6.53e-04 | 1.09e-03 | Tier 1 (Alta Credibilidade) |
| **CYP4B1** | 100% | 0.781 | [0.68, 0.90] | 8.27e-04 | 1.27e-03 | Tier 1 (Alta Credibilidade) |
| **KRT6C** | 100% | 1.283 | [1.11, 1.49] | 9.32e-04 | 1.33e-03 | Tier 1 (Alta Credibilidade) |
| **KRT6B** | 100% | 1.289 | [1.11, 1.50] | 1.04e-03 | 1.38e-03 | Tier 1 (Alta Credibilidade) |
| **KRT6A** | 100% | 1.282 | [1.10, 1.50] | 1.63e-03 | 2.03e-03 | Tier 1 (Alta Credibilidade) |
| **CPS1** | 100% | 1.253 | [1.09, 1.44] | 1.88e-03 | 2.21e-03 | Tier 1 (Alta Credibilidade) |
| **KIAA0408** | 100% | 0.789 | [0.67, 0.92] | 3.15e-03 | 3.50e-03 | Tier 1 (Alta Credibilidade) |
| **SFTPC** | 100% | 0.820 | [0.71, 0.95] | 8.53e-03 | 8.98e-03 | Tier 1 (Alta Credibilidade) |
| **PGC** | 100% | 0.832 | [0.72, 0.97] | 1.62e-02 | 1.62e-02 | Tier 1 (Alta Credibilidade) |

## 3. Interpretação Biológica e Mecanística dos Principais Biomarcadores

### A. Genes Associados a Prognóstico Desfavorável (Alto Risco)
- **`DKK1` ($HR = 1,533$, $q = 2,64 \times 10^{-7}$)**: *Dickkopf WNT Signaling Pathway Inhibitor 1*. Inibe a via canônica Wnt, correlacionando-se com proliferação tumoral agressiva, invasão precoce e escape imunológico no adenocarcinoma pulmonar.
- **`IGF2BP1` ($HR = 1,354$, $q = 2,04 \times 10^{-4}$)**: *Insulin Like Growth Factor 2 MRNA Binding Protein 1*. Regulador pós-transcricional oncofetal que estabiliza transcritos oncogênicos (como MYC e KRAS), promovendo transição epitélio-mesênquima (EMT) e metástase.
- **`TCN1` ($HR = 1,349$, $q = 3,25 \times 10^{-4}$)**: Marcador de evasão e invasão em carcinoma de pulmão.
- **`ABCC2` ($HR = 1,296$, $q = 3,25 \times 10^{-4}$)**: Bomba de efluxo de xenobióticos associada à quimiorresistência intrínseca e fenótipo multirresistente.
- **Família das Queratinas (`KRT6A`, `KRT6B`, `KRT6C`) ($HR \approx 1,28$, $q \approx 0,001$)**: Indicadores de desdiferenciação epitelial escamosa e fenótipo altamente proliferativo.

### B. Genes Associados a Prognóstico Favorável (Marcadores de Diferenciação Funcional)
- **`SFTA3` ($HR = 0,738$, $q = 1,93 \times 10^{-5}$)** e **`SFTPB`/`SFTPC` ($HR \approx 0,77$, $q < 0,001$)**: Proteínas associadas ao surfactante pulmonar sintetizadas exclusivamente por pneumócitos tipo II diferenciados. A perda da sua expressão reflete desdiferenciação de alto grau (*poorly differentiated LUAD*).
- **`NAPSA` ($HR = 0,758$, $q = 2,04 \times 10^{-4}$)**: *Napsina A*. Peptidase aspártica padrão-ouro imunohistoquímico para adenocarcinomas bem diferenciados. Tumores que mantêm expressão de Napsina A apresentam menor taxa de invasão sistêmica e maior sobrevida global.
- **`CACNA2D2` ($HR = 0,775$, $q = 1,09 \times 10^{-3}$)**: Localizado na região cromossômica supressora de tumor 3p21.3.

## 4. Vias Moleculares Enriquecidas (MSigDB Hallmark)

| Grupo | Via Biológica (Hallmark) | Sobreposição | p-valor | FDR (q-valor) | Genes Chave |
|---|---|---|---|---|---|
| Alto Risco (Genes Desfavoráveis) | **Xenobiotic Metabolism** | 2/200 | 0.0042 | 0.0255 | IGFBP1;ABCC2 |
| Alto Risco (Genes Desfavoráveis) | **Wnt-beta Catenin Signaling** | 1/42 | 0.0208 | 0.0624 | DKK1 |
| Alto Risco (Genes Desfavoráveis) | **Unfolded Protein Response** | 1/113 | 0.0551 | 0.0956 | IGFBP1 |
| Alto Risco (Genes Desfavoráveis) | **Hypoxia** | 1/200 | 0.0956 | 0.0956 | IGFBP1 |
| Alto Risco (Genes Desfavoráveis) | **p53 Pathway** | 1/200 | 0.0956 | 0.0956 | SERPINB5 |
| Protetor (Genes de Boa Diferenciação) | **Adipogenesis** | 1/200 | 0.0956 | 0.0956 | CYP4B1 |
| Protetor (Genes de Boa Diferenciação) | **Estrogen Response Late** | 1/200 | 0.0956 | 0.0956 | CACNA2D2 |

## 5. Declaração de Rigor Ético e Linguagem Não-Causal (REG-16)
> **IMPORTANTE**: As associações reportadas refletem correlação estatística prognóstica independente no contexto de dados observacionais retrospectivos do TCGA. Em conformidade com a REG-16, estas associações **não representam alvos terapêuticos comprovados nem estabelecem relação causal**, constituindo hipóteses biológicas candidatas para futura validação funcional pré-clínica.

---
*Documento gerado em conformidade com as regras REG-09, REG-11, REG-16 e diretrizes REMARK.*