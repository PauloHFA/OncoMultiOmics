# OncoMultiOmics Survival Engine

> **Predição de prognóstico e sobrevivência oncológica por Machine Learning de Sobrevivência, integrando dados clínicos e expressão gênica (RNA-Seq) sob estrito rigor científico e reprodutibilidade.**

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
├── docs/
│   ├── plano_de_analise.md            # Pré-registro formal de hipóteses, coorte, desfecho e tau (REG-02, REG-14)
│   ├── dicionario_de_dados.md         # Dicionário de dados, origem e codificação clínica e molecular
│   └── decisoes/                      # Architecture Decision Records (ADRs)
│       ├── 001-escolha-coorte-e-desfecho.md
│       └── 002-prevencao-vazamento-intra-fold.md
├── data/
│   ├── raw/                           # Dados brutos imutáveis e versionados por hash SHA-256 (manifest.json)
│   ├── interim/                       # Base clínica curada e matriz de RNA-Seq pré-processada
│   └── processed/
├── src/oncosurv/
│   ├── ingestao/                      # Download versionado e verificação de integridade (SHA-256)
│   ├── clinico/                       # Curadoria, funil de exclusão e cálculo de seguimento via KM Reverso
│   ├── expressao/                     # Filtragem não-supervisionada de genes expressos
│   ├── features/                      # Seleção supervisionada univariada intra-fold (anti-vazamento)
│   ├── modelos/                       # M0 (Kaplan-Meier), M1 (Cox Clínico), M3 (Coxnet Integrado)
│   └── validacao/                     # CV 5x5 repetida, Uno IPCW C-index, Dynamic AUC, IBS, Nadeau-Bengio
├── tests/                             # Testes automatizados com pytest (REG-01, REG-03)
└── reports/                           # Funil de exclusão, resumos de métricas e relatórios comparativos
```

---

## 📊 Principais Resultados do Estudo

### 1. Descoberta Interna (TCGA-LUAD, 25 dobras repetidas 5×5)
- **Coorte Elegível (REG-01)**: 494 pacientes únicos com tumor sólido primário (`01`) e RNA-Seq alinhado.
- **Desfecho Primário (REG-02)**: Sobrevida Global (**OS**) com horizonte temporal administrativo $\tau = 5 \text{ anos}$ ($1.826,25 \text{ dias}$).
- **Seguimento Mediano (KM Reverso)**: 2,41 anos (882 dias).
- **Desempenho na Validação Cruzada 5×5 (25 dobras)**:
  - **M0 (Kaplan-Meier Nulo)**: $C_{\text{Uno}} = 0,5000$ | $\text{IBS} = 0,1865$
  - **M1 (Cox Clínico Baseline)**: $C_{\text{Uno}} = 0,6359$ (IC 95%: $[0,5517, 0,7099]$) | $\text{Dynamic AUC Médio} = 0,6821$ | $\text{IBS} = 0,1730$
  - **M3 (Cox Integrado Clínico + RNA-Seq)**: $C_{\text{Uno}} = 0,6366$ | $\text{IBS} = 0,1721$
  - **M5 (Random Survival Forest)**: $C_{\text{Uno}} = 0,5958$ | $\text{IBS} = 0,1796$
  - **M6 (Gradient Boosting)**: $C_{\text{Uno}} = 0,6272$ | $\text{IBS} = 0,1758$
- **Veredito H2**: Modelos lineares penalizados superam ensembles de árvores na escala amostral do TCGA.

### 2. Validação Externa Independente (GSE31210 / NCBI GEO) (REG-08, Q3, H3)
- **Coorte Externa Independente**: 204 pacientes de adenocarcinoma pulmonar em plataforma distinta (Affymetrix HG-U133_Plus_2).
- **Desempenho com Modelo e Ponto de Corte Congelados**:
  - **M1 (Cox Clínico no GSE31210)**: $C_{\text{Uno}} = 0,5132$ (perda acentuada pelo espectro restrito a estágios I e II).
  - **M3 (Cox Integrado no GSE31210)**: **$C_{\text{Uno}} = 0,6364$** (perda de desempenho interna vs. externa quase nula: $\text{Perda} = 0,0002$).
  - **Valor Incremental Molecular Externo**: **$\Delta C_{\text{Uno}} = +0,1232$** (+12,3 pontos percentuais de ganho preditivo).
  - **Estratificação Externa por Corte Congelado**: Teste Log-Rank **$p = 0,0072$** ($p < 0,01$).

### 3. Biomarcadores Estáveis e Vias (REG-11, Q4)
- **Genes Tier 1 (Alta Credibilidade, FDR $q < 0,02$)**:
  - Risco Desfavorável: `DKK1` ($HR = 1,533$, via Wnt), `IGF2BP1` ($HR = 1,353$), `ABCC2` ($HR = 1,296$), queratinas `KRT6A/B/C`.
  - Diferenciação Funcional Protetora: `SFTA3` ($HR = 0,738$), `NAPSA` ($HR = 0,758$), `SFTPB` ($HR = 0,774$), `CACNA2D2` ($HR = 0,776$).
- **Vias Enriquecidas (Hallmark)**: *Xenobiotic Metabolism* ($q = 0,025$) e *Wnt-beta Catenin Signaling* ($p = 0,021$).

### 4. Diagnóstico de Lote e Análise de Sensibilidade a TSS (REG-09)
- **Associação TSS-Sobrevida**: Teste de log-rank nos 11 principais hospitais/centros ($p = 0,1090$, sem correlação espúria com tempo de evento).
- **Estabilidade dos Biomarcadores**: A variação do Hazard Ratio em modelo estratificado por TSS foi inferior a $4,5\%$ em todos os genes chave (`DKK1`: $1,87\%$, `NAPSA`: $2,57\%$, `KRT6A`: $0,07\%$).
- **Figura Diagnóstica**: `reports/figures/pca_diagnostico_lote_tss.png`.

### 5. Calibração Probabilística e Nomograma (REG-05)
- **Inclinações de Calibração (*Slope*)**: $0,99$ aos 12 meses (erro absoluto médio de $2,8\%$), $0,82$ aos 36 meses ($4,4\%$) e $0,87$ aos 60 meses.
- **Visualização de Pesos**: Nomograma horizontal decompondo coeficientes clínicos e transcricionais não-nulos.
- **Figuras**: `reports/figures/calibracao_multi_horizontes_m3.png` e `reports/figures/nomograma_pesos_m3.png`.

---

## 🚀 Como Executar

### 1. Instalar dependências com uv
```bash
uv sync
```

### 2. Executar os testes automatizados (REG-01, REG-03)
```bash
uv run pytest tests
```

### 3. Rodar o pipeline completo
```bash
# Ingestão e verificação de integridade
uv run python scripts/download_luad_data.py

# Curadoria clínica e funil de exclusão
uv run python -m oncosurv.clinico.curadoria

# Pré-processamento da expressão gênica
uv run python -m oncosurv.expressao.processamento

# Avaliação comparativa M1 vs M3
uv run python -m oncosurv.validacao.comparacao
```

