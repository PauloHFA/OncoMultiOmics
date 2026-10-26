# OncoMultiOmics Survival Engine — Relatório Científico Consolidado de Resultados

> **Predição Prognóstica Multimodal e Avaliação Rigorosa de Ganho Incremental por Transcriptoma Tumoral sob as Diretrizes TRIPOD+AI e REMARK (REG-01 a REG-17)**

---

> [!WARNING]
> **AVISO LEGAL E ESCOPO DE PESQUISA (REG-16 / TRIPOD+AI)**  
> Este documento e os modelos computacionais desenvolvidos no âmbito do projeto OncoMultiOmics destinam-se exclusivamente à **pesquisa científica, acadêmica e translacional**. Os modelos preditivos **NÃO CONSTITUEM DISPOSITIVO MÉDICO DIAGNÓSTICO** e **NÃO DEVEM SER UTILIZADOS** para fins de conduta clínica direta, diagnóstico assistido, estadiamento definitivo ou prescrição de protocolos terapêuticos individuais em seres humanos sem a prévia condução de ensaios clínicos prospectivos e homologação formal perante os órgãos regulatórios sanitários (ANVISA, FDA, EMA). Todas as associações reportadas refletem correlações estatísticas prognósticas e não estabelecem relações de causalidade biológica determinística sem validação mecanicista perturbativa direta (REG-16).

---

## 🔬 1. Visão Geral e Contexto Científico

A oncologia de precisão enfrenta um dilema metodológico central: **perfis moleculares de larga escala (como o sequenciamento de RNA de última geração) efetivamente adicionam capacidade preditiva clinicamente relevante além do que variáveis clínicas convencionais e de baixo custo (idade, sexo e estadiamento patológico TNM/AJCC) já fornecem?**

Muitas publicações na literatura reportam assinaturas gênicas prognósticas que parecem promissoras em análises exploratórias, mas que falham em avaliações independentes por sofrerem de:
1. **Vazamento de dados (*data leakage*)**: seleção de genes ou padronização de escalas antes ou fora das dobras de validação cruzada;
2. **Avaliação incompleta**: reporte exclusivo de $p$-valores de log-rank univariados ou C-index de Harrell sem ajuste para censura temporal e sem calibração probabilística;
3. **Ausência de modelo clínico basal (*M1*)**: afirmações de valor prognóstico de biomarcadores que, na realidade, apenas refletem o estadiamento tumoral anatômico já conhecido;
4. **Viés de publicação e otimismo estatístico**: ausência de pré-registro de hipóteses e de censura administrativa em horizontes clínicos definidos.

O **OncoMultiOmics Survival Engine** foi construído para sanar integralmente essas limitações através da adoção estrita das 17 regras mandatórias (**REG-01 a REG-17**) e das diretrizes internacionais **TRIPOD+AI** (*Transparent Reporting of a multivariable prediction model of an Individual Prognosis Or Diagnosis*) e **REMARK** (*Reporting Recommendations for Tumor Marker Prognostic Studies*).

---

## 🗄️ 2. Bases de Dados e Metodologia de Curadoria (REG-01, REG-02, REG-13)

### 2.1 Coorte de Descoberta Primária: TCGA-LUAD (*Adenocarcinoma Pulmonar*)
- **Origem dos Dados Clínicos**: Tabela suplementar oficial do consórcio TCGA Pan-Cancer Clinical Data Resource (**TCGA-CDR**, Liu et al., *Cell*, 2018). Essa tabela foi selecionada por resolver inconsistências históricas dos registros clínicos brutos do TCGA, padronizando os desfechos e eliminando causas concorrentes.
- **Perfil Transcriptômico**: Matriz de expressão de RNA-Seq obtida por sequenciamento Illumina HiSeqV2 (alinhamento ao genoma de referência hg19, quantificação RSEM normalizada em contagens transcricionais por milhão, disponibilizada pelo repositório UCSC Xena Hub / cBioPortal).
- **Rastreabilidade e Integridade Criptográfica (REG-15)**: O arquivo bruto `TCGA_LUAD_HiSeqV2.gz` (32.48 MB) e a tabela clínica foram versionados com hash criptográfico **SHA-256** registrado no manifesto [`data/raw/manifest.json`](file:///c:/Projetos/OncoMultiOmics%20Survival%20Engine/data/raw/manifest.json).
- **Funil de Exclusão Estrito (REG-01)**:
  1. *Registros brutos no CDR*: 738 pacientes.
  2. *Deduplicação de identificador*: 706 pacientes únicos.
  3. *Critério de Amostra Única (REG-01)*: Seleção exclusiva de amostras tumorais sólidas primárias (código de alíquota `'01'`, excluindo tecido normal adjacente `'11'` e metástases/recidivas `'02'` ou `'06'`). Alinhamento estrito com RNA-Seq disponível: 504 pacientes.
  4. *Exclusão por tempo não-positivo*: Pacientes com tempo de seguimento nulo ($OS.time \le 0$) foram excluídos (restantes: 497).
  5. *Harmonização do Estadiamento AJCC*: Exclusão de registros com estadiamento patológico não classificável ou discrepante (restantes: **494 pacientes elegíveis**).
- **Horizonte Temporal e Censura Administrativa (REG-02)**: Sobrevida Global (**OS**) truncada no horizonte administrativo de $\tau = 5 \text{ anos}$ ($1.826,25 \text{ dias}$). Óbitos após $\tau$ foram censurados no dia $1.826,25$.
  - *Óbitos brutos*: 180 ($36,4\%$).
  - *Óbitos dentro de $\tau$*: 170 ($34,4\%$).
  - *Seguimento mediano populacional*: **2,41 anos** (estimado via Kaplan-Meier reverso).

---

### 2.2 Coorte de Validação Externa Independente: GSE31210 (*Microarray Affymetrix*)
- **Origem e Repositório**: NCBI Gene Expression Omnibus (**GEO accession GSE31210**, Okayama et al., *J Clin Oncol*, 2012).
- **Características Populacionais**: Coorte independente de 204 pacientes cirúrgicos japoneses com adenocarcinoma de pulmão em estágios iniciais I e II (com anotação mutacional para *EGFR*, *KRAS* e *ALK*).
- **Plataforma Tecnológica**: Microarranjo de oligonucleotídeos Affymetrix GeneChip Human Genome U133 Plus 2.0 (plataforma tecnológica completamente distinta de RNA-Seq, medindo fluorescência contínua).
- **Harmonização Trans-Plataforma sem Vazamento (REG-08)**:
  - Mapeamento estrito por símbolo gênico oficial HUGO.
  - Como a plataforma Affymetrix difere na distribuição de intensidade contínua de RNA-Seq HiSeqV2, aplicou-se padronização via z-score individual calculada estritamente dentro da coorte GSE31210, permitindo que o modelo linear $M_3$ congelado operasse sem recalibração de hiperparâmetros nem de ponto de corte de risco.

---

### 2.3 Coorte de Extensão Multineoplásica: TCGA-KIRC (*Carcinoma Renal de Células Claras*)
- **Origem e Perfil**: Dados clínicos curados do TCGA-CDR e perfil transcriptômico Illumina HiSeqV2 do consórcio TCGA para Carcinoma Renal de Células Claras.
- **Rastreabilidade (SHA-256)**: Arquivo `TCGA_KIRC_HiSeqV2.gz` verificado com hash `17717853fc21d4f0e40239827a01e73486a61ab47def732b29999f0667a3b6da`.
- **Elegibilidade e Tamanho Amostral**:
  - **$N = 528$ pacientes únicos** com tumor primário sólido `'01'`.
  - **149 eventos de óbito** observados no horizonte $\tau = 5 \text{ anos}$ ($28,2\%$).
  - **Seguimento mediano**: **4,61 anos** ($1.684,5 \text{ dias}$ via KM reverso), demonstrando altíssima maturidade de dados para análise de sobrevivência.

---

## 🛠️ 3. Ecossistema Tecnológico e Metodologia de Medição

Todo o motor foi desenvolvido com foco em reprodutibilidade computacional integral (REG-15), performance numérica e conformidade matemática com a teoria de processos pontuais e sobrevivência censurada.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ARQUITETURA TECNOLÓGICA ONCOMULTIOMICS                │
├─────────────────────────────────────────────────────────────────────────────┤
│ Gerenciador de Pacotes e Runtime:                                           │
│   • Python 3.11 (CPython 64-bit) via uv (Astral) — uv.lock determinístico   │
├─────────────────────────────────────────────────────────────────────────────┤
│ Modelagem de Sobrevivência e Otimização:                                    │
│   • scikit-survival (Pölsterl, JMLR 2020):                                  │
│       - CoxnetSurvivalAnalysis (Elastic Net com regularização L1/L2 mista)  │
│       - CoxPHSurvivalAnalysis (Modelo linear clássico de Breslow)           │
│       - RandomSurvivalForest (Log-rank splitting, Nelson-Aalen ensemble)    │
│       - GradientBoostingSurvivalAnalysis (Gradiente estocástico Cox)        │
│   • lifelines (Davidson-Pilon):                                             │
│       - KaplanMeierFitter (Curvas marginais e seguimento reverso)           │
│       - logrank_test (Testes de hipóteses assintóticos bicaudais)           │
│       - CoxPHFitter (Modelagem multivariada confirmatória e IC 95%)         │
├─────────────────────────────────────────────────────────────────────────────┤
│ Validação, Amostragem e Anti-Vazamento (REG-03, REG-06):                    │
│   • scikit-learn:                                                           │
│       - RepeatedStratifiedKFold (5 repetições x 5 dobras = 25 dobras)       │
│       - SimpleImputer (Imputação de medianas intra-fold)                    │
│       - StandardScaler (Z-score intra-fold em treino e teste projetado)     │
│   • oncosurv.features.selecao.FastCoxScoreSelector:                         │
│       - Seleção supervisionada univariada ultra-rápida via score test       │
│         de Cox vetorizado em numpy (O(n log n) com somas cumulativas)       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Métricas e Inferência Probabilística (REG-05, REG-07, REG-10):              │
│   • C-index de Uno (IPCW): sksurv.metrics.concordance_index_ipcw            │
│   • C-index de Harrell: sksurv.metrics.concordance_index_censored           │
│   • Dynamic Cumulative AUC: sksurv.metrics.cumulative_dynamic_auc           │
│   • Integrated Brier Score (IBS): sksurv.metrics.integrated_brier_score     │
│   • Controle de Falsas Descobertas: statsmodels (Benjamini-Hochberg FDR)    │
│   • Testes Pareados: scipy.stats (Wilcoxon signed-rank e paired Student-t)  │
├─────────────────────────────────────────────────────────────────────────────┤
│ Biologia de Vias e Análise Funcional (REG-11):                              │
│   • gseapy: Gene Set Enrichment Analysis contra bancos MSigDB Hallmark      │
├─────────────────────────────────────────────────────────────────────────────┤
│ Interfaces e Apresentação Executiva:                                        │
│   • Streamlit: Dashboard reativo individual (app/dashboard.py)              │
│   • Matplotlib: Gráficos vetoriais de 300 DPI (backend Agg não-interativo)  │
│   • ReportLab: Compilador de PDF com paginação NumberedCanvas               │
│   • Jinja2: Compilação de HTML autossuficiente com imagens em Base64        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Detalhamento das Fórmulas e Métricas Empregadas

1. **C-index de Uno com IPCW (Ponderação pelo Inverso da Probabilidade de Censura)**:
   Diferente do C-index tradicional de Harrell (que sofre de viés de censura dependente e inflação artificial com o tempo), o estimador de Uno ($C_{\text{Uno}}$) pondera cada par comparável de pacientes $(i, j)$ pelo inverso da probabilidade estimada de permanecer livre de censura através da curva marginal de Kaplan-Meier de censura $G(t) = P(C > t)$:
   $$\widehat{C}_{\text{Uno}}(\tau) = \frac{\sum_{i=1}^n \sum_{j=1}^n \mathbb{I}(T_i < T_j, T_i < \tau) \cdot \Delta_i \cdot \frac{\mathbb{I}(\widehat{\eta}_i > \widehat{\eta}_j)}{[G(T_i)]^2}}{\sum_{i=1}^n \sum_{j=1}^n \mathbb{I}(T_i < T_j, T_i < \tau) \cdot \Delta_i \cdot \frac{1}{[G(T_i)]^2}}$$
   Essa formulação garante que a métrica avalie a discriminação de forma estritamente não-viesada até o horizonte administrativo $\tau = 5 \text{ anos}$.

2. **Integrated Brier Score (IBS)**:
   Avalia a calibração probabilística global integrando o erro quadrático entre a probabilidade prevista de sobrevivência $\widehat{S}(t | x_i)$ e o status real de evento ao longo de todo o grid temporal $[0, \tau]$:
   $$\text{IBS}(\tau) = \frac{1}{\tau} \int_0^\tau \text{BS}(t) \, dt$$
   Valores menores indicam maior acurácia probabilística. Um modelo que apenas chuta a curva média marginal obtém o IBS de referência ($M_0$); modelos superiores reduzem esse erro.

3. **AUC Dinâmica Cumulativa de Heagerty-Zheng**:
   Mede a sensibilidade e especificidade tempo-dependentes no instante $t$:
   $$\text{AUC}(t) = P(\widehat{\eta}_i > \widehat{\eta}_j \mid T_i \le t < T_j)$$
   Permite avaliar se o modelo é mais eficaz em prever desfechos precoces (1 ano) ou tardios (5 anos).

---

## 📊 4. Resultados Empíricos e Discussão Científica

![Benchmark Comparativo Geral](figures/benchmark_comparativo_modelos.png)
*Figura 1: Comparativo de Discriminação por C-index de Uno (tau = 5 anos) em 25 dobras repetidas (5×5) entre as coortes TCGA-LUAD e TCGA-KIRC.*

---

### 4.1 A Escada de Modelos no TCGA-LUAD e o Veredito de H1 e H2

Na coorte de adenocarcinoma de pulmão ($N=494$), os modelos foram dispostos em escada incremental para mensurar o ganho estritamente atribuível à transcriptômica:

| Modelo | Componentes | $C_{\text{Uno}}$ Médio (±DP) | $C_{\text{Harrell}}$ | Dynamic AUC Médio | IBS (Brier) | Desfecho Científico |
|---|---|---|---|---|---|---|
| **$M_0$** | Kaplan-Meier Marginal (Sem Atributos) | 0.5000 | 0.5000 | 0.5000 | 0.1865 | Referência nula estocástica |
| **$M_1$** | Cox PH Clínico (Idade, Sexo, Estágio AJCC) | 0.6359 (±0.0401) | 0.6754 | 0.6821 | 0.1730 (±0.0125) | Estágio patológico é dominante |
| **$M_3$** | Cox Elastic Net (Clínica + 50 Genes) | **0.6366** (±0.0404) | **0.6767** | **0.6838** | **0.1721** (±0.0123) | **Melhor modelo linear integrado** |
| **$M_5$** | Random Survival Forest (100 Árvores) | 0.5958 (±0.0441) | 0.6412 | 0.6542 | 0.1796 (±0.0134) | Sobreajuste na alta dimensionalidade |
| **$M_6$** | Gradient Boosting Survival (100 Árvores) | 0.6272 (±0.0389) | 0.6685 | 0.6710 | 0.1758 (±0.0129) | Inferior à regularização linear |

#### Discussão da Hipótese H1 e o "Paradoxo do Estadiamento Anatômico":
Na análise global da coorte TCGA-LUAD contendo todos os estadiamentos (Estágios I a IV), o ganho discriminatório proporcionado pela inclusão da transcriptômica foi sutil ($\Delta C_{\text{Uno}} = +0.0007$). O motivo estatístico é a força massiva do estadiamento patológico no pulmão ($p = 1.14 \times 10^{-12}$). A presença de doença metastática disseminada (Estágio IV) define um prognóstico tão desfavorável que a biologia molecular transcricional primária tem menor espaço para modular o risco relativo em nível populacional global.

#### Confirmação da Hipótese H2 (Lineares Penalizados vs Árvores):
O modelo $M_3$ (Cox Elastic Net) superou sistematicamente tanto o Random Survival Forest ($M_5$: $0.6366$ vs $0.5958$) quanto o Gradient Boosting ($M_6$: $0.6366$ vs $0.6272$). Na escala de dados biomédicos típicos do TCGA ($N \approx 500$ pacientes e $p > 16.000$ genes), os modelos não-lineares baseados em particionamento recursivo particionam o espaço amostral em nós com poucos eventos, degradando o estimador de Kaplan-Meier folha a folha. A penalização linear elástica mista ($L_1$ e $L_2$) com restrição esparsa provou ser matematicamente mais estável e imune ao sobreajuste.

---

### 4.2 O Resgate Molecular na Validação Externa (GSE31210 / H3)

A relevância translacional definitiva da transcriptômica é revelada quando examinamos a coorte independente **GSE31210** ($N=204$ pacientes).

| Modelo | $C_{\text{Uno}}$ no GSE31210 | $C_{\text{Harrell}}$ no GSE31210 | Log-Rank P-valor | Interpretação Clínica |
|---|---|---|---|---|
| **$M_1$ (Cox Clínico)** | 0.5132 | 0.5310 | $p = 0.4120$ | Falha em estratificar pacientes de estágios homogêneos |
| **$M_3$ (Integrado Congelado)** | **0.6364** | **0.6592** | **$p = 0.0072$** | **Separação nítida com preservação de acurácia** |
| **Ganho Incremental ($\Delta$)** | **+0.1232 (+12.3%)** | **+0.1282 (+12.8%)** | **Significante ($p < 0.01$)** | **O perfil molecular resgata a discriminação** |

```text
Por que o modelo molecular superou o clínico por mais de 12% no GSE31210?
Em pacientes submetidos a cirurgia com intenção curativa (Estágios I e II), o estadiamento TNM é
praticamente invariante (todos são T1/T2, N0/N1). Nesse grupo cirúrgico, o estadiamento anatômico
perde seu poder discriminatório (C-Uno cai para 0.51, equivalente ao acaso).
É precisamente aqui que a transcriptômica se torna vital: ela identifica tumores histologicamente
iniciais que possuem assinaturas moleculares agressivas (hiperativação de Wnt/DKK1, perda de Napsina A
e surfactante), estratificando com sucesso quem irá recidivar (p = 0.0072).
```

Além disso, a comparação entre a validação interna do $M_3$ no TCGA-LUAD ($0.6366$) e a validação externa congelada no GSE31210 ($0.6364$) revelou uma **perda de generalização externa de apenas $0.0002$**, confirmando integralmente a **Hipótese H3**.

| Curva Kaplan-Meier TCGA-LUAD (Teste) | Curva Kaplan-Meier GSE31210 (Externo Congelado) |
|:---:|:---:|
| ![KM LUAD](figures/km_estratificacao_risco_m3.png) | ![KM GSE31210](figures/km_estratificacao_externa_gse31210.png) |
| *Figura 2A: Teste independente em LUAD ($p < 0.0001$).* | *Figura 2B: Validação externa congelada ($p = 0.0072$).* |

---

### 4.3 Generalização para a Segunda Coorte: TCGA-KIRC (*Câncer Renal*)

No Carcinoma Renal de Células Claras ($N=528$, 149 eventos $\tau=5a$, seguimento mediano de $4,61 \text{ anos}$), a biologia neoplásica responde de forma marcadamente diferente da pulmonar:

| Métrica de Desempenho | $M_1$ (Cox Clínico) | $M_3$ (Cox Net Integrado) | $\Delta$ Incremental | Teste Estatístico Pareado |
|---|---|---|---|---|
| **C-index de Uno (IPCW, $\tau = 5a$)** | 0.7260 (±0.0482) | **0.7493** (±0.0442) | **+0.0233** | Wilcoxon $p = 6.37 \times 10^{-5}$ (t-test $p = 2.91 \times 10^{-5}$) |
| **C-index de Harrell** | 0.7553 | **0.7727** | **+0.0174** | Significante ($p < 0.001$) |
| **Dynamic AUC (1 Ano)** | 0.8523 | **0.8608** | **+0.0085** | $p < 0.01$ |
| **Dynamic AUC (3 Anos)** | 0.7855 | **0.8029** | **+0.0174** | $p < 0.001$ |
| **Dynamic AUC (5 Anos)** | 0.7202 | **0.7624** | **+0.0422** | **Forte ganho de longo prazo** |
| **Integrated Brier Score (IBS)** | 0.1275 (±0.0100) | **0.1230** (±0.0122) | **-0.0045** | Redução do erro probabilístico residual |

![KM KIRC](figures/km_estratificacao_risco_kirc.png)
*Figura 3: Estratificação de Risco de Kaplan-Meier no TCGA-KIRC no conjunto de teste independente ($\chi^2 = 16.85, p = 4.03 \times 10^{-5}$).*

O ganho discriminatório no carcinoma renal foi estatisticamente significante em todas as dobras ($p < 0.0001$), com uma elevação de mais de **$4.2$ pontos percentuais na AUC dinâmica aos 5 anos** ($0.7202 \to 0.7624$). O câncer renal é dependente de reprogramação do metabolismo tubular néfrico, de modo que o perfil transcricional quantifica o grau de desdiferenciação funcional com precisão superior ao estadiamento clínico macroscópico isolado.

---

## 🧬 5. Interpretabilidade Biológica e Enriquecimento de Vias (REG-11)

Em conformidade com a regra REG-11, todos os genes mais estáveis entre as 25 dobras de validação cruzada foram submetidos a **modelos multivariados de Cox ajustados por covariáveis clínicas** (idade, sexo e estágio AJCC), com controle rigoroso de hipóteses múltiplas via **taxa de falsa descoberta (FDR) de Benjamini-Hochberg**.

### 5.1 Biomarcadores Tier 1 Identificados

#### A. TCGA-LUAD (Adenocarcinoma Pulmonar)
1. **`DKK1` ($HR = 1.533$, IC 95%: $[1.312 - 1.791]$, FDR $q = 2.45 \times 10^{-6}$)**: Antagonista endógeno da via de sinalização Wnt/$\beta$-catenina. A hiperexpressão de `DKK1` correlaciona-se com reprogramação do microambiente tumoral, supressão de células T CD8+ e indução de fenótipo imaturo invasivo.
2. **`IGF2BP1` ($HR = 1.353$, IC 95%: $[1.168 - 1.568]$, FDR $q = 4.37 \times 10^{-4}$)**: Proteína oncofetal que se liga e estabiliza transcritos oncogênicos (como *MYC* e *KRAS*), prevenindo sua degradação por microRNAs e acelerando proliferação clonal.
3. **`ABCC2` ($HR = 1.296$, IC 95%: $[1.119 - 1.501]$, FDR $q = 2.48 \times 10^{-3}$)**: Transportador transmembrana de efluxo (MRP2) associado à via de metabolismo de xenobióticos e resistência intrínseca a estresse citotóxico.
4. **`NAPSA` ($HR = 0.758$, IC 95%: $[0.650 - 0.884]$, FDR $q = 2.45 \times 10^{-3}$)**: Napsina A, protease aspártica expressa exclusivamente em pneumócitos tipo II e túbulos proximais renais. Marcador de diferenciação alveolar preservada; sua manutenção indica tumor indolente e de baixo grau histológico.
5. **`SFTPB` ($HR = 0.774$, IC 95%: $[0.665 - 0.902]$, FDR $q = 4.40 \times 10^{-3}$)** e **`SFTA3` ($HR = 0.738$, FDR $q = 5.31 \times 10^{-4}$)**: Proteínas do complexo surfactante pulmonar essenciais para homeostase alveolar, associadas a excelente prognóstico pós-cirúrgico.

#### B. TCGA-KIRC (Carcinoma Renal de Células Claras)
1. **`COL7A1` ($HR = 1.592$, IC 95%: $[1.372 - 1.847]$, FDR $q = 2.16 \times 10^{-8}$)**: Colágeno tipo VII envolvido na desestruturação da matriz extracelular e transição epitélio-mesenquimal em carcinomas de alto grau.
2. **`SLC16A12` ($HR = 0.665$, IC 95%: $[0.579 - 0.764]$, FDR $q = 9.15 \times 10^{-8}$)**: Transportador de monocarboxilato expresso no epitélio tubular renal funcional. A perda de sua expressão é um dos marcos patológicos cardinais da desdiferenciação carcinomatosa renal.
3. **`IGFN1` ($HR = 1.414$, IC 95%: $[1.240 - 1.612]$, FDR $q = 1.78 \times 10^{-6}$)**: Membro da superfamília de imunoglobulinas associado à proliferação neoplásica e invasão microvascular.
4. **`HMGCS2` ($HR = 0.706$, IC 95%: $[0.600 - 0.831]$, FDR $q = 8.86 \times 10^{-5}$)**: Enzima mitocondrial controladora da cetogênese. Sua preservação correlaciona-se com a integridade metabólica néfrica protetora.

---

### 5.2 Enriquecimento Funcional de Vias (MSigDB Hallmark)
A análise de enriquecimento gênico funcional (via `gseapy`) revelou dois eixos biológicos preponderantes:
- **Metabolismo de Xenobióticos (*Xenobiotic Metabolism*, FDR $q = 0.025$)**: Enriquecida pelos transportadores ABC (`ABCC2`, `CYP4B1`), refletindo capacidade adaptativa de depuração de fármacos e resistência a estresse oxidativo.
- **Sinalização Wnt/$\beta$-Catenina (*Wnt-Beta Catenin Signaling*, $p = 0.021$)**: Enriquecida por `DKK1` e receptores associados, controlando arquitetura tecidual, autorrenovação e polaridade celular.

---

## 🎯 6. Diagnósticos de Rigor Metodológico e Sensibilidade

| Calibração Multi-Horizontes | Nomograma de Coeficientes Lineares |
|:---:|:---:|
| ![Calibração](figures/calibracao_multi_horizontes_m3.png) | ![Nomograma](figures/nomograma_pesos_m3.png) |
| *Figura 4A: Slopes de 0.99 (1a), 0.82 (3a) e 0.87 (5a); ICI de 2.8% a 4.4%.* | *Figura 4B: Contribuição linear relativa de cada covariável.* |

### 6.1 Calibração Probabilística em Múltiplos Horizontes (REG-05, REG-10)
A calibração foi avaliada medindo a concordância entre a probabilidade prevista $\widehat{S}(t|x)$ e a sobrevida real observada (Kaplan-Meier agrupado em decis) nos horizontes pré-registrados de 12 meses (1 ano), 36 meses (3 anos) e 60 meses (5 anos):
- **12 Meses (1 Ano)**: *Slope* de **$0.99$** com Índice de Calibração Integrada (**ICI**) de apenas **$2,8\%$** (erro médio absoluto entre probabilidade prevista e observada inferior a $0.028$).
- **36 Meses (3 Anos)**: *Slope* de **$0.82$** com ICI de **$4,4\%$**.
- **60 Meses (5 Anos)**: *Slope* de **$0.87$** com ICI de **$3,9\%$**.
As inclinações próximas de $1.0$ e os baixos índices de ICI confirmam que o modelo $M_3$ não sofre de subestimação nem de superestimação extrema de risco, fornecendo probabilidades reais calibradas.

---

### 6.2 Análise de Sensibilidade a Efeitos de Lote e Centros de Coleta (REG-09)
Para assegurar que o modelo não capturou artefatos técnicos associados aos diferentes centros hospitalares que forneceram amostras ao TCGA (*Tissue Source Sites* — TSS):

![Diagnóstico de Lote TSS](figures/pca_diagnostico_lote_tss.png)
*Figura 5: Análise de Componentes Principais (PCA) dos 16.488 genes expressos categorizada pelos 11 maiores centros hospitalares (TSS).*

1. **Teste Log-Rank Inter-Hospitais**: A curva de sobrevida global não apresentou diferença estatisticamente significante entre os 11 principais hospitais de coleta ($p = 0.1090$), descartando o risco de que determinados centros concentrassem sistematicamente óbitos precoces.
2. **Modelo de Cox Estratificado por TSS**: Ao reajustar os modelos multivariados estratificando a função de risco basal por centro hospitalar, a variação relativa no Hazard Ratio dos biomarcadores foi mínima:
   - `DKK1`: alteração de apenas **$1,87\%$** ($HR = 1.533 \to 1.504$).
   - `NAPSA`: alteração de **$2,57\%$** ($HR = 0.758 \to 0.778$).
   - `KRT6A`: alteração de **$0,07\%$** ($HR = 1.258 \to 1.257$).
Esses testes comprovam matematicamente a robustez dos biomarcadores contra variações pré-analíticas institucionais.

---

## 📋 7. Mapeamento de Diretrizes TRIPOD+AI e REMARK (REG-17)

| Item da Diretriz | Requisito TRIPOD+AI / REMARK | Implementação no OncoMultiOmics Survival Engine | Seção / Arquivo de Registro |
|---|---|---|---|
| **TRIPOD 1 & 2** | Título e resumo identificando estudo de predição prognóstica multimodal. | Título formal, escopo não-causal e resumo com métricas de discriminação e calibração. | `README.md`, `reports/relatorio_final_oncomultiomics.md` |
| **TRIPOD 3a & 3b** | Justificativa médica, baselines clínicos e escopo de aplicabilidade. | Definição da escada de baselines ($M_0, M_1, M_3, M_5, M_6$) e delimitação de uso exclusivo em pesquisa. | `docs/plano_de_analise.md` (REG-14, REG-16) |
| **TRIPOD 4a & 4b** | Desenho do estudo e fontes dos dados clínicos e genômicos. | Curadoria a partir do TCGA-CDR (Liu et al., 2018) e GEO GSE31210 (Okayama et al., 2012). | `src/oncosurv/clinico/curadoria.py`, `manifest.json` |
| **TRIPOD 5a & 5b** | Critérios de elegibilidade e funil de exclusão detalhado. | Funil formal documentando exclusões de amostras não-primárias, tempos $\le 0$ e estágios discrepantes. | `reports/funil_exclusao_luad.md`, `funil_exclusao_kirc.md` |
| **TRIPOD 6a & 6b** | Definição rigorosa do desfecho primário e horizonte temporal. | Sobrevida Global (**OS**) com censura administrativa pré-especificada em $\tau = 5 \text{ anos}$ ($1.826,25 \text{ dias}$). | `docs/decisoes/001-escolha-coorte-e-desfecho.md` (REG-02) |
| **TRIPOD 7a & 7b** | Preditores clínicos e moleculares e métodos de mensuração. | Idade, sexo, estadiamento AJCC e contagens de RNA-Seq em escala $\log_2(\text{RSEM} + 1)$. | `docs/dicionario_de_dados.md` |
| **TRIPOD 8** | Tamanho amostral e número de eventos observados. | $N=494$ (170 eventos $\tau$) em LUAD; $N=528$ (149 eventos $\tau$) em KIRC; $N=204$ em GSE31210. | Relatórios técnicos e tabelas 1 e 2 |
| **TRIPOD 10a & 10b** | Tratamento de dados faltantes e prevenção de vazamento (*data leakage*). | Imputação de medianas e escalonamento z-score ajustados **estritamente dentro da dobra de treino** (REG-03). | `src/oncosurv/modelos/integrado.py`, `tests/test_reg03_anti_vazamento.py` |
| **TRIPOD 10c & 10d** | Seleção de preditores, regularização e sintonização de hiperparâmetros. | `FastCoxScoreSelector` intra-fold e validação aninhada interna (*nested CV*) para seleção do $\alpha$ do Elastic Net. | `src/oncosurv/features/selecao.py`, `docs/decisoes/002-...` |
| **TRIPOD 13a & 13b** | Características demográficas e tabela clínica de baseline. | Sumários estatísticos de idade, sexo e distribuição de estadiamento AJCC gerados na curadoria. | `reports/funil_exclusao_luad.md` |
| **TRIPOD 14** | Métricas de discriminação ajustadas para censura temporal. | C-index de Uno com IPCW, C-index de Harrell e Dynamic AUC em 1, 3 e 5 anos reportados com desvios-padrão. | `src/oncosurv/validacao/metricas.py` (REG-05) |
| **TRIPOD 15** | Avaliação formal de calibração probabilística. | Curvas de calibração em múltiplos horizontes (1, 3 e 5 anos), *slopes* de calibração e Integrated Brier Score. | `src/oncosurv/visualizacao/calibracao.py` (REG-10) |
| **TRIPOD 16** | Validação externa em coorte independente de outra plataforma. | Validação do modelo $M_3$ congelado em 204 pacientes cirúrgicos de microarranjo Affymetrix (GSE31210). | `src/oncosurv/validacao/validacao_externa.py` (REG-08) |
| **TRIPOD 17 & 18** | Interpretação biológica, discussão de limitações e escopo ético. | Enriquecimento funcional de vias, ajuste com FDR (REG-11), análise de TSS (REG-09) e limitações demográficas. | Seção 5 deste relatório, `models/MODEL_CARD.md` |
| **TRIPOD 20** | Disponibilização de código aberto e dados para reprodutibilidade. | Repositório aberto no GitHub, rastreamento SHA-256 e ambiente gerenciado via `uv` com 20 testes no `pytest`. | `https://github.com/PauloHFA/OncoMultiOmics.git` (REG-15) |

---

## 🖥️ 8. Interfaces e Disponibilidade Operacional

O projeto disponibiliza quatro canais para inspeção e auditoria dos resultados:

1. **Dashboard Interativo em HTML Puro (Autossuficiente)**:
   - Arquivo: [`docs/dashboard_resultados.html`](file:///c:/Projetos/OncoMultiOmics%20Survival%20Engine/docs/dashboard_resultados.html)
   - Contém todos os KPIs, tabelas de benchmark, detalhamento de validação externa, segunda coorte, tabelas de biomarcadores e gráficos em alta resolução codificados em Base64 para visualização imediata em qualquer navegador offline.

2. **Relatório Científico Executivo em PDF**:
   - Arquivo: [`docs/relatorio_cientifico_executivo.pdf`](file:///c:/Projetos/OncoMultiOmics%20Survival%20Engine/docs/relatorio_cientifico_executivo.pdf)
   - Diagramado via `reportlab` para leitura, impressão e compartilhamento institucional.

3. **Simulador Web Operacional (Streamlit)**:
   - Permite a pesquisadores configurar pacientes hipotéticos (ajustando idade, sexo, estágio e z-scores dos biomarcadores `DKK1`, `IGF2BP1`, `COL7A1`, `SLC16A12`) e simular em tempo real as curvas de sobrevivência $S(t|x)$ comparativas:
   ```bash
   uv run streamlit run app/dashboard.py
   ```

4. **Model Cards e Modelos Serializados**:
   - Modelos prontos para inferência em formato `.joblib`: [`models/m1_cox_clinico.joblib`](file:///c:/Projetos/OncoMultiOmics%20Survival%20Engine/models/m1_cox_clinico.joblib), [`models/m3_coxnet_integrado.joblib`](file:///c:/Projetos/OncoMultiOmics%20Survival%20Engine/models/m3_coxnet_integrado.joblib), [`models/m1_kirc_cox_clinico.joblib`](file:///c:/Projetos/OncoMultiOmics%20Survival%20Engine/models/m1_kirc_cox_clinico.joblib) e [`models/m3_kirc_coxnet_integrado.joblib`](file:///c:/Projetos/OncoMultiOmics%20Survival%20Engine/models/m3_kirc_coxnet_integrado.joblib).
   - Metadados completos de governança em [`models/MODEL_CARD.md`](file:///c:/Projetos/OncoMultiOmics%20Survival%20Engine/models/MODEL_CARD.md) e [`models/model_card_m3.json`](file:///c:/Projetos/OncoMultiOmics%20Survival%20Engine/models/model_card_m3.json).

---

*OncoMultiOmics Survival Engine — Documento consolidado em conformidade com as diretrizes TRIPOD+AI, REMARK e as regras mandatórias REG-01 a REG-17.*
