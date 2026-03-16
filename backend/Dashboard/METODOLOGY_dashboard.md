# METODOLOGY_dashboard

## 1. Introducción y Propósito del Módulo

El módulo **Dashboard** del sistema **SwingFish** es la capa de extracción, procesamiento y agregación de datos duros orientados tanto a métricas corporativas individuales (Microeconomía/Fundamentales) como al entorno de mercado global (Macroeconomía/Sentimiento). Su principal objetivo es servir como el "motor proveedor de datos" (Data Provider Engine) para un ecosistema integral de análisis de Swing Trading.

Mientras que otras partes del ecosistema (como el sistema multiagente) se encargan de *interpretar* los datos, este módulo garantiza que los datos sean:
1. Extraídos de fuentes fiables (Yahoo Finance, Finviz, FRED, CFTC/COT, ForexFactory).
2. Estructurados uniformemente en formatos orientados a APIs (JSON/Diccionarios).
3. Entregados en tiempo real o cuasi-real para la toma de decisiones.

## 2. Arquitectura de Archivos y Componentes

El módulo se compone de tres pilares fundamentales implementados en los siguientes scripts:

### 2.1. `asset_details.py` (Micro y Fundamentales)
Este componente está diseñado para realizar una radiografía completa de un activo en particular (Ticker). Extrae información que todo inversor institucional revisaría antes de tomar una posición en acciones.

**Fuentes de datos:**
- `yfinance`: Para métricas en tiempo real y ratios financieros básicos.
- `yahooquery`: Para estructuraciones más complejas como perfiles corporativos, datos de "Insiders" (ejecutivos comprando/vendiendo acciones de su propia empresa) y grandes tenedores institucionales.

**Funciones Clave:**
* `get_general_info()`: Extrae el precio actual, beta (medida de volatilidad comparada con el mercado), promedios de volumen, ratios de valoración y **Estimaciones de Analistas de Wall Street** (High, Mean, Low Targets). Conocer a dónde apunta el consenso institucional es crítico para evaluar el "Upside" de la acción.
* `get_insider_summary()`: Retorna los movimientos del "Smart Money" interno. Si el CEO y el CFO están vendiendo masivamente, o si fondos como Vanguard/BlackRock están acumulando posiciones, esta función lo extrae y estructura de manera que sea fácilmente interpretable.
* `get_full_details()`: Unifica todo en un solo diccionario, convirtiéndose en el "endpoint" natural de esta clase para ser llamado por otros módulos (por ejemplo, el agente Fundamental de la carpeta multiagente).

### 2.2. `macro_sentiment.py` (Macroeconomía y Flujos Institucionales)
El Swing Trading rara vez es exitoso si se opera en contra del régimen del mercado. Este archivo proporciona esa "vista de pájaro" esencial.

**Fuentes de datos:**
- `requests` + `xml.etree.ElementTree`: Para ForexFactory.
- `fredapi`: Para los datos de la Reserva Federal de San Luis.
- `cot_reports`: Para informes de la Commodity Futures Trading Commission (CFTC).

**Funciones Clave:**
* `get_economic_calendar()`: Hace scrapping del feed XML público de Forex Factory. Solo filtra eventos marcados como **"High" (Alto Impacto)**, tales como NFP (Nóminas no Agrícolas), decisiones sobre Tasas de Interés de bancos centrales o reportes de Inflación (CPI). El swing trader necesita saber si se aproxima una fecha "peligrosa" para cubrir (hedge) sus posiciones o cerrarlas temporalmente.
* `get_economic_events()`: Se conecta a la API de FRED para extraer series históricas robustas:
  - Tasa de Desempleo vs cierre del S&P 500.
  - GDP (Gross Domestic Product / PIB).
  - CPI (Inflación).
  - Confianza del Consumidor (UMCSENT).
  Entender la salud macro subyacente define si estamos en una fase expansiva (Risk-on) o contractiva (Risk-off).
* `get_cot_report()`: Extrae el **Commitment of Traders (COT)**. Esto permite observar el posicionamiento neto de los "Leveraged Funds" (Hedge Funds) frente a los "Dealers/Commercials" en el mercado de futuros. Una invaluable herramienta que muestra dónde está posicionado el verdadero capital inteligente semana a semana en índices (S&P500), divisas y bonos. Se calcula el "Net COT" restando los cortos de los largos.

### 2.3. `market_scanner.py` (Escaneo del Mercado)
Este componente es el "buscador de oportunidades" algorítmico, utilizando los filtros preestablecidos del screener de Finviz.

**Funciones Clave:**
* `get_market_screener()`: Devuelve dos listas vitales:
  1. **"Most Active"**: Los instrumentos con mayor volumen de transacciones actuales. Un swing trader requiere liquidez alta para asegurar entradas y salidas exactas sin *slippage* (deslizamiento de precio).
  2. **"Most Volatile"**: Los activos que están experimentando mayores variaciones porcentuales. Generalmente es aquí donde se encuentran las oportunidades de Momentum para trades de corto a medio plazo (1 a 10 días).
En ambos casos, extrae precio, volumen, P/E ratio, Market Cap y cambio porcentual. Todo formateado en `pd.DataFrame` y convertido finalmente en diccionarios para serialización.

## 3. Utilidad Práctica en Swing Trading

El **Swing Trading** es una estrategia que intenta capturar "swings" o movimientos de precios a corto/mediano plazo dentro de una tendencia principal que dura desde unos pocos días hasta varias semanas. No es Day Trading (donde la volatilidad intra-diaria domina) y no es Value Investing a 5 años. Por ende, la toma de decisiones debe ser la fusión de análisis **Técnico** + **Fundamental** + **Conciencia Macro**. 

El módulo Dashboard dota a la infraestructura SwingFish de esta triada:

### Fase 1: Entendiendo el Régimen (Top-Down Approach)
Antes de buscar una acción específica, se ejecuta `macro_sentiment.py`. 
- Revisamos el reporte COT (¿Los fondos de cobertura están largos o cortos en el S&P500?).
- Se verifican los indicadores adelantados en FRED (¿Está la inflación repuntando? ¿Desempleo al alza?).
- Miramos el Calendario Económico: Si la Reserva Federal habla el miércoles, es prudente reducir el tamaño de las posiciones el martes.

### Fase 2: Escaneando Oportunidades
Sabiendo el clima macroeconómico, se corre `market_scanner.py`.
- Si el macro es alcista y el mercado es optimista (Risk-on), buscaremos activos altamente líquidos en la lista de "Most Active" o rezagados ganando tracción en "Most Volatile" que podamos comprar.

### Fase 3: Radiografía del Activo
Una vez que encontramos (por ejemplo) que `$AAPL` tiene momentum técnico y está en nuestro escáner, disparamos `asset_details.py`:
- Se chequean los Insiders (Si el CEO de Apple acaba de vender el 20% de sus tenencias, es una inmensa bandera roja contraria al Momentum detectado).
- Confirmar Ratios Institucionales (Propiedad institucional por encima del 70% asegura estabilidad, mientras que precios objetivo promedio muy superiores al precio actual sugieren "Upside").

## 4. Consideraciones Técnicas y Extensibilidad

* Todos los scripts devuelven diccionarios de Python o listas de diccionarios, y envuelven los procesos de obtención en bloques `try/except`. Esto asegura la resiliencia: si Finviz bloquea peticiones o ocurre un _timeout_ en Yahoo Finance, el Dashboard no hace crashear toda la aplicación en Backend; en su lugar, devuelve un diccionario con la clave `{"error": "mensaje..."}`, que los agentes de IA o el frontend sabrán manejar grácilmente.
* El módulo maneja correctamente los MultiIndex conflictivos y los objetos incompatibles mediante aplanamiento, `fillna()` y el uso explícito de `multi_level_index=False` implementado sistémicamente en los workflows recientes.
* Puede conectarse fácilmente pasivamente mediante crons o scripts automatizados (`FastAPI`) para alimentar un Dashboard Frontend en React/Vue, o ser utilizado por un framework de LangChain/LangGraph, actuando como la base de datos temporal provisoria del estado del mercado.

## 5. Resumen de Flujo de Negocio
**Input:** Símbolos financieros (`AAPL`), Mercados (`E-MINI S&P 500`), o peticiones estáticas (`macroentorno`). \
**Procesamiento:** Descarga, curaduría de DataFrames (Pandas), limpieza de strings XML, agrupamiento, formateo lógico. \
**Output:** Matrices de datos puras estandarizadas.

Este desarrollo otorga total soberanía de datos sobre el mercado, constituyendo el corazón latente donde SwingFish bebe información real, verificada e institucionalmente respetada antes de aplicar lógicas de inteligencia artificial predictiva superior.
