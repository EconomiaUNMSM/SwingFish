# METODOLOGY_multiagent

## 1. Introducción al Sistema de Inteligencia Multidisciplinaria

El módulo **multiagent_analysis** es el cerebro algorítmico de **SwingFish**. Aprovechando la tecnología de *Large Language Models* (LLMs), este módulo implementa y orquesta una firma virtual de inversión usando el entorno de **LangGraph** (una librería orientada a modelar la gestión de estado y grafos computacionales para agentes de Inteligencia Artificial). 

A diferencia de usar a un LLM individualmente y pedirle que actúe de analista, este enfoque lo segmenta. Construye un comité de 6 analistas cuantitativos (Agentes AI) que estudian los aspectos técnicos, de riesgo, de flujo monetario, de opciones, fundamentales y macroeconómicos, para luego entregar los reportes a un Agente Portfolio Manager (Jefe) que emite un dictamen final (Long, Short, o Cash). 

El objetivo es minimizar las "alucinaciones" inherentes a la IA y evitar el enredo de *roles múltiples*, brindando reportes institucionales para Swing Trading de la más alta calidad y un documento de trazabilidad de auditoría.

## 2. Abordando el Desafío de Concurrencia (DataFetcher y LangGraph)

Una característica vital implementada dentro de `graph.py` es solventar la incapacidad de la librería `yfinance` para ser *thread-safe* bajo un modelo paralelo asincrónico. 

Al ejecutar LLMs en los nodos paralelos del grafo, LangChain paraleliza de forma expedita (ahorrando tiempo al llamar seis veces a la API de OpenAI al mismo tiempo). Sin embargo, si cada agente tratase de extraer su propia data con yfinance utilizando ese multi-threading, Pandas y yfinance colapsarían o alterarían los precios en memoria de forma silenciosa.

**Solución Implementada:**
1. **Paso 1: `data_fetcher.py` (Secuencial).** El grafo inicia enviando el ticker hacia un nodo inicial (Entry Point) que funciona de manera estrictamente secuencial. Invocando todas las `tools`, el DataFetcher extrae la información dura de indicadores técnicos, opciones, macro y sentimientos, y la guarda en un `AnalystState` (estado) central.
2. **Paso 2: Fan-out Paralelo (Nodos LLM).** Una vez que el diccionario de estado posee *todos* los datos crudos extraídos de forma segura (ej. `raw_technical`, `raw_fundamental`), LangGraph activa los 6 agentes analíticos al unísono. Al tener la data ya pre-cargada, realizan inferencia (con LLMs) 100% libre de conflictos entre hilos y de un modo sumamente veloz.
3. **Paso 3: Fan-in Secuencial (Portfolio Manager).** Los 6 reportes de LLM y data cruda se reensamblan en el State, fluyendo al Agente Manager que toma la decisión soberana de trading.

## 3. Topología Organizacional: Los Agentes

Ubicados en `agents/`, cada uno cuenta con un System Prompt con reglas inflexibles. El *prompt engineering* central recae en obligar a cada agente a acatar estrictamente los **"Datos Crudos Verificados"**, penalizando duramente cualquier alucinación paramétrica en sus dictámenes.

### 3.1. `manager_agent.py` (Portfolio Manager / CRO)
- Es el cerebro que utiliza un LLM superior (`gpt-4o`). 
- **Función Principal:** Lee las conclusiones sectorizadas de cada analista y realiza validaciones cruzadas. Por ejemplo, si el agente técnico grita "Compra", pero el agente de Riesgo alerta que "El Max Drawdown actual sugiere pánico y no aguantará nuestro stop loss", el Manager impondrá directiva de No Operar (CASH).
- **Entregable:** Emite The Verdict (LONG, SHORT, CASH), un resumen interconectado y los protocolos de Take Profit, Stop Loss, marco de tiempo y tamaño de locación.

### 3.2. `technical_agent.py` (Analista Técnico)
- **Cálculos Subyacentes:** Reúne Indicadores Moving Averages, RSI, Índice Ulcer (para volatilidad y caídas), Ichimoku Clouds (Régimen de estado), y el Relative Volatility Index (RVI).
- **Función:** Genera la "Persistencia Cruda", por lo que entiende el nivel de *momentum*, dictamina soportes lógicos inquebrantables, y da señales de entrada al gerente.

### 3.3. `fundamental_agent.py` (Analista Fundamental)
- Reúne las lógicas del dashboard local: Ratios financieros, P/E ratio y, más importante, revisiones de targets por parte de analistas reales humanos y las transacciones de Insiders.
- **Función:** Determina el valor subyacente de la empresa. Detecta si la subida técnica actual es sustentable basada en compras institucionales del trimestre o no.

### 3.4. `risk_agent.py` (Analista de Riesgo de Mercado)
- **Cálculos Subyacentes:** Realiza proyecciones de Monte Carlo simulando 10,000 años paralelos con base en desviación estándar actual (Retornos Logarítmicos transformados a simples). Aporta Value At Risk (VaR) y CVaR, además de un control del comportamiento estacional del mes activo y drawdowns de crisis pasadas.
- **Función:** Acota la euforia de las estrategias de apalancamiento mostrando el nivel real estresado de exposición.

### 3.5. `options_agent.py` (Analista de Derivados / Volatilidad)
- **Cálculos Subyacentes:** Reúne ratios Put/Call, open interest, Implicit Volatility Skew y **Expected Move**.
- **Función:** El derivado rige a la acción hoy en día. Este agente proyecta exactamente cuánto espera el mercado de opciones (los market-makers) que se asigne a la acción en variación porcentual para la expiración más prontas de las primas (Straddle ATM calculation). 

### 3.6. `sentiment_agent.py` (Analista de Noticias)
- Conecta con motores de procesamiento NLP (FinBERT) para leer las noticias extraidas de la web.
- Evalúa el diferencial u "Optimismo Neto / Gap". Analiza si el flujo informativo genera un riesgo de cisne negro potencial.

### 3.7. `macro_agent.py` (Analista Macroeconómico)
- Chequea Spread Crediticios Institucionales (Ratio HYG de Bonos Basura sobre LQD Grado Inversión) para medir apetito de riesgo general, junto al VIX y Rendimientos de Ten Years Treasuries (TNX). Chequea ForexFactory por si hay FOMC rate policy o CPI hoy o mañana.

## 4. Generación de Evidencias (pdf_generator.py)

Uno de los aportes arquitectónicos más altos del sistema, es su motor de rendering fpdf2 de última generación, encapsulado en dos módulos esenciales:

1. **Reporte Ejecutivo Principal (`Analisis_Auditoria_TICKER.pdf`):** Un documento estilizado con código de color corporativo institucional. Realiza un parsing avanzado de la sintaxis Markdown nativa del LLM en formato tipográfico elegante. Muestra **únicamente los racionamientos argumentales curados** emitidos por cada nodo agente y la decisión final del Manager, emulando la calidad en PDF que Morgan Stanley o Goldman Sachs arrojan a sus clientes para leer cómodamente.

2. **Reporte de Audit Trail (`Audit_Trail_TICKER.pdf`):** La genialidad de un pipeline de IA reside en comprobar su calidad. Este segundo PDF emite una comparación *side-by-side* para **cada** analista.
   - En una celda sombreada de verde, imprime con tipografía "Courier" (Monoespaciada) la línea exacta de información cruda extraída de Pandas/Yfinance/Finviz (ej. `SMA 20: $184.20`).
   - Justo abajo de esto, en una celda en rosa y rojo, imprime la retórica redactada (Respuesta del Agente IA elaborador). 
   Este protocolo de auditoría permite detectar en un marco de 2 minutos si el LLM inventó los valores SMA en su explicación, erradicando la opacidad de los agentes de "Caja Negra".

## 5. Implementación en la Metodología de Swing Trading

Con esto, el Workflow completo para el decisor humano ocurre de este modo:
1. El usuario interviene una terminal y hace `python main.py TSLA`.
2. Las APIs capturan el estrés del mercado y las métricas directas (Segundos 1 a 10).
3. LangGraph despliega 6 cerebros simultáneos, evaluando si el technical momentum acompaña la valuación de opciones (Segundos 10 a 20).
4. El Portfolio Manager coteja asimetrías de riesgo beneficio frente al riesgo CVaR (Segundos 20 a 30).
5. Se redactan en la carpeta `reports/` los Pdfs Finales.
6. El Trader humano lee The Verdict y acoge los limitadores sugeridos (Stop Loss basados en Expected Move del mercado de opciones sumado al ATR) y evalúa el dictamen que se presenta purgado de cualquier sesgo emocional humano y puramente empírico. 

El módulo encapsula el análisis Wall Street Standard a nivel macro y técnico para que los tomadores de decisiones basen su arquitectura de apalancamiento de manera sólida y rigurosa.
