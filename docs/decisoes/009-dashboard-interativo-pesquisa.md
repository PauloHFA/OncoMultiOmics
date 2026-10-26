# ADR 009: Interface Interativa e Dashboard de Simulação de Sobrevida (Streamlit)

## Contexto
A disseminação dos achados e a transparência metodológica exigidas pelas diretrizes TRIPOD+AI requerem ferramentas que permitam a pesquisadores e bioinformatas inspecionar dinamicamente o comportamento dos modelos preditivos e das curvas de probabilidade $S(t | x)$. Foi solicitada a implementação de um dashboard interativo multimodal como a 3ª extensão do motor OncoMultiOmics.

## Decisão
1. **Framework Selecionado**: Streamlit, integrado via gerenciador `uv`, garantindo inicialização rápida, reatividade e isolamento de dependências.
2. **Arquitetura da Aplicação (`app/dashboard.py`)**:
   - **Suporte Multi-Coorte**: Seletor dinâmico para alternar entre as coortes TCGA-LUAD e TCGA-KIRC.
   - **Simulador Individual**: Sliders clínicos (Idade, Sexo, Estágio Patológico AJCC) combinados com controles padronizados (z-scores) dos biomarcadores mais influentes de cada neoplasia (`DKK1`, `IGF2BP1`, `NAPSA`, `SFTPB` para LUAD; `COL7A1`, `IGFN1`, `SLC16A12`, `HMGCS2` para KIRC).
   - **Projeção Temporal Dinâmica**: Estimação simultânea de $S(t | x)$ ao longo do horizonte de 5 anos ($\tau = 1.826,25 \text{ dias}$) com destaque para horizontes críticos de 1, 3 e 5 anos, comparando o modelo clínico convencional ($M_1$) com o modelo integrado ($M_3$).
   - **Decomposição Linear de Contribuição**: Gráfico de pesos e impacto de cada atributo ($\beta \cdot z$) para explicar a elevação ou redução do risco em relação à média populacional.
   - **Painel de Validação e Governança**: Exibição das métricas de 25 dobras repetidas ($C_{\text{Uno}}$, Harrell, AUCs dinâmicas, IBS), curvas de Kaplan-Meier e Model Card estruturado.
3. **Conformidade Ética e Científica (REG-16)**:
   - Inserção de banner proeminente de aviso legal especificando que a aplicação é estritamente voltada à pesquisa translacional, sem fins diagnósticos ou terapêuticos clínicos diretos.

## Consequências
- Permite validação visual e simulação interativa de cenários hipotéticos sem necessidade de execução manual de scripts.
- Facilita a comunicação dos resultados para revisores, colaboradores clínicos e a comunidade científica aberta.
- Mantém o ecossistema modular e desacoplado, com testes automatizados dedicados em `tests/test_dashboard.py`.
