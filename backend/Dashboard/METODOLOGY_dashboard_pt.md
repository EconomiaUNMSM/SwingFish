# Metodologia do Dashboard | Metodologia do Motor Provedor de Dados

## 1. Introdução e Propósito
O módulo **Dashboard** do sistema **SwingFish** é a camada de extração, processamento e agregação de dados brutos (Microeconomia/Fundamentais) e dados globais (Macroeconomia/Sentimento). O seu principal objetivo é servir como o **"Motor Provedor de Dados"** para o ecossistema de análise de Swing Trading.

### 💡 Combate às Alucinações
Ao isolar a extração de dados num motor dedicado, garantimos que os agentes de IA não precisem de "navegar" ou adivinhar factos financeiros. Eles recebem um **contexto bruto pré-verificado**, o que elimina o risco de alucinações comuns em LLMs generalistas que dependem apenas de web scraping ou dados de treino desatualizados.

## 2. Componentes e Arquitetura

### 2.1. `asset_details.py` (Micro e Fundamentais)
Realiza uma radiografia completa do ativo (Ticker).
*   **Estimativas de Analistas**: Consenso (High, Mean, Low) de Wall Street.
*   **Resumo de Insiders**: Movimentos do "Smart Money" (CEOs/CFOs comprando ou vendendo).

### 2.2. `macro_sentiment.py` (Macroeconomia e Fluxos Institucionais)
Fornece a "vista de pássaro" do mercado.
*   **Relatório COT**: Posicionamento de Hedge Funds vs. Comerciais.
*   **Indicadores FRED**: PIB, Desemprego, Inflação e Confiança do Consumidor.

### 2.3. `market_scanner.py` (Escaneamento de Oportunidades)
Busca algorítmica usando filtros do Finviz.
*   **Most Active**: Garantia de alta liquidez.
*   **Most Volatile**: Oportunidades de momentum para trades de curto/médio prazo.

## 3. Utilidade Prática no Swing Trading
O Swing Trading busca capturar movimentos dentro de uma tendência. O Dashboard provê a tríade necessária:
1.  **Fase 1: Regime de Mercado (Top-Down)**: O clima macro é Risk-on ou Risk-off?
2.  **Fase 2: Escaneamento**: Encontrar ativos líquidos com volatilidade.
3.  **Fase 3: Radiografia do Ativo**: Confirmar o suporte institucional e o potencial de alta (upside).

---
**⚠️ Aviso**: Este projeto está otimizado para **Ações Individuais Norte-Americanas**. O uso em outros mercados pode resultar em mapeamento incompleto de dados.
