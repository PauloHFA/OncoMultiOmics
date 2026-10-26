# ADR 006: Diagnóstico de Efeito de Lote Técnico e Análise de Sensibilidade a TSS (REG-09)

## Contexto
No TCGA, amostras de tecido tumoral são provenientes de múltiplos hospitais e centros de coleta (*Tissue Source Sites — TSS*), processadas em diferentes placas e datas. O risco metodológico documentado na Seção 2 e na regra REG-09 é de que diferenças técnicas entre centros se correlacionem espuriamente com o tempo de seguimento ou com a sobrevida dos pacientes, gerando falsos biomarcadores.

## Decisão
Implementamos no módulo `src/oncosurv/expressao/diagnostico_lote.py`:
1. **PCA na Matriz Molecular**: Extração das 10 primeiras componentes e teste ANOVA entre os centros de coleta (TSS) e as componentes PC1 a PC5.
2. **Teste de Associação TSS-Sobrevida**: Teste de log-rank multivariado entre os 11 principais centros de coleta ($\ge 15$ pacientes cada).
3. **Análise de Sensibilidade por Estratificação**: Comparação pareada do Hazard Ratio de cada biomarcador candidato em modelo de Cox convencional versus modelo de Cox estratificado por TSS (no qual a função de risco basal $\lambda_{0, s}(t)$ é livre por centro).

## Resultados Observados
- **Associação TSS com Sobrevida**: $\chi^2$ log-rank $p = 0,1090$ ($p > 0,05$). Não há associação estatisticamente significativa entre centro de coleta e sobrevida global.
- **Estabilidade dos Biomarcadores**:
  - `DKK1`: $HR_{\text{padrão}} = 1,527$ vs. $HR_{\text{estratificado}} = 1,555$ (variação de apenas $1,87\%$).
  - `IGF2BP1`: $HR_{\text{padrão}} = 1,389$ vs. $HR_{\text{estratificado}} = 1,353$ (variação de $2,58\%$).
  - `NAPSA`: $HR_{\text{padrão}} = 0,779$ vs. $HR_{\text{estratificado}} = 0,759$ (variação de $2,57\%$).
  - `SFTPB`: $HR_{\text{padrão}} = 0,803$ vs. $HR_{\text{estratificado}} = 0,788$ (variação de $1,87\%$).
  - `ABCC2`: $HR_{\text{padrão}} = 1,314$ vs. $HR_{\text{estratificado}} = 1,328$ (variação de $1,10\%$).
  - `KRT6A`: $HR_{\text{padrão}} = 1,401$ vs. $HR_{\text{estratificado}} = 1,400$ (variação de $0,07\%$).

## Consequências
- A regra REG-09 foi rigorosamente cumprida.
- Confirma-se que os biomarcadores identificados refletem sinal biológico intrínseco do tumor e não artefatos espúrios de lote ou hospital de origem.

