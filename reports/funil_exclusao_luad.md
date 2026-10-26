# Relatório de Curadoria Clínica e Funil de Exclusão — TCGA-LUAD

- **Coorte**: TCGA-LUAD (*Lung Adenocarcinoma*)
- **Desfecho Primário**: Sobrevida Global (OS) com horizonte $\tau = 5\text{ anos}$ (1826.2 dias)
- **Seguimento Mediano (KM Reverso)**: 2.41 anos (882.0 dias)

## 1. Funil de Exclusão (REG-01, REG-13)

| Etapa | Pacientes Restantes | Excluídos | Motivo da Exclusão |
|---|---|---|---|
| 1. Total TCGA-LUAD no TCGA-CDR | 641 | 0 | Amostra bruta do estudo |
| 2. Pacientes únicos no TCGA-CDR | 519 | 122 | Duplicatas de registro no arquivo clínico |
| 3. Pacientes com RNA-Seq tumoral primário ('01') | 515 | 4 | Ausência de amostra tumoral primária (01) com RNA-Seq |
| 4. Exclusão de tempos de seguimento nulos ou não-positivos (OS.time <= 0) | 502 | 13 | Seguimento zero ou tempo de evento inválido |
| 5. Exclusão de estadiamento AJCC indefinido / discrepante | 494 | 8 | Estágio patológico ausente ou [Discrepancy] |

## 2. Estatísticas da Coorte Final Elegível

- **Total de Pacientes Elegíveis**: 494
- **Óbitos Observados (OS Bruto)**: 180 (36.4%)
- **Óbitos no Horizonte $\tau$ (5 Anos)**: 170 (34.4%)
- **Distribuição de Estágio AJCC**:
  - Stage I: 269 (54.5%)
  - Stage II: 120 (24.3%)
  - Stage III: 80 (16.2%)
  - Stage IV: 25 (5.1%)
- **Sexo**: Feminino = 268 (54.3%), Masculino = 226 (45.7%)
- **Idade**: Média de 65.3 anos (Valores ausentes: 10 — serão imputados via mediana intra-fold)

---
*Documento gerado automaticamente pelo pipeline de curadoria em conformidade com REG-01 e REG-13.*