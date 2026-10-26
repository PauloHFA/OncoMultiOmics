# OncoMultiOmics Survival Engine

> **Motor de Machine Learning de Sobrevivência Multimodal integrando dados clínicos e perfis transcriptômicos (RNA-Seq) sob estrito rigor científico, governança algorítmica e reprodutibilidade integral (TRIPOD+AI e REMARK).**

[![Tests](https://img.shields.io/badge/pytest-20%20passed-brightgreen.svg)](tests/)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](pyproject.toml)
[![Standard](https://img.shields.io/badge/guidelines-TRIPOD%2BAI%20%7C%20REMARK-orange.svg)](docs/)
[![Rules](https://img.shields.io/badge/rules-REG--01%20to%20REG--17-success.svg)](docs/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

---

## 🔬 1. Visão Geral e Pergunta Central de Pesquisa

A oncologia de precisão enfrenta uma questão metodológica fundamental:  
> **A adição de perfis moleculares de larga escala (RNA-Seq) agrega capacidade preditiva clinicamente relevante além do que variáveis clínicas convencionais e de baixo custo (idade, sexo e estadiamento patológico AJCC) já fornecem?**

Muitas assinaturas prognósticas reportadas na literatura sofrem de **vazamento de dados (*data leakage*)**, ausência de modelo clínico de referência (*baseline M1*), falta de censura administrativa em horizontes pré-especificados ($\tau$) e sobreajuste em amostras pequenas com alta dimensionalidade ($p \gg n$).

O **OncoMultiOmics Survival Engine** foi desenvolvido para responder a essa pergunta com o mais alto padrão de rigor científico. O projeto implementa um pipeline completo de Machine Learning de Sobrevivência, guiado por **17 regras mandatórias (REG-01 a REG-17)** em total conformidade com as diretrizes internacionais **TRIPOD+AI** e **REMARK**.

---

## 📋 2. As 17 Regras Mandatórias de Rigor Científico (REG-01 a REG-17)

| Regra | Nome / Descrição | Implementação no Projeto |
|---|---|---|
| **REG-01** | **Amostra Única por Paciente** | Filtro estrito de 1 alíquota de tecido sólido primário (código `'01'`) por paciente, descartando tecidos normais (`'11'`) e recidivas (`'02'`). |
| **REG-02** | **Censura Administrativa no Horizonte $\tau$** | Desfecho primário de Sobrevida Global (OS) truncado estritamente em $\tau = 5 \text{ anos}$ ($1.826,25 \text{ dias}$). |
| **REG-03** | **Anti-Vazamento Estrito (*No Leakage*)** | Todas as seleções de genes, imputações de medianas e escalonamentos z-score ocorrem **estritamente dentro da dobra de treino** da validação cruzada. |
| **REG-04** | **Escada Incremental de Baselines** | Avaliação sistemática de $M_0$ (Nulo KM), $M_1$ (Cox Clínico), $M_3$ (Coxnet Integrado), $M_5$ (RSF) e $M_6$ (Gradient Boosting). |
| **REG-05** | **Painel Abrangente de Métricas** | C-index de Uno (IPCW no horizonte $\tau$), C-index de Harrell, Integrated Brier Score (IBS) e Dynamic AUC (1, 3 e 5 anos). |
| **REG-06** | **Validação Cruzada Repetida (5×5)** | Amostragem em 25 dobras estratificadas por evento de óbito ($5 \times 5 \text{ Repeated Stratified CV}$) para garantir estabilidade. |
| **REG-07** | **Testes Estatísticos Pareados** | Teste de postos sinalizados de Wilcoxon e teste t de Student pareado para comparação formal entre $M_1$ e $M_3$. |
| **REG-08** | **Validação Externa com Modelo Congelado** | Avaliação em coorte independente (GSE31210 / Microarray Affymetrix) sem recalibração de pesos ou ponto de corte. |
| **REG-09** | **Diagnóstico de Efeitos de Lote (TSS)** | Análise de componentes principais (PCA) e modelos de Cox estratificados por centro hospitalar de coleta (TSS) para descartar viés técnico. |
| **REG-10** | **Avaliação Contínua de Calibração** | Curvas de calibração em múltiplos horizontes (12, 36 e 60 meses), *slopes* de calibração e Índice de Calibração Integrada (ICI). |
| **REG-11** | **Ajuste Clínico com Controle de FDR** | Cox multivariado ajustado por idade, sexo e estágio patológico com correção de Benjamini-Hochberg (FDR $q$-valor) nos biomarcadores. |
| **REG-12** | **Ponto de Corte Pré-Especificado no Treino** | Limiar de alto vs baixo risco definido exclusivamente pela mediana do conjunto de treino e aplicado cegamente ao teste. |
| **REG-13** | **Funil de Exclusão Detalhado** | Rastreabilidade numérica e justificativa formal para cada paciente excluído em tabelas Markdown e JSON. |
| **REG-14** | **Pré-Registro Formal de Hipóteses** | Documentação a priori de H1, H2 e H3 no plano de análise antes da modelagem preditiva (`docs/plano_de_analise.md`). |
| **REG-15** | **Reprodutibilidade Computacional Integral** | Ambiente Python gerenciado via `uv`, sementes pseudoaleatórias fixadas e dados brutos versionados com hash SHA-256. |
| **REG-16** | **Linguagem Não-Causal e Escopo Ético** | Caracterização como ferramenta de uso exclusivo em pesquisa científica (RUO), sem alegações causais determinísticas infundadas. |
| **REG-17** | **Checklist TRIPOD+AI e REMARK** | Mapeamento completo dos 20 itens de transparência metodológica e governança de inteligência artificial biomédica. |

---

## 🗄️ 3. Bases de Dados Utilizadas

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BASES DE DADOS E COORTES                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. TCGA-LUAD (Adenocarcinoma Pulmonar — Coorte de Descoberta):              │
│    • Fonte Clínica: TCGA-CDR (Liu et al., Cell 2018) — Supplemental Table S1│
│    • Fonte Genômica: Illumina HiSeqV2 (16.488 genes expressos mantidos)     │
│    • População Curada: N = 494 pacientes primários ('01'), 170 óbitos       │
│    • Seguimento Mediano (KM Reverso): 2,41 anos (882 dias)                  │
│    • Integridade Criptográfica: SHA-256 registrado em data/raw/manifest.json│
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. GSE31210 (Validação Externa Independente — NCBI GEO):                    │
│    • População: N = 204 pacientes cirúrgicos em Estágios Iniciais I e II    │
│    • Plataforma Tecnológica: Microarranjo Affymetrix HG-U133 Plus 2.0       │
│    • Objetivo: Validação de generalização trans-plataforma e modelo congelado│
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. TCGA-KIRC (Carcinoma Renal de Células Claras — Segunda Coorte):          │
│    • Fonte Clínica: TCGA-CDR cruzado com RNA-Seq Illumina HiSeqV2           │
│    • População Curada: N = 528 pacientes primários ('01'), 149 óbitos       │
│    • Seguimento Mediano (KM Reverso): 4,61 anos (1.684,5 dias)              │
│    • Objetivo: Comprovar a generalizabilidade da arquitetura multineoplásica│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ 4. Stack Tecnológica e Arquitetura de Software

O ecossistema foi construído sobre uma arquitetura modular, tipada e com testes automatizados:

```text
OncoMultiOmics Survival Engine/
├── pyproject.toml                     # Metadados e dependências travadas via uv
├── uv.lock                            # Lockfile determinístico multiplataforma
├── README.md                          # Guia mestre do repositório
├── app/
│   └── dashboard.py                   # Simulador Web Interativo em Streamlit
├── docs/                              # Documentação científica e arquitetural
│   ├── dashboard_resultados.html      # Dashboard executivo visual em HTML puro (Base64)
│   ├── relatorio_geral_resultados.md  # Relatório científico consolidado com figuras
│   ├── plano_de_analise.md            # Pré-registro formal de hipóteses (REG-14)
│   ├── dicionario_de_dados.md         # Dicionário de covariáveis e expressões
│   ├── figures/                       # Galeria de figuras em alta resolução (300 DPI)
│   └── decisoes/                      # Architecture Decision Records (ADRs 001 a 009)
├── models/                            # Modelos treinados serializados (.joblib) e Model Cards
│   ├── m1_cox_clinico.joblib          # Baseline Clínico LUAD
│   ├── m3_coxnet_integrado.joblib     # Modelo Integrado Cox Elastic Net LUAD
│   ├── m1_kirc_cox_clinico.joblib     # Baseline Clínico KIRC
│   ├── m3_kirc_coxnet_integrado.joblib# Modelo Integrado Cox Elastic Net KIRC
│   ├── model_card_m3.json             # Model Card estruturado (Mitchell et al.)
│   ├── MODEL_CARD.md                  # Especificação humana de governança
│   └── dependencies.json              # Registro de versões de bibliotecas centrais
├── src/oncosurv/                      # Pacote Python de engenharia biomédica
│   ├── clinico/                       # Curadoria clínica, funil de exclusão e KM Reverso
│   ├── expressao/                     # Filtragem não-supervisionada de RNA-Seq
│   ├── features/                      # Seleção supervisionada univariada intra-fold
│   ├── modelos/                       # M0, M1, M3, M5 (RSF), M6 (GBoost) e exportação
│   ├── explicabilidade/               # Cox multivariado com FDR (REG-11) e vias MSigDB
│   ├── validacao/                     # CV 5x5 repetida, C-Uno IPCW, IBS e Dynamic AUC
│   └── visualizacao/                  # Curvas KM, calibração multi-horizontes e nomograma
├── tests/                             # 20 testes automatizados no pytest
└── reports/                           # Relatórios comparativos, funis e figuras
```

### Principais Bibliotecas e suas Funções:
- **`scikit-survival`** (Pölsterl, JMLR 2020): `CoxnetSurvivalAnalysis` (Elastic Net com regularização $L_1/L_2$), `RandomSurvivalForest`, `GradientBoostingSurvivalAnalysis`, `concordance_index_ipcw` e `integrated_brier_score`.
- **`lifelines`** (Davidson-Pilon): `KaplanMeierFitter` (curvas e seguimento reverso), `logrank_test` e `CoxPHFitter` (modelos multivariados com IC 95%).
- **`scikit-learn`**: `RepeatedStratifiedKFold`, `StandardScaler`, `SimpleImputer` e validação aninhada interna (*nested CV*) para seleção do $\alpha$.
- **`numpy` & `scipy.stats`**: Vetorização de alta performance do teste de score de Cox (`FastCoxScoreSelector` em $O(n \log n)$ com somas cumulativas) e testes pareados de Wilcoxon.
- **`statsmodels`**: Controle de taxa de falsa descoberta (FDR) via algoritmo de Benjamini-Hochberg.
- **`gseapy`**: Análise de enriquecimento funcional contra bancos MSigDB Hallmark e KEGG.
- **`streamlit`**: Simulador web dinâmico para predição individualizada de curvas $S(t|x)$.

---

## 📊 5. Métricas de Avaliação Explicadas

A análise de sobrevivência com censura requer métricas específicas:

1. **C-index de Uno com IPCW (Ponderação pelo Inverso da Probabilidade de Censura)**:  
   O C-index clássico de Harrell sofre de viés quando a censura depende do tempo. O estimador de Uno ($C_{\text{Uno}}$) pondera cada par de pacientes pelo inverso do quadrado da probabilidade de censura $[G(t)]^2$ estimada marginalmente. Mede a proporção de pares concordantes estritamente até o horizonte $\tau = 5 \text{ anos}$ ($0.50$ = acaso; $1.00$ = perfeição).
2. **Integrated Brier Score (IBS)**:  
   Mede a acurácia das probabilidades de sobrevida integrando o erro quadrático médio entre a probabilidade estimada $\widehat{S}(t|x)$ e o status real de evento de 0 a $\tau = 5 \text{ anos}$. Valores menores indicam modelos melhor calibrados.
3. **Dynamic Cumulative AUC**:  
   Quantifica a capacidade de classificar pacientes que sofrerão o evento antes de um horizonte específico (1, 3 ou 5 anos) versus aqueles que sobreviverão além dele.
4. **Inclinação de Calibração (*Slope*) e ICI**:  
   Mede se o modelo superestima (*slope* $< 1.0$) ou subestima (*slope* $> 1.0$) os riscos reais. O Índice de Calibração Integrada (ICI) expressa o erro absoluto médio entre a probabilidade prevista e a observada.

---

## 📈 6. Principais Resultados e Discussão Científica

### A. TCGA-LUAD (25 Dobras Repetidas 5×5)

| Modelo | Estrutura Algorítmica | $C_{\text{Uno}}$ (±DP) | $C_{\text{Harrell}}$ | Dynamic AUC Médio | Integrated Brier Score (IBS) |
|---|---|---|---|---|---|
| **$M_0$** | Kaplan-Meier Nulo Marginal | 0.5000 | 0.5000 | 0.5000 | 0.1865 |
| **$M_1$** | Cox PH Clínico (Idade, Sexo, Estágio) | 0.6359 (±0.0401) | 0.6754 | 0.6821 | 0.1730 (±0.0125) |
| **$M_3$** | Cox Elastic Net Integrado | **0.6366** (±0.0404) | **0.6767** | **0.6838** | **0.1721** (±0.0123) |
| **$M_5$** | Random Survival Forest (RSF) | 0.5958 (±0.0441) | 0.6412 | 0.6542 | 0.1796 (±0.0134) |
| **$M_6$** | Gradient Boosting Survival | 0.6272 (±0.0389) | 0.6685 | 0.6710 | 0.1758 (±0.0129) |

- **Veredito H1 no LUAD Geral**: Na coorte global contendo estágios I a IV misturados, o estadiamento patológico AJCC é extremamente dominante ($p = 1.14 \times 10^{-12}$), deixando margem linear modesta para a transcriptômica em nível populacional amplo.
- **Veredito H2 (Confirmada)**: Modelos lineares penalizados com restrição esparsa superaram amplamente ensembles de árvores (RSF e Boosting), comprovando menor sobreajuste no regime $p \gg n$.

---

### B. O Fenômeno do Resgate Molecular na Validação Externa (GSE31210 / H3)

Na coorte cirúrgica independente GSE31210 ($N=204$), restrita a pacientes com tumores ressecados em **Estágios I e II**:

| Métrica | $M_1$ (Cox Clínico) | $M_3$ (Integrado Congelado) | Ganho Incremental Molecular ($\Delta$) |
|---|---|---|---|
| **C-index de Uno (IPCW)** | 0.5132 | **0.6364** | **+0.1232 (+12.3%)** |
| **C-index de Harrell** | 0.5310 | **0.6592** | **+0.1282 (+12.8%)** |
| **Estratificação Log-Rank** | $p = 0.4120$ (Falhou) | **$p = 0.0072$** (Significante) | **Separação nítida de subgrupos** |

> **Significado Clínico**: Quando os tumores têm tamanho e estadiamento anatômico idênticos (todos são cirúrgicos I/II), a anatomia convencional perde o poder de estratificação ($C_{\text{Uno}} \approx 0.51$). Nesse momento, a biologia tumoral transcricional assume o protagonismo, resgatando a discriminação em mais de 12 pontos percentuais.  
> Além disso, a perda de generalização externa do modelo $M_3$ foi de apenas **$0.0002$** ($0.6366 \to 0.6364$), confirmando a **Hipótese H3**.

---

### C. Segunda Coorte: TCGA-KIRC (*Carcinoma Renal de Células Claras*)

No Carcinoma Renal de Células Claras ($N=528$, 149 eventos, seguimento mediano de $4,61 \text{ anos}$):

| Métrica | $M_1$ (Cox Clínico) | $M_3$ (Cox Net Integrado) | $\Delta$ Incremental | Teste Estatístico Pareado |
|---|---|---|---|---|
| **C-index de Uno (IPCW, $\tau=5a$)** | 0.7260 (±0.0482) | **0.7493** (±0.0442) | **+0.0233** | Wilcoxon $p = 6.37 \times 10^{-5}$ |
| **C-index de Harrell** | 0.7553 | **0.7727** | **+0.0174** | Teste t $p = 2.91 \times 10^{-5}$ |
| **Dynamic AUC (5 Anos)** | 0.7202 | **0.7624** | **+0.0422** | Forte ganho a longo prazo |
| **Integrated Brier Score (IBS)** | 0.1275 (±0.0100) | **0.1230** (±0.0122) | **-0.0045** | Redução do erro probabilístico |

O ganho molecular no câncer renal foi consistente em todas as 25 dobras ($p < 0.0001$), pois o KIRC é uma doença metabólica cuja agressividade se manifesta pela perda de transportadores de solutos funcionais do néfron.

---

### D. Principais Biomarcadores Tier 1 com FDR (REG-11)
Ajustados para idade, sexo e estágio patológico por regressão multivariada de Cox com correção de Benjamini-Hochberg:
- **`DKK1`** ($HR = 1.533$, FDR $q = 2.45 \times 10^{-6}$): Inibidor de Wnt associado a evasão imune e desdiferenciação epitelial no pulmão.
- **`NAPSA`** ($HR = 0.758$, FDR $q = 2.45 \times 10^{-3}$): Napsina A, marcador protetor de pneumócitos tipo II diferenciados.
- **`COL7A1`** ($HR = 1.592$, FDR $q = 2.16 \times 10^{-8}$): Colágeno VII promotor de quebra de membrana basal e invasão estromal no rim.
- **`SLC16A12`** ($HR = 0.665$, FDR $q = 9.15 \times 10^{-8}$): Transportador tubular de monocarboxilato indicando função néfrica preservada.

---

## 🖥️ 7. Como Explorar Visualmente e Executar o Projeto

### A. Dashboard Interativo em HTML Puro (Sem Dependências)
Basta abrir no navegador o arquivo [`docs/dashboard_resultados.html`](file:///c:/Projetos/OncoMultiOmics%20Survival%20Engine/docs/dashboard_resultados.html).  
Ele contém todas as 7 figuras codificadas em Base64, tabelas completas de métricas, abas de navegação e resumo das bases de dados sem depender de servidores ou conexão à internet.

### B. Simulador Interativo Web (Streamlit)
Para simular pacientes hipotéticos, ajustar sliders de biomarcadores e inspecionar a curva $S(t|x)$ em tempo real:
```bash
uv run streamlit run app/dashboard.py
```

### C. Executar a Suíte de Testes Automatizados (20 Testes)
```bash
uv run pytest tests
```
*Garante conformidade com REG-01, REG-02, REG-03 (anti-vazamento), calibração, validação externa, diagnósticos de lote e estabilidade do dashboard.*

### D. Reproduzir o Pipeline Completo do Zero
```bash
# 1. Curadoria clínica e processamento transcriptômico
uv run python -m oncosurv.clinico.curadoria
uv run python -m oncosurv.expressao.processamento

# 2. Benchmark 5x5 CV e validação externa de LUAD
uv run python -m oncosurv.validacao.comparacao
uv run python -m oncosurv.validacao.validacao_externa

# 3. Curadoria e validação da segunda coorte (TCGA-KIRC)
uv run python -m oncosurv.clinico.curadoria_kirc
uv run python -m oncosurv.validacao.kirc_validation

# 4. Exportação dos modelos serializados (.joblib) e Model Cards
uv run python -m oncosurv.modelos.export
```

---

## ⚖️ 8. Conformidade Ética e Aviso Legal (REG-16)

> **USO EXCLUSIVO EM PESQUISA CIENTÍFICA (RESEARCH USE ONLY — RUO)**:  
> Este repositório e os modelos computacionais desenvolvidos destinam-se exclusivamente à pesquisa acadêmica, translacional e científica. **NÃO CONSTITUEM DISPOSITIVO MÉDICO**, não possuem aprovação de agências regulatórias de saúde (ANVISA, FDA ou EMA) e não devem ser utilizados para diagnóstico, estadiamento ou prescrição terapêutica em pacientes humanos. Todas as associações entre expressão gênica e sobrevida reportadas refletem correlações estatísticas prognósticas observadas em dados retrospectivos, não implicando relações de causa e efeito mecanicistas diretas sem prévia validação experimental perturbativa (REG-16).
