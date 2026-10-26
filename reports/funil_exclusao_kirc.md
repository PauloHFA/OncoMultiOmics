# Relatório de Curadoria Clínica e Funil de Exclusão — TCGA-KIRC

- **Coorte**: TCGA-KIRC (*Kidney Renal Clear Cell Carcinoma*)
- **Desfecho Primário**: Sobrevida Global (OS) com horizonte $\tau = 5\text{ anos}$ (1826.2 dias)
- **Seguimento Mediano (KM Reverso)**: 4.61 anos (1683.0 dias)

## 1. Funil de Exclusão (REG-01, REG-13)

| Etapa | Pacientes Restantes | Excluídos | Motivo da Exclusão |
|---|---|---|---|
| 1. Total TCGA-KIRC no TCGA-CDR | 944 | 0 | Registros brutos do consórcio |
| 2. Pacientes únicos no TCGA-CDR | 536 | 408 | Duplicatas de registro clínico |
| 3. Pacientes com RNA-Seq tumoral primário ('01') | 533 | 3 | Ausência de RNA-Seq de tumor sólido primário (01) |
| 4. Exclusão de tempos de seguimento nulos ou não-positivos (OS.time <= 0) | 531 | 2 | Seguimento zero ou inválido |
| 5. Exclusão de estadiamento AJCC indefinido / [Discrepancy] | 528 | 3 | Estágio não-classificável |

## 2. Estatísticas da Coorte Final Elegível
- **Total de Pacientes Elegíveis**: 528
- **Óbitos Observados (OS Bruto)**: 174 (33.0%)
- **Óbitos no Horizonte $\tau$ (5 Anos)**: 149 (28.2%)
- **Distribuição por Estágio AJCC**:
  - Stage I: 265 (50.2%)
  - Stage III: 123 (23.3%)
  - Stage IV: 83 (15.7%)
  - Stage II: 57 (10.8%)
- **Sexo**: Feminino = 186 (35.2%), Masculino = 342 (64.8%)
- **Idade**: Média de 60.6 anos
- **Genes Expressos Mantidos**: 17635 genes

---
*Documento gerado automaticamente pelo pipeline de curadoria em conformidade com REG-01 e REG-13.*