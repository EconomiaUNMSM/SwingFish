# Metodologia de Análise Multiagente | O Cérebro Algorítmico

## 1. Inteligência Multidisciplinar
O módulo **multiagent_analysis** é o núcleo de raciocínio do SwingFish. Utiliza o **LangGraph** para orquestrar um comitê virtual de investimentos composto por 6 agentes especializados.

### 💡 Combate a LLMs Generalistas
LLMs genéricos frequentemente "alucinam" ao resumir notícias desenfreadamente. O SwingFish **combate alucinações** fornecendo dados brutos estruturados aos agentes dentro de um grafo controlado. Nossos agentes funcionam como "intérpretes de dados especialistas", eliminando a necessidade de web scraping aleatório que gera ruído.

## 2. Arquitetura e Fluxo
1.  **DataFetcher (Sequencial)**: Carrega o "Estado dos Fatos".
2.  **Inferência Paralela**: Nodos técnicos, macro e de risco processam simultaneamente.
3.  **Portfolio Manager (Síntese)**: Supervisor sênior que valida os relatórios e emite o Veredito.

## 3. Os Agentes do Comitê
*   **Técnico**: Ichimoku Clouds, RSI e ATR.
*   **Risco (CRO)**: Cálculos de VaR e CVaR via simulações de Monte Carlo.
*   **Opções**: Put/Call skew e "Expected Move".
*   **Macro**: Rendimentos de títulos (TNX) e spreads de crédito.

## 4. Auditoria Institucional (Audit Trail)
Cada análise gera um PDF de Auditoria Profunda. Este documento permite que o trader humano verifique os dados exatos utilizados e a lógica do agente, garantindo total transparência.

---
**⚠️ Aviso**: Otimizado para **Ações Norte-Americanas**. Indicadores técnicos e métricas de opções estão calibrados para o comportamento deste mercado específico.
