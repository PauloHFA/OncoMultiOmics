# 📋 Pendências e Próximos Passos — OncoMultiOmics Survival Engine

> Documento de governança algorítmica, status de homologação clínica e backlog de melhorias futuras do **OncoMultiOmics Survival Engine** per diretrizes **TRIPOD+AI** e **REMARK**.

---

## 🚀 1. Backlog de Melhorias Futuras (Propostas)

### 1.1 Integração de Mutações Somáticas (SNVs / InDels) e Variações de Número de Cópias (CNV)
- [ ] **Descrição:** Expandir o modelo além da transcriptômica (RNA-Seq), incorporando dados de mutações pontuais (*driver genes* como TP53, EGFR, KRAS em LUAD; VHL, PBRM1, BAP1 em KIRC) e amplificações/deleções de CNV (GISTIC2).
- [ ] **Justificativa:** Cria uma arquitetura genômica verdadeiramente pan-ômica, integrando variantes genéticas com assinaturas de expressão.
- [ ] **Impacto:** Alto (Aumento da fidelidade biológica do modelo).

### 1.2 Deploy em Nuvem Pública do Dashboard Interativo (Streamlit)
- [ ] **Descrição:** Disponibilizar o simulador interativo (`app/dashboard.py`) em plataforma gerenciada (ex: Hugging Face Spaces ou Streamlit Community Cloud) com proteção de autenticação e caching dos modelos `.joblib`.
- [ ] **Justificativa:** Facilita a demonstração interativa de curvas de sobrevivência e nomogramas dinâmicos para pesquisadores e revisores de periódicos.
- [ ] **Impacto:** Médio/Alto (Disseminação e acessibilidade científica).

### 1.3 Calibração Bayesiana de Incerteza (Survival Bayesian Ensembles)
- [ ] **Descrição:** Incorporar quantificação de incerteza preditiva em nível individual via processos gaussianos ou ensembles de Cox bayesianos para sinalizar predições com baixa confiança.
- [ ] **Justificativa:** Requisito emergente em sistemas de apoio à decisão clínica sob a extensão TRIPOD-Cluster.
- [ ] **Impacto:** Médio (Rigor estatístico adicional).

---

## ✅ 2. O que já está Concluído (Status Atual)

- **As 17 Regras de Rigor Científico (`REG-01` a `REG-17`):** 100% implementadas e validadas por testes automatizados (TRIPOD+AI e REMARK).
- **Curadoria Clínica & Desfecho:** Coortes TCGA-LUAD (N=494) e TCGA-KIRC (N=528) curadas com 1 amostra primária por paciente (`'01'`), censura administrativa em $\tau = 5 \text{ anos}$ e seguimento mediano via Kaplan-Meier Reverso.
- **Modelagem Preditiva & Baselines:**
  - $M_0$ (Nulo KM), $M_1$ (Cox Clínico), $M_3$ (Coxnet Integrado), $M_5$ (Random Survival Forest) e $M_6$ (Gradient Boosting Survival).
  - Validação cruzada repetida $5 \times 5$ (25 dobras estratificadas).
  - Controle de taxa de falsa descoberta (FDR via Benjamini-Hochberg, $q < 0,05$).
- **Validação Externa Independente (`REG-08`):** Modelo congelado avaliado cegamente na coorte independente GSE31210 (Microarray Affymetrix) confirmando generalização trans-plataforma.
- **Artefatos e Interface:**
  - Dashboard interativo em Streamlit com simulação de risco e nomograma (`app/dashboard.py`).
  - Relatório executivo diagramado em PDF de 5 páginas (`docs/relatorio_cientifico_executivo.pdf`).
  - Model Cards estruturados e documentados (`models/model_card_m3.json` e `MODEL_CARD.md`).
- **Suíte de Testes:** 20 testes automatizados no `pytest` com 100% de sucesso.
- **Linter & Qualidade:** Ruff 100% limpo (`0 erros`).

---

## 🛠️ 3. Dependências de Infraestrutura Externa
- Matrizes brutas de expressão gênica e dados clínicos do GDC Data Portal (TCGA-LUAD, TCGA-KIRC) e NCBI GEO (GSE31210).
- Os artefatos processados e modelos serializados estão versionados em `data/interim/` e `models/`.
