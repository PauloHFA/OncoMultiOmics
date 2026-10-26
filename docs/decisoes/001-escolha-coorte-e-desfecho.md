# ADR 001: Seleção da Coorte Piloto (TCGA-LUAD) e Desfecho Primário (OS)

## Contexto
O projeto OncoMultiOmics Survival Engine visa determinar se perfis transcriptômicos agregam ganho preditivo mensurável em relação a modelos clínicos basais convencionais. Para iniciar a análise com rigor científico e robustez estatística (REG-02 e REG-14), é fundamental selecionar uma coorte com taxa adequada de eventos e tempos de seguimento confiáveis.

## Decisão
1. **Coorte Selecionada**: TCGA-LUAD (*Lung Adenocarcinoma*).
2. **Desfecho Primário**: Sobrevida Global (**OS** — *Overall Survival*).
3. **Horizonte Máximo de Avaliação**: $\tau = 5 \text{ anos}$ ($1.826,25 \text{ dias}$) com censura administrativa.
4. **Fonte Clínica**: TCGA-CDR (Liu et al., *Cell*, 2018), que realizou curadoria estrita dos eventos clínicos de todo o TCGA.

## Consequências
- A coorte LUAD possui volume suficiente de pacientes ($N = 494$ elegíveis com RNA-Seq tumoral primário) e proporção equilibrada de óbitos ($36,4\%$), garantindo poder estatístico para modelos de regressão de Cox e Elastic Net.
- A censura administrativa aos 5 anos limita a instabilidade da cauda longa da curva de Kaplan-Meier.

