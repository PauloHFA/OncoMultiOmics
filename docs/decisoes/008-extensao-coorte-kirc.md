# ADR 008: Extensão da Arquitetura para Segunda Coorte (TCGA-KIRC)

## Contexto
Após o sucesso do desenvolvimento e validação do motor OncoMultiOmics no adenocarcinoma pulmonar (TCGA-LUAD e GSE31210), foi estabelecida a extensão para uma segunda neoplasia independente com biologia tumoral distinta: o Carcinoma Renal de Células Claras (*TCGA-KIRC*), conforme estipulado na Seção 3.3 e nas regras REG-01 a REG-17 do protocolo científico.

## Decisão
1. **Segunda Coorte Selecionada**: TCGA-KIRC (*Kidney Renal Clear Cell Carcinoma*).
2. **Fonte Clínica e Molecular**: Curadoria clínica a partir da tabela suplementar TCGA-CDR (Liu et al., 2018) cruzada com perfil transcriptômico RNA-Seq Illumina HiSeqV2 (UCSC Xena / cBioPortal).
3. **Critérios de Elegibilidade (REG-01, REG-02)**:
   - Amostra sólida primária única por paciente (código '01').
   - Exclusão de tempos nulos ou não-positivos ($OS.time \le 0$).
   - Harmonização de estadiamento patológico AJCC (I a IV).
   - Desfecho primário: Sobrevida Global (OS) com censura administrativa em $\tau = 5 \text{ anos}$ ($1.826,25 \text{ dias}$).
4. **Isolamento de Vazamento (REG-03) e Desenho Experimental**:
   - Validação cruzada repetida 5x5 estratificada por evento (25 dobras, REG-06).
   - Seleção univariada de genes (`FastCoxScoreSelector`), escalonamento e sintonização de regularização elástica (nested CV) estritamente intra-fold.
   - Ajuste clínico multivariado com correção Benjamini-Hochberg (FDR $q$-value) para biomarcadores candidatos (REG-11).

## Consequências
- A coorte TCGA-KIRC final conta com $N = 528$ pacientes elegíveis com tecido tumoral primário curado e $149$ eventos de óbito no horizonte $\tau = 5$ anos ($28,2\%$).
- O seguimento mediano (via Kaplan-Meier reverso) é de $4,61$ anos ($1.684,5$ dias), proporcionando alta maturidade estatística.
- Demonstra a versatilidade, reprodutibilidade e generalizabilidade do pipeline OncoMultiOmics para diferentes tipos tumorais sem modificação na infraestrutura central de modelagem e validação.

