# Multiagent Analysis Methodology | The Algorithmic Brain

## 1. Introduction: Multidisciplinary Intelligence
The **multiagent_analysis** module is the central reasoning core of SwingFish. Built with **LangGraph**, it orchestrates a virtual investment committee composed of 6 specialized AI agents overseen by a senior Portfolio Manager.

### 💡 Combating Generalist LLMs
Generic LLMs (like GPT-4 with browsing) often "hallucinate" by missing subtle financial nuances or repeating outdated web-scraped sentiments. SwingFish **combats hallucinations** by providing agents with structured raw data strings and a strict JSON reporting logic. The agents function as "expert data interpreters" within a controlled graph, not as random web crawlers.

## 2. Architecture & State Management
To ensure accuracy, we use a distinct workflow:
1.  **DataFetcher (Sequential)**: The only node authorized to touch external data. It pre-loads the "Fact State".
2.  **Parallel Inference**: Agents (Technical, Risk, Macro, etc.) process the pre-loaded data simultaneously.
3.  **Portfolio Manager (Synthesis)**: A senior supervisor that cross-validates all reports.

## 3. The Specialized Agents
*   **Technical**: Focuses on Ichimoku Clouds, RSI, and ATR.
*   **Risk (CRO)**: Calculates VaR and CVaR via 10,000 Monte Carlo scenarios.
*   **Options Specialist**: Analyzes Put/Call skew and the "Expected Move".
*   **Macro Strategist**: Monitors TNX yields and credit spreads.

## 4. Institutional Audit Trail
Every analysis generates a **Deep-Dive Audit Trail (PDF)**. This document lists the exact raw data used alongside the AI's reasoning, allowing a human trader to verify the logic step-by-step.

---
**⚠️ Warning**: Optimized for **Individual North American Equities**. Technical indicators like Ichimoku or specific Options skew metrics are calibrated for equity market behavior.
