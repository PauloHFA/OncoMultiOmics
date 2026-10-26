# ADR 004: Ajuste Clínico Multivariado com FDR e Enriquecimento de Vias (Q4, REG-11, REG-16)

## Contexto
A identificação de biomarcadores transcricionais requer rigor para evitar falsos positivos decorrentes de confusão por variáveis clínicas basais (como idade e estadiamento patológico AJCC) ou de testes múltiplos em larga escala. Conforme as regras REG-11 e a Seção 9.2 do documento metodológico, cada gene candidato deve:
1. Apresentar estabilidade consistente em reamostragens ($\ge 80\%$ das dobras).
2. Manter significância prognóstica após regressão multivariada de Cox ajustada por idade, sexo e estadiamento.
3. Sobreviver à correção de taxa de falsa descoberta (Benjamini-Hochberg FDR $q < 0,05$).
4. Ser interpretado em nível de vias biológicas (Hallmarks) sem alegações espúrias de causalidade (REG-16).

## Decisão
Implementamos o módulo `src/oncosurv/explicabilidade/interpretacao.py`, que:
- Avalia cada um dos 20 principais genes identificados na validação cruzada 5×5.
- Modela o log-hazard com ajuste multivariado por z-score: $HR = \exp(\beta_{\text{gene}})$.
- Aplica correção de Benjamini-Hochberg para controlar a taxa de falsa descoberta.
- Classifica os genes em Tiers de Credibilidade (Tier 1 a Tier 3).
- Realiza Over-Representation Analysis (ORA) nas vias MSigDB Hallmark 2020 via `gseapy`.

## Resultados Principais
- **100% dos 20 genes candidatos alcançaram a classificação Tier 1 (Alta Credibilidade)** com $q < 0,02$.
- **Núcleo de Risco Desfavorável**:
  - `DKK1` ($HR = 1,533$, $q = 2,64 \times 10^{-7}$): Inibidor de sinalização Wnt/$\beta$-catenina.
  - `IGF2BP1` ($HR = 1,354$, $q = 2,04 \times 10^{-4}$): Proteína ligadora de mRNA oncofetal.
  - `TCN1` ($HR = 1,349$), `ABCC2` ($HR = 1,296$), e família das queratinas `KRT6A/B/C` ($HR \approx 1,28$).
- **Núcleo Protetor (Marcadores de Diferenciação Funcional)**:
  - `SFTA3` ($HR = 0,738$, $q = 1,93 \times 10^{-5}$), `NAPSA` ($HR = 0,758$, $q = 2,04 \times 10^{-4}$), `SFTPB` ($HR = 0,774$), `SFTPC` ($HR = 0,820$).
  - Refletem pneumócitos tipo II diferenciados cuja perda fenotípica correlaciona-se com desdiferenciação tumoral agressiva.
- **Vias Enriquecidas**:
  - `Xenobiotic Metabolism` ($q = 0,0255$) e `Wnt-beta Catenin Signaling` ($p = 0,0208$).

## Consequências
- Os biomarcadores identificados demonstram forte coerência biológica e validade estatística independente da clínica.
- As diretrizes REMARK e regras REG-11 e REG-16 foram rigorosamente atendidas.

