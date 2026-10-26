# Dicionário de Dados — OncoMultiOmics Survival Engine (TCGA-LUAD)

Este dicionário documenta todas as variáveis clínicas, desfechos e atributos moleculares utilizados no estudo, incluindo origem, formato, transformação e tratamento de valores omissos ou inconsistentes.

---

## 1. Identificadores de Amostra e Paciente

| Campo | Tipo | Origem | Descrição e Regras |
|---|---|---|---|
| `paciente_id` | String (12 char) | Barcode TCGA | Identificador único do paciente (ex: `TCGA-05-4244`). Chave primária de junção clínico-molecular. |
| `sample_barcode` | String | Barcode TCGA | Identificador completo da amostra (ex: `TCGA-05-4244-01A-01R-1107-07`). |
| `sample_type` | String (2 dígitos) | Posição 14-15 | Tipo de tecido: `01` = Tumor Sólido Primário (incluso); `11` = Tecido Normal Adjacente (excluído). |
| `tss_code` | String (2 dígitos) | Posição 6-7 | *Tissue Source Site* (hospital/centro de origem). Utilizado estritamente para auditoria de efeito de lote. |

---

## 2. Desfechos de Sobrevivência (TCGA-CDR — Liu et al., 2018)

| Campo | Tipo | Valores | Descrição e Tratamento |
|---|---|---|---|
| `OS` | Binário (int/bool) | `0` = Vivo / censurado, `1` = Óbito | Desfecho primário de Sobrevida Global. |
| `OS.time` | Numérico (dias) | Contínuo positivo | Dias transcorridos do diagnóstico até óbito ou última data de seguimento. Amostras com tempo $\le 0$ são excluídas. |
| `OS_tau_time` | Numérico (dias) | $[0, 1826.25]$ | Tempo truncado no horizonte administrativo $\tau = 5 \text{ anos}$ ($1.826,25 \text{ dias}$). |
| `OS_tau_event` | Binário | `0` ou `1` | Status do evento reclassificado: se evento ocorreu após $\tau$, é censurado em $\tau$ (`0`). |
| `PFI` | Binário | `0` = Sem progressão, `1` = Progressão/Recorrência/Morte | Desfecho de Intervalo Livre de Progressão (sensibilidade). |
| `PFI.time` | Numérico (dias) | Contínuo positivo | Dias até progressão ou censura. |

---

## 3. Variáveis Clínicas Basais (Covariáveis do Modelo $M_1$)

| Campo | Tipo | Categorias / Unidade | Tratamento e Codificação |
|---|---|---|---|
| `idade` | Numérico | Anos ao diagnóstico | Valores biológicos válidos (18 a 100). Padronização por z-score ajustada no treino. |
| `sexo` | Categórico | `MALE`, `FEMALE` | Codificado como variável binária (`is_female`). |
| `estagio_ajcc` | Categórico / Ordinal | `Stage I`, `Stage II`, `Stage III`, `Stage IV` | Harmonização das diferentes edições do AJCC agrupando subestágios (ex: `Stage IA` e `IB` viram `Stage I`). |
| `estagio_ajcc_simplificado` | Categórico | `I`, `II`, `III`, `IV` | Tratamento como variáveis one-hot ou ordinais no treino. |
| `fumante` | Categórico | `Current`, `Former`, `Never` | Agrupamento de categorias de exposição tabágica (com indicador de valor faltante caso $> 5\%$). |

---

## 4. Variáveis Moleculares (RNA-Seq)

| Campo | Tipo | Origem | Tratamento e Escala |
|---|---|---|---|
| Genes (Ensembl ID / Gene Symbol) | Numérico contínuo | Matriz STAR-Counts (TPM) | Transformação padrão: $\log_2(\text{TPM} + 1)$. Apenas genes codificadores de proteína com expressão detectada em $\ge 20\%$ das amostras. |
| `batch_plate` / `batch_tss` | Categórico | Manifest / Barcode | Metadados técnicos. **Proibido o uso como preditores** em $M_1, M_2, M_3$; usados apenas no diagnóstico de lote (PCA e resíduos). |

