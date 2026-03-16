# Dashboard Methodology | Methodology of the Data Provider Engine

## 1. Introduction and Purpose
The **Dashboard** module of the **SwingFish** system is the layer for extracting, processing, and aggregating hard data focused on both individual corporate metrics (Microeconomics/Fundamentals) and the global market environment (Macroeconomics/Sentiment). Its main goal is to serve as the **"Data Provider Engine"** for a comprehensive Swing Trading analysis ecosystem.

While other parts of the ecosystem (such as the multiagent system) handle *interpreting* the data, this module ensures that the data is:
1.  Extracted from reliable sources (Yahoo Finance, Finviz, FRED, CFTC/COT, ForexFactory).
2.  Uniformly structured in API-oriented formats (JSON/Dictionaries).
3.  Delivered in real-time or near real-time for decision-making.

### 💡 Combating Hallucinations
By isolating data extraction into a dedicated engine, we ensure that AI agents do not have to "browse" or guess financial facts. They receive a **pre-verified raw context**, which eliminates the risk of hallucinations common in generic LLMs that rely solely on web scraping or outdated training data.

## 2. File Architecture and Components

### 2.1. `asset_details.py` (Micro & Fundamentals)
Designed to perform a complete x-ray of a specific asset (Ticker). It extracts information that any institutional investor would review before taking a position.
*   **Analyst Estimates**: Consensus targets (High, Mean, Low) from Wall Street.
*   **Insider Summary**: Smart Money movements (CEOs/CFOs buying or selling).

### 2.2. `macro_sentiment.py` (Macroeconomics & Institutional Flows)
Provides the essential "bird's eye view".
*   **Commitment of Traders (COT)**: Net positioning of Hedge Funds vs. Commercials.
*   **FRED Indicators**: GDP, Unemployment, CPI, and Consumer Sentiment.
*   **Economic Calendar**: High-impact events (NFP, Rate decisions) that define the "Danger Zone".

### 2.3. `market_scanner.py` (Opportunity Scanning)
The algorithmic "search engine" using Finviz filters.
*   **Most Active**: High liquidity assurance.
*   **Most Volatile**: Momentum opportunities for short-to-medium term trades (1 to 10 days).

## 3. Practical Utility in Swing Trading
Swing Trading aims to capture price swings within a main trend. The Dashboard module grants the necessary triad for this:

1.  **Phase 1: Understanding the Regime (Top-Down)**: Is the macro climate Risk-on or Risk-off?
2.  **Phase 2: Scanning Opportunities**: Finding liquid assets with momentum.
3.  **Phase 3: Asset X-Ray**: Confirming institutional backing and analyst upside before deployment.

---
**⚠️ Warning**: This module is optimized for **Individual North American Equities**. Using it for other asset classes may require specific configuration adjustments.
