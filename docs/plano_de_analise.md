# OncoMultiOmics Survival Engine — Plano de Análise Científica (Fase 0)

> **Documento de Pré-Registro Metodológico**  
> Elaborado em conformidade com as diretrizes **TRIPOD+AI** e **REMARK**.  
> Registrado antes de qualquer ajuste de modelo ou abertura do conjunto de teste (REG-02, REG-14).

---

## 1. Definição do Estudo e Pergunta Científica

- **Objetivo**: Estimar para cada paciente oncológico a curva de probabilidade de sobrevivência ao longo do tempo integrando variáveis clínicas basais e perfil de expressão gênica (RNA-Seq), testando se a informação molecular confere ganho preditivo incremental estatisticamente significativo além da informação clínica disponível no momento do diagnóstico.
- **Pergunta Principal ($Q_1$)**: A expressão gênica melhora a predição de sobrevivência em relação ao modelo baseado exclusivamente em variáveis clínicas convencionais ($M_3 \text{ vs. } M_1$)?
- **Perguntas Secundárias**:
  - **$Q_2$**: Qual estratégia de redução de dimensionalidade e algoritmo (Cox penalizado Elastic Net, Random Survival Forest, Gradient Boosting Survival) apresenta o melhor equilíbrio entre discriminação e calibração?
  - **$Q_3$**: O modelo treinado generaliza em coorte externa independente com perda de desempenho quantificada?
  - **$Q_4$**: Quais genes e vias biológicas associam-se ao prognóstico de forma estável (bootstrap) e independente das variáveis clínicas (ajuste multivariado com FDR)?
  - **$Q_5$**: O modelo estratifica pacientes em grupos de risco com curvas de sobrevivência significativamente distintas utilizando limiares fixados no treino?

---

## 2. Hipóteses Falsificáveis

1. **$H_1$**: O modelo integrado clínico + expressão ($M_3$) apresenta C-index de Uno com horizonte $\tau$ superior ao modelo apenas clínico ($M_1$), com intervalo de confiança de 95% derivado por bootstrap que exclui a diferença nula ($\Delta\text{C-index} > 0$).
2. **$H_2$**: Modelos lineares penalizados (Cox Elastic Net) apresentam desempenho discriminativo e de calibração comparável ou superior a algoritmos não-lineares/árvores nas dimensões amostrais do TCGA.
3. **$H_3$**: O desempenho discriminativo na validação externa sofrerá degradação mensurável em relação à validação cruzada interna, documentando a perda de generalização.

---

## 3. Coorte Selecionada e Desfecho (TCGA-CDR)

- **Coorte Piloto**: **TCGA-LUAD** (*Lung Adenocarcinoma*).
  - *Justificativa*: Alta taxa de eventos observados, maturidade de seguimento no TCGA, relevância clínica e orientação explícita no recurso clínico padronizado TCGA-CDR (*Liu et al., Cell 2018*).
- **Desfecho Primário**: **OS** (*Overall Survival* — Sobrevida Global).
  - Variáveis TCGA-CDR: `OS` (status do evento binário: 0 = censurado, 1 = óbito) e `OS.time` (tempo em dias até o evento ou última data de seguimento).
  - *Desfecho Secundário para Análise de Sensibilidade*: **PFI** (*Progression-Free Interval*).
- **Horizonte Temporal Máximo ($\tau$)**:
  - $\tau = 5 \text{ anos}$ ($1.826,25 \text{ dias}$).
  - Eventos ou tempos de seguimento superiores a $\tau$ serão censurados administrativamente em $\tau$, evitando a instabilidade da cauda longa da curva de Kaplan-Meier.
- **Horizontes Dinâmicos de Avaliação ($t$)**:
  - $t_1 = 1 \text{ ano}$ ($365,25 \text{ dias}$)
  - $t_2 = 3 \text{ anos}$ ($1.095,75 \text{ dias}$)
  - $t_3 = 5 \text{ anos}$ ($1.826,25 \text{ dias}$)

---

## 4. Regras de Curadoria e Funil de Exclusão (REG-01, REG-13)

1. **Amostra Única por Paciente (REG-01)**:
   - Identificação do paciente: primeiros 12 caracteres do código de barras TCGA (`TCGA-XX-XXXX`).
   - Tipo de amostra: caracteres 14-15 (`01` = Tumor Sólido Primário).
   - Exclusão estrita de amostras normais de controle adjacente (`11`), tecidos normais derivados de sangue (`10`) e metástases (`06`).
   - Se houver múltiplas alíquotas `01` para o mesmo paciente, manter a primeira alíquota por critério determinístico fixado e registrado no funil.
2. **Critérios de Exclusão de Pacientes**:
   - Pacientes sem dados de tempo ou com `OS.time <= 0`.
   - Pacientes sem estágio patológico/clínico documentado ou sem idade ao diagnóstico.
   - Pacientes com amostras FFPE (se presentes).
3. **Funil de Exclusão**:
   - Cada etapa de filtragem deve registrar: $N_{\text{inicial}} \to N_{\text{excluídos por motivo}} \to N_{\text{final}}$, além de número de eventos e mediana de seguimento via KM reverso.

---

## 5. Pré-Processamento Molecular (RNA-Seq)

1. **Anotação de Genes**:
   - Filtrar apenas genes codificadores de proteína (*protein-coding genes*) a partir dos identificadores Ensembl/GENCODE.
2. **Filtro de Baixa Expressão (Não-Supervisionado)**:
   - Remoção de genes com expressão TPM $\le 1.0$ em mais de 80% das amostras (isto é, manter apenas genes com expressão detectada em pelo menos 20% da coorte).
3. **Transformação**:
   - Escala padrão: $\log_2(\text{TPM} + 1)$.
4. **Isolamento de Vazamento (REG-03)**:
   - Qualquer padronização estatística (ex: `StandardScaler`), seleção de genes supervisionada ou redução de dimensionalidade (ex: PCA) deve ter seus parâmetros aprendidos **exclusivamente no conjunto de treinamento de cada dobra** da validação cruzada.

---

## 6. Escada de Modelos e Avaliação

| ID | Modelo | Covariáveis | Papel |
|---|---|---|---|
| **$M_0$** | Kaplan-Meier | Nenhuma (nulo) | Referência nula ($\text{C-index} = 0,5$) |
| **$M_1$** | Cox PH Clínico | Idade, Sexo, Estágio AJCC (I a IV), Tabagismo | Baseline obrigatório de comparação |
| **$M_2$** | Cox Elastic Net Molecular | Genes filtrados | Força preditiva isolada do transcriptoma |
| **$M_3$** | Cox Elastic Net Integrado | Clínico (não-penalizado) + Genes | **Modelo integrado principal** |
| **$M_4$** | Cox + Assinaturas Gênicas | Clínico + Hallmarks/GSVA | Modelo interpretável baseado em vias |
| **$M_5$** | Random Survival Forest (RSF) | Clínico + Genes selecionados | Relações não-lineares e interações |
| **$M_6$** | Gradient Boosting Survival | Clínico + Genes selecionados | Aprendizado ensemble com regularização |

---

## 7. Estratégia de Validação e Métricas (REG-05, REG-06, REG-07, REG-12)

1. **Esquema de Validação**:
   - **Validação Cruzada Repetida**: 5 repetições de 5-fold CV ($5 \times 5 = 25$ dobras), estratificada pelo status do evento (`event`).
   - **Validação Aninhada (*Nested CV*)**: Laço interno com 5 folds para sintonização do hiperparâmetro de regularização ($\alpha$, $\ell_1\text{-ratio}$) do Cox Elastic Net.
2. **Métricas Obrigatórias**:
   - **C-index de Uno ($C_{\text{Uno}}$)** com correção por IPCW (*Inverse Probability of Censoring Weighting*) fixado no horizonte $\tau$.
   - **AUC Dinâmico Cumulativo ($AUC(t)$)** nos horizontes de 1, 3 e 5 anos.
   - **Integrated Brier Score (IBS)** comparado ao modelo nulo de Kaplan-Meier.
   - **Curva e Inclinação de Calibração** por decis/quantis de risco em $\tau$.
   - **Ganho Incremental**: $\Delta C_{\text{Uno}} = C_{\text{Uno}}(M_3) - C_{\text{Uno}}(M_1)$.
3. **Inferência Estatística e Incerteza**:
   - Intervalos de confiança de 95% calculados por **Bootstrap por Paciente** (1.000 replicações).
   - Teste de comparação pareada com correção amostral de Nadeau & Bengio para dobras repetidas.
4. **Estratificação de Risco (REG-12)**:
   - Ponto de corte (ex: mediana de risco estimado) **definido exclusivamente no treino** e aplicado cegamente ao teste.
   - Curvas de Kaplan-Meier nos grupos de Alto e Baixo Risco com teste log-rank.

---

## 8. Conformidade Ética e de Rigor (REG-09 a REG-17)

- **Diagnóstico de Lote (REG-09)**: Avaliação de TSS (*Tissue Source Site*) e centro de sequenciamento via PCA para descartar associações espúrias com tempo de sobrevida.
- **Riscos Proporcionais (REG-10)**: Verificação dos resíduos de Schoenfeld nos modelos Cox.
- **Linguagem (REG-16)**: Associação prognóstica correlacional; jamais alegações de causalidade ou direcionamento terapêutico sem ensaio prospectivo.
- **Transparência (REG-17)**: Publicação e documentação integral de resultados nulos ou ganhos marginais.

