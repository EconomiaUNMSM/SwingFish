# 🔱 SwingFish | Terminal de Trading Abisal (Español)

![SwingFish Showcase](./assets/video_muestra_3.gif)

**SwingFish** es una terminal de análisis automatizado de grado institucional para Swing Trading. Supera las limitaciones de las IAs genéricas al fusionar modelos cuantitativos con un comité de lógica multi-agente.

## 💡 El Problema: LLMs Generalistas vs. SwingFish
Los LLMs estándar utilizan web-scraping para "resumir" el mercado, lo que a menudo conduce a alucinaciones financieras y análisis superficiales.
**SwingFish combate esto mediante:**
1.  **Separación de Datos y Razonamiento**: Utilizamos un motor dedicado para obtener hechos crudos primero.
2.  **Comité Especializado**: Los agentes procesan datos basados en dominios específicos (Riesgo, Técnico, Macro) en lugar de generar texto genérico.
3.  **Rastro de Auditoría**: Cada veredicto incluye un informe profundo que compara los datos crudos con el razonamiento.

## 🔱 Pilares Analíticos
### 1. Motor de Datos (Dashboard)
Actúa como el "Sonar". Extrae datos de Yahoo Finance, FRED y COT.
*   **Metodología**: [Leer más](./backend/Dashboard/METODOLOGY_dashboard.md)

### 2. Sonda Abisal (Comité Multi-Agente)
Orquestado a través de **LangGraph**, 6 agentes (Técnico, Fundamental, Riesgo, Opciones, Sentimiento, Macro) analizan el activo. Un **Portfolio Manager** sintetiza sus informes para eliminar sesgos.
*   **Metodología**: [Leer más](./backend/multiagent_analysis/METODOLOGY_multiagent.md)

### 3. Motor de Puntuación S&P 500
Filtra el universo del S&P 500 mediante una fórmula ponderada (0-100) basada en los modelos de Piotroski, Altman, Beneish y la Fórmula Mágica.
*   **Metodología**: [Leer más](./backend/Filter_sp500/METODOLOGY_filter_sp500.md)

## 🔄 Flujo de Trabajo Ideal
1.  **Chequeo Macro**: Usar el Dashboard Macro para identificar el régimen de mercado (Risk-on/off).
2.  **Escaneo de Activos**: Identificar activos líquidos con momentum vía el S&P 500 Screener.
3.  **Investigación Profunda**: Ejecutar la **Sonda Abisal** en un ticker específico para recibir una auditoría y veredicto institucional.

## ⚠️ Advertencia Importante
Esta terminal está estrictamente optimizada para **Acciones de Empresas Individuales**, específicamente del **mercado norteamericano (US)**. El uso en índices u otros activos puede resultar en mapeos de datos incompletos.

## 🗺️ Hoja de Ruta (Roadmap)
1.  **Estrategia de Opciones Robusta**: Integración de un módulo profesional de [OptionStrat-AI](https://github.com/EconomiaUNMSM/OptionStrat-AI).
2.  **Clases de Activos**: Soporte para Commodities y ETFs.
3.  **Integración de Futuros**: Análisis de contratos de futuros de alta mar.
4.  **Soporte Multi-LLM**: Compatibilidad con Anthropic (Claude), DeepSeek y LLMs locales.
5.  **Personalización Interactiva**: Ajuste en tiempo real de los roles y herramientas de los agentes.
6.  **Modelos Cuantitativos Avanzados**: Integración de estrategias de ML y Deep Learning pre-backtesteadas.
7.  **Ponderación Dinámica**: Configuración personalizada de los pesos para el sistema de puntuación del S&P 500.

## 👨‍💻 Autor
**Luis Fabio Yoplac Cortez**
- [GitHub](https://github.com/EconomiaUNMSM)
- [LinkedIn](https://www.linkedin.com/in/luis-yoplac-cortez-10397328b)
