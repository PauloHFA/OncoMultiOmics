# ADR 007: Calibração Probabilística Dinâmica e Nomograma Clínico-Molecular (REG-05)

## Contexto
Um modelo prognóstico que apenas discrimina (ordena riscos via C-index) sem calibração adequada não pode ser utilizado com segurança, pois probabilidades absolutas incorretas podem distorcer o aconselhamento de pacientes e a estratificação clínica. Conforme a regra REG-05:
> "Reportar C-index de Uno, AUC dependente do tempo, IBS e calibração, e não só o C-index."

## Decisão
Implementamos no módulo `src/oncosurv/visualizacao/calibracao.py`:
1. **Calibração por Quantis de Risco**: Avaliação em três horizontes clínicos de relevância oncológica: 1 ano (365 dias), 3 anos (1.095 dias) e 5 anos (1.826 dias).
2. **Estimativa Robusta Não-Paramétrica**: Dentro de cada quantil, a sobrevida observada foi calculada pelo estimador de Kaplan-Meier com intervalos de confiança de Greenwood a 95%.
3. **Métricas Formais**:
   - *Calibration Slope* (inclinação de calibração; ideal = 1,0).
   - *ICI (Integrated Calibration Index)*: erro médio absoluto entre probabilidade prevista e observada.
4. **Nomograma / Decomposição de Pesos**: Gráfico de pesos (*forest plot*) discriminando a contribuição relativa das covariáveis clínicas e de cada biomarcador transcricional no modelo $M_3$.

## Resultados Observados
- **Calibração nos Horizontes**:
  - **1 ano**: Slope = **$0,99$** | Erro Médio Absoluto $\text{ICI} = 0,028$ ($2,8\%$).
  - **3 anos**: Slope = **$0,82$** | Erro Médio Absoluto $\text{ICI} = 0,044$ ($4,4\%$).
  - **5 anos**: Slope = **$0,87$** | Erro Médio Absoluto $\text{ICI} = 0,163$ ($16,3\%$).
- **Pesos Relativos**:
  - Estadiamento AJCC é o maior preditor clínico isolado ($\beta = +0,449$, $HR = 1,567$).
  - O perfil molecular atua de forma refinada modulando o risco basal: `DKK1` ($\beta = +0,168$), `TCN1` ($\beta = +0,129$), `CPS1` ($\beta = +0,090$) aumentam o risco, enquanto `SLC14A2` ($\beta = -0,108$) e `SFTPB` ($\beta = -0,075$) exercem efeito protetor associado a diferenciação alveolar.

## Consequências
- A regra REG-05 foi completamente atendida.
- As figuras `reports/figures/calibracao_multi_horizontes_m3.png` e `reports/figures/nomograma_pesos_m3.png` fornecem os gráficos essenciais exigidos pelas diretrizes TRIPOD+AI.

