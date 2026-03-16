# 🔱 SwingFish | Terminal de Trading Abissal (Português)

![SwingFish Showcase](./assets/video_muestra_3.gif)

**SwingFish** é um terminal de análise automatizada de nível institucional para Swing Trading. Supera as limitações das IAs genéricas ao fundir modelos quantitativos com um comitê de lógica multi-agente.

## 💡 O Problema: LLMs Generalistas vs. SwingFish
Os LLMs padrão usam web-scraping para "resumir" o mercado, o que frequentemente leva a alucinações financeiras e análises superficiais.
**SwingFish combate isso através de:**
1.  **Separação de Dados e Raciocínio**: Utilizamos um motor dedicado para obter factos brutos primeiro.
2.  **Comitê Especializado**: Os agentes processam dados baseados em domínios específicos (Risco, Técnico, Macro) em vez de gerar texto genérico.
3.  **Rastro de Auditoria**: Cada veredito inclui um relatório profundo que compara os dados brutos com o raciocínio.

## 🔱 Pilares Analíticos
### 1. Motor de Dados (Dashboard)
Atua como o "Sonar". Extrai dados do Yahoo Finance, FRED e COT.
*   **Metodologia**: [Leia mais](./backend/Dashboard/METODOLOGY_dashboard_pt.md)

### 2. Sonda Abissal (Comitê Multi-Agente)
Orquestrado via **LangGraph**, 6 agentes (Técnico, Fundamental, Risco, Opções, Sentimento, Macro) analisam o ativo. Um **Portfolio Manager** sintetiza os relatórios para eliminar vieses.
*   **Metodologia**: [Leia mais](./backend/multiagent_analysis/METODOLOGY_multiagent_pt.md)

### 3. Motor de Pontuação S&P 500
Filtra o universo do S&P 500 através de uma fórmula ponderada (0-100) baseada nos modelos de Piotroski, Altman, Beneish e Fórmula Mágica.
*   **Metodologia**: [Leia mais](./backend/Filter_sp500/METODOLOGY_filter_sp500_pt.md)

## 🔄 Fluxo de Trabalho Ideal
1.  **Check Macro**: Usar o Dashboard Macro para identificar o regime de mercado (Risk-on/off).
2.  **Varredura de Ativos**: Identificar ativos líquidos com momentum via o S&P 500 Screener.
3.  **Pesquisa Profunda**: Executar a **Sonda Abissal** num ticker específico para receber uma auditoria e veredito institucional.

## ⚠️ Aviso Importante
Este terminal está estritamente otimizado para **Ações de Empresas Individuais**, especificamente do **mercado norte-americano (US)**. O uso em índices ou outros ativos pode resultar em mapeamentos de dados incompletos.

## 🗺️ Roadmap
1.  **Estratégia de Opções Robusta**: Integração de um módulo profissional de [OptionStrat-AI](https://github.com/EconomiaUNMSM/OptionStrat-AI).
2.  **Classes de Ativos**: Suporte para Commodities e ETFs.
3.  **Integração de Futuros**: Análise de contratos de futuros.
4.  **Suporte Multi-LLM**: Compatibilidade com Anthropic (Claude), DeepSeek e LLMs locais.
5.  **Personalização Interativa**: Ajuste em tempo real dos papéis e ferramentas dos agentes.
6.  **Modelos Quantitativos Avançados**: Integração de estratégias de ML e Deep Learning pré-backtesteadas.
7.  **Ponderação Dinâmica**: Configuração personalizada dos pesos para o sistema de pontuação do S&P 500.

## 👨‍💻 Autor
**Luis Fabio Yoplac Cortez**
- [GitHub](https://github.com/EconomiaUNMSM)
- [LinkedIn](https://www.linkedin.com/in/luis-yoplac-cortez-10397328b)
