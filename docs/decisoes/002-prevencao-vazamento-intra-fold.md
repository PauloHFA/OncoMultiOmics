# ADR 002: Isolamento Estrito Anti-Vazamento (REG-03) e Validação Aninhada

## Contexto
Um dos erros mais comuns em Data Science genômica é o vazamento de dados (*data leakage*), que infla artificialmente o desempenho dos modelos ao selecionar genes ou calcular parâmetros estatísticos (médias, desvios ou componentes principais) utilizando o conjunto completo de amostras antes da divisão treino/teste.

## Decisão
1. **Seleção de Genes Intra-Fold**: O ranqueamento univariado por escore de Cox é executado estritamente sobre as amostras de treinamento de cada dobra ($X_{\text{train}}, y_{\text{train}}$).
2. **Padronização e Imputação Isoladas**: O `SimpleImputer` e o `StandardScaler` são ajustados exclusivamente no conjunto de treinamento de cada dobra e apenas aplicados (*transform*) ao conjunto de teste.
3. **Validação Aninhada (*Nested CV*)**: A sintonização do parâmetro de regularização $\alpha$ do Elastic Net é realizada por meio de um laço interno de validação cruzada contido dentro do conjunto de treino da dobra externa.
4. **Verificação Automatizada**: Testes automatizados com `pytest` (`test_reg03_anti_vazamento.py`) asseguram contratualmente que os estimadores não acessam nem são afetados por alterações no conjunto de teste.

## Consequências
- Estimativas de métricas livres de otimismo artificial, reprodutíveis e cientificamente auditáveis.

