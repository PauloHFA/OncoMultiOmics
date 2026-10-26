# OncoMultiOmics Survival Engine

> **Predição de prognóstico e sobrevivência oncológica por Machine Learning de Sobrevivência, integrando dados clínicos e expressão gênica (RNA-Seq) sob estrito rigor científico e reprodutibilidade.**

[![Tests](https://img.shields.io/badge/pytest-20%20passed-brightgreen.svg)](tests/)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](pyproject.toml)
[![Standard](https://img.shields.io/badge/guidelines-TRIPOD%2BAI%20%7C%20REMARK-orange.svg)](docs/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

---

## 🔬 Visão Geral

O **OncoMultiOmics Survival Engine** investiga se a adição de perfis moleculares de transcriptoma (RNA-Seq) melhora de forma estatisticamente significante a predição da curva de sobrevivência em pacientes com câncer em comparação com modelos baseados exclusivamente em variáveis clínicas diagnósticas (idade, sexo, estadiamento patológico AJCC).

O projeto é estruturado conforme as diretrizes internacionais **TRIPOD+AI** (*Transparent Reporting of a multivariable prediction model of an Individual Prognosis Or Diagnosis*) e **REMARK** (*Reporting Recommendations for Tumor Marker Prognostic Studies*), incorporando 17 regras mandatórias de rigor científico (REG-01 a REG-17).

---

## 📁 Estrutura do Repositório

```text
OncoMultiOmics Survival Engine/
├── pyproject.toml                     # Gerenciamento de dependências travadas via uv (Python 3.11)
├── README.md
├── app/
│   └── dashboard.py                   # Dashboard interativo de pesquisa em Streamlit (Item 3)
├── docs/
│   ├── plano_de_analise.md            # Pré-registro formal de hipóteses, coorte, desfecho e tau (REG-02, REG-14)
│   ├── dicionario_de_dados.md         # Dicionário de dados, origem e codificação clínica e molecular
│   └── decisoes/                      # Architecture Decision Records (ADRs 001 a 009)
│       ├── 001-escolha-coorte-e-desfecho.md
│       ├── 002-prevencao-vazamento-intra-fold.md
│       ├── 003-avaliacao-modelos-lineares-vs-nao-lineares.md
│       ├── 004-ajuste-clinico-fdr-e-vias-moleculares.md
│       ├── 005-validacao-externa-gse31210.md
│       ├── 006-diagnostico-de-lote-e-tss.md
│       ├── 007-calibracao-probabilistica-e-nomograma.md
│       ├── 008-extensao-coorte-kirc.md
│       └── 009-dashboard-interativo-pesquisa.md
├── models/                            # Modelos treinados, serializados e Model Cards (Item 1)
│   ├── m1_cox_clinico.joblib          # M1 Clínico LUAD
│   ├── m3_coxnet_integrado.joblib     # M3 Integrado LUAD
│   ├── m1_kirc_cox_clinico.joblib     # M1 Clínico KIRC
│   ├── m3_kirc_coxnet_integrado.joblib# M3 Integrado KIRC
│   ├── model_card_m3.json             # Model Card estruturado LUAD
│   ├── model_card_kirc_m3.json        # Model Card estruturado KIRC
│   ├── MODEL_CARD.md                  # Especificação humana de governança algorítmica
│   └── dependencies.json              # Versões travadas das bibliotecas centrais
├── data/
│   ├── raw/                           # Dados brutos imutáveis e versionados por hash SHA-256 (manifest.json)
│   ├── interim/                       # Base clínica curada e matriz de RNA-Seq pré-processada (LUAD e KIRC)
│   └── external/                      # Coorte independente de validação (GSE31210)
├── src/oncosurv/
│   ├── ingestao/                      # Download versionado e verificação de integridade (SHA-256)
│   ├── clinico/                       # Curadoria, funil de exclusão (LUAD e KIRC) e seguimento via KM Reverso
│   ├── expressao/                     # Filtragem não-supervisionada de genes expressos
│   ├── features/                      # Seleção supervisionada univariada intra-fold (anti-vazamento)
│   ├── modelos/                       # M0 (Kaplan-Meier), M1 (Cox Clínico), M3 (Coxnet), M5 (RSF), M6 (GBoost)
│   ├── explicabilidade/               # Cox multivariado com FDR (REG-11) e enriquecimento de vias moleculares
│   ├── validacao/                     # CV 5x5 repetida, Uno IPCW C-index, Dynamic AUC, IBS, KIRC benchmark
│   └── visualizacao/                  # Curvas KM, calibração em múltiplos horizontes e nomograma de pesos
├── tests/                             # 20 testes automatizados com pytest (REG-01 a REG-17, KIRC e UI)
└── reports/                           # Relatórios técnicos, tabelas comparativas e figuras científicas
    ├── figures/                       # Figuras em alta resolução (300 DPI)
    ├── funil_exclusao_luad.md         # Funil de elegibilidade TCGA-LUAD
    ├── funil_exclusao_kirc.md         # Funil de elegibilidade TCGA-KIRC
    ├── relatorio_final_oncomultiomics.md # Relatório científico consolidado de LUAD
    └── relatorio_kirc_segunda_coorte.md  # Relatório científico de TCGA-KIRC
```

---

## 📊 Principais Resultados do Estudo

### 1. Descoberta Interna: TCGA-LUAD (25 dobras repetidas 5×5)
- **Coorte Elegível (REG-01)**: 494 pacientes únicos com tumor sólido primário (`01`) e RNA-Seq alinhado.
- **Desfecho Primário (REG-02)**: Sobrevida Global (**OS**) com horizonte temporal administrativo $\tau = 5 \text{ anos}$ ($1.826,25 \text{ dias}$).
- **Seguimento Mediano (KM Reverso)**: 2,41 anos (882 dias).
- **Desempenho na Validação Cruzada 5×5 (25 dobras)**:
  - **M0 (Kaplan-Meier Nulo)**: $C_{\text{Uno}} = 0,5000$ | $\text{IBS} = 0,1865$
  - **M1 (Cox Clínico Baseline)**: $C_{\text{Uno}} = 0,6359$ (IC 95%: $[0,5517, 0,7099]$) | $\text{Dynamic AUC Médio} = 0,6821$ | $\text{IBS} = 0,1730$
  - **M3 (Cox Integrado Clínico + RNA-Seq)**: $C_{\text{Uno}} = 0,6366$ | $\text{IBS} = 0,1721$
  - **M5 (Random Survival Forest)**: $C_{\text{Uno}} = 0,5958$ | $\text{IBS} = 0,1796$
  - **M6 (Gradient Boosting Survival)**: $C_{\text{Uno}} = 0,6272$ | $\text{IBS} = 0,1758$
- **Veredito H2**: Modelos lineares penalizados superam ensembles de árvores na escala amostral do TCGA ($N \approx 500, p \gg n$).

### 2. Validação Externa Independente: GSE31210 / NCBI GEO (REG-08, Q3, H3)
- **Coorte Externa Independente**: 204 pacientes de adenocarcinoma pulmonar em plataforma distinta (Affymetrix HG-U133_Plus_2).
- **Desempenho com Modelo e Ponto de Corte Congelados**:
  - **M1 (Cox Clínico no GSE31210)**: $C_{\text{Uno}} = 0,5132$ (perda acentuada pelo espectro restrito a estágios I e II).
  - **M3 (Cox Integrado no GSE31210)**: **$C_{\text{Uno}} = 0,6364$** (perda de desempenho interna vs. externa quase nula: $\text{Perda} = 0,0002$).
  - **Valor Incremental Molecular Externo**: **$\Delta C_{\text{Uno}} = +0,1232$** (+12,3 pontos percentuais de ganho preditivo).
  - **Estratificação Externa por Corte Congelado**: Teste Log-Rank **$p = 0,0072$** ($p < 0,01$).

### 3. Segunda Coorte: TCGA-KIRC (Carcinoma Renal de Células Claras) (Item 2)
- **Coorte Elegível (REG-01, REG-02)**: 528 pacientes com amostra sólida primária (`01`), 149 óbitos no horizonte $\tau = 5 \text{ anos}$ ($28,2\%$), seguimento mediano de 4,61 anos.
- **Desempenho em 25 Dobras Repetidas (5×5)**:
  - **M0 (Nulo KM)**: $C_{\text{Uno}} = 0,5000$ | $\text{IBS} = 0,1511$
  - **M1 (Cox Clínico)**: $C_{\text{Uno}} = 0,7260$ (±0,0482) | $\text{Dynamic AUC 5a} = 0,7202$ | $\text{IBS} = 0,1275$
  - **M3 (Cox Net Integrado)**: **$C_{\text{Uno}} = 0,7493$** (±0,0442) | **$\text{Dynamic AUC 5a} = 0,7624$** | **$\text{IBS} = 0,1230$**
  - **Ganho Incremental Molecular**: **$\Delta C_{\text{Uno}} = +0,0233$** (Wilcoxon pareado $p = 6,37 \times 10^{-5}$, teste t $p = 2,91 \times 10^{-5}$).
  - **Separação de Risco Kaplan-Meier**: $\chi^2 = 16,85$ ($p = 4,03 \times 10^{-5}$).
  - **Biomarcadores Tier 1 (FDR $q < 10^{-4}$)**: `COL7A1` ($HR = 1,592$), `SLC16A12` ($HR = 0,665$), `IGFN1` ($HR = 1,414$), `SLC10A2` ($HR = 0,678$).

### 4. Biomarcadores Estáveis e Vias em LUAD (REG-11, Q4)
- **Genes Tier 1 (Alta Credibilidade, FDR $q < 0,02$)**:
  - Risco Desfavorável: `DKK1` ($HR = 1,533$, via Wnt), `IGF2BP1` ($HR = 1,353$), `ABCC2` ($HR = 1,296$), queratinas `KRT6A/B/C`.
  - Diferenciação Funcional Protetora: `SFTA3` ($HR = 0,738$), `NAPSA` ($HR = 0,758$), `SFTPB` ($HR = 0,774$), `CACNA2D2` ($HR = 0,776$).
- **Vias Enriquecidas (Hallmark)**: *Xenobiotic Metabolism* ($q = 0,025$) e *Wnt-beta Catenin Signaling* ($p = 0,021$).

### 5. Calibração Probabilística e Nomograma (REG-05)
- **Inclinações de Calibração (*Slope*)**: $0,99$ aos 12 meses (erro absoluto médio de $2,8\%$), $0,82$ aos 36 meses ($4,4\%$) e $0,87$ aos 60 meses.
- **Visualização de Pesos**: Nomograma horizontal decompondo coeficientes clínicos e transcricionais não-nulos.

---

## 🖥️ Dashboard Interativo de Pesquisa (Item 3)

O motor conta com uma interface de simulação web em **Streamlit** para exploração interativa de predições individuais, decomposição linear de biomarcadores e governança algorítmica:

```bash
uv run streamlit run app/dashboard.py
```

### Funcionalidades do Dashboard:
1. **Seletor Multi-Coorte**: Alternância dinâmica entre TCGA-LUAD e TCGA-KIRC.
2. **Sliders Clínicos e Genômicos**: Ajuste de Idade, Sexo, Estádio Patológico e z-scores dos principais biomarcadores de risco (`DKK1`, `IGF2BP1`, `COL7A1`, `IGFN1`) e proteção (`NAPSA`, `SFTPB`, `SLC16A12`, `HMGCS2`).
3. **Simulador de Curva de Sobrevida**: Projeção em tempo real de $S(t | x)$ ao longo de 5 anos, comparando a estimativa puramente clínica ($M_1$) com a estimativa molecular integrada ($M_3$), com probabilidades pontuais em 1, 3 e 5 anos.
4. **Decomposição Linear de Contribuição**: Gráfico de barras horizontal demonstrando a contribuição exata de cada gene e covariável clínica no log-hazard individual.
5. **Painel TRIPOD+AI & Model Card**: Visualização de métricas de 25 dobras, curvas Kaplan-Meier e metadados de governança.

---

## 🚀 Como Reproduzir o Pipeline Completo

### 1. Instalar dependências com `uv`
```bash
uv sync
```

### 2. Executar a suíte de testes automatizados (20 testes)
```bash
uv run pytest tests
```

### 3. Executar Curadoria e Modelagem
```bash
# Curadoria clínica e pré-processamento de TCGA-LUAD
uv run python -m oncosurv.clinico.curadoria
uv run python -m oncosurv.expressao.processamento

# Benchmark e comparação 5x5 CV em TCGA-LUAD
uv run python -m oncosurv.validacao.comparacao

# Validação Externa Independente em GSE31210
uv run python -m oncosurv.validacao.validacao_externa

# Curadoria e Validação da Segunda Coorte (TCGA-KIRC)
uv run python -m oncosurv.clinico.curadoria_kirc
uv run python -m oncosurv.validacao.kirc_validation

# Exportação e Serialização dos Modelos e Model Cards
uv run python -m oncosurv.modelos.export

# Inicialização do Dashboard
uv run streamlit run app/dashboard.py
```

---

## ⚖️ Conformidade e Aviso Legal (REG-16)

> **USO EXCLUSIVO EM PESQUISA (RESEARCH USE ONLY — RUO)**:  
> Este repositório e os modelos preditivos aqui desenvolvidos destinam-se exclusivamente à pesquisa acadêmica, translacional e científica. **NÃO CONSTITUEM DISPOSITIVO MÉDICO**, não possuem aprovação de agências regulatórias de saúde (ANVISA, FDA ou EMA) e não devem ser utilizados para diagnóstico, estadiamento ou prescrição terapêutica em pacientes humanos. Conforme prescrito pela REG-16, todas as associações entre expressão gênica e sobrevida reportadas refletem correlações estatísticas prognósticas observadas em dados retrospectivos, não implicando relações de causa e efeito mecanicistas diretas sem prévia validação experimental perturbativa.
