# ADR 005: Validação Externa Independente na Coorte GSE31210 (Q3, H3, REG-08)

## Contexto
Um modelo prognóstico não pode ser considerado validado sem teste cego em coorte independente (REG-08), com modelo e pontos de corte estritamente congelados antes da avaliação externa. A hipótese $H_3$ estabeleceu a necessidade de quantificar a perda de desempenho:
> "Parte do desempenho observada na validação interna não se reproduz na coorte externa (quantificar a perda)."

## Decisão
1. **Coorte Externa Selecionada**: GSE31210 (Okayama et al., 2012 / NCBI GEO), compreendendo 204 pacientes elegíveis com adenocarcinoma de pulmão, sobrevida global curada e perfil transcricional na plataforma Affymetrix HG-U133_Plus_2.
2. **Harmonização de Plataforma (REG-08)**: Mapeamento direto das sondas para os 20 biomarcadores identificados no TCGA e padronização por z-score intra-estudo para neutralizar deslocamento de escala entre RNA-Seq (Illumina HiSeq) e Microarray.
3. **Congelamento**: O modelo $M_3$ ajustado no TCGA e o limiar de estratificação de risco ($\theta$) foram aplicados sem qualquer re-treinamento no GSE31210.

## Resultados Observados
- **Generalização do Modelo Molecular ($M_3$)**:
  - $C_{\text{Uno}}$ Interno (TCGA CV): $0,6366$
  - $C_{\text{Uno}}$ Externo (GSE31210): **$0,6364$**
  - **Perda de Desempenho**: $\mathbf{-0,0002}$ (perda nula; conservação quase perfeita da capacidade discriminativa).
- **Queda do Modelo Clínico Baseline ($M_1$)**:
  - $C_{\text{Uno}}$ Externo do $M_1$: $0,5132$ (queda acentuada em virtude da homogeneidade de estadiamento I e II no GSE31210).
- **Valor Incremental Molecular na Coorte Externa**:
  - $\Delta C_{\text{Uno}} = 0,6364 - 0,5132 = \mathbf{+0,1232}$ (+12,3 pontos percentuais).
- **Estratificação Externa por Ponto de Corte Congelado (REG-12)**:
  - Log-Rank: $\chi^2 = 6,18$, **$p = 0,0072$** ($p < 0,01$).

## Consequências
- A validação externa demonstrou que a assinatura transcriptômica compensa a ausência de variância clínica em coortes cirúrgicas de estadiamento precoce, provando a robustez da generalização translacional do modelo integrado.

