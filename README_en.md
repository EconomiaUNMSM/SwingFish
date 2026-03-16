# 🔱 SwingFish | Deep Sea Trading Terminal (English)

![SwingFish Showcase](./assets/video_muestra_3.gif)

**SwingFish** is an institutional-grade automated analysis terminal for Swing Trading. It overcomes the limitations of generalist AI by fusing quantitative models with a multi-agent logic committee.

## 💡 The Problem: Generalist LLMs vs. SwingFish
Standard LLMs use web-scraping to "summarize" the market, which often leads to financial hallucinations and superficial analysis.
**SwingFish combats this by:**
1.  **Data-Reasoning Separation**: We use a dedicated engine to fetch raw facts first.
2.  **Specialized Committee**: Agents process data based on specific domains (Risk, Technical, Macro) rather than generating generic text.
3.  **Audit Trail**: Every verdict includes a deep-dive report comparing raw input vs. reasoning.

## 🔱 Analytical Pillars
### 1. Data Provider Engine (Dashboard)
Acts as the "Sonar." It extracts data from Yahoo Finance, FRED, and COT.
*   **Methodology**: [Read More](./backend/Dashboard/METODOLOGY_dashboard_en.md)

### 2. Abyssal Probe (Multi-Agent Committee)
Orchestrated via **LangGraph**, 6 agents (Technical, Fundamental, Risk, Options, Sentiment, Macro) analyze the asset. A **Portfolio Manager** synthesizes their reports to avoid bias.
*   **Methodology**: [Read More](./backend/multiagent_analysis/METODOLOGY_multiagent_en.md)

### 3. S&P 500 Scoring Engine
Filters the S&P 500 universe using a weighted formula (0-100) based on Piotroski, Altman, Beneish, and Magic Formula models.
*   **Methodology**: [Read More](./backend/Filter_sp500/METODOLOGY_filter_sp500_en.md)

## 🔄 Ideal Workflow for Swing Traders
1.  **Macro Check**: Use the Macro Dashboard to identify the market regime (Risk-on/off).
2.  **Asset Scanning**: Identify liquid assets with momentum via the S&P 500 Screener.
3.  **Deep Research**: Run the **Abyssal Probe** on a specific ticker to receive an institutional audit and verdict.

## ⚠️ Important Warning
This terminal is strictly optimized for **Individual Equities (Stocks)**, specifically from the **North American market (US)**. Using it for indices or other assets might result in incomplete data mapping.

## 🗺️ Roadmap
1.  **Robust Options Strategy**: Integration of a professional [OptionStrat-AI](https://github.com/EconomiaUNMSM/OptionStrat-AI) module.
2.  **Asset Classes**: Support for Commodities and ETFs.
3.  **Futures Integration**: Analysis of deep-sea futures contracts.
4.  **Multi-Model Support**: Compatibility with Anthropic (Claude), DeepSeek, and Local LLMs.
5.  **Interactive Configuration**: Real-time adjustment of agent roles and tools.
6.  **Advanced Quant Models**: Integration of pre-backtested ML and Deep Learning strategies.
7.  **Dynamic Weighting**: Custom configuration of weights for the S&P 500 scoring system.

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **Git**

### 1. Backend Setup
From the project root:
```bash
cd backend
# Create virtual environment
python -m venv venv
# Activate virtual environment (Windows)
venv\Scripts\activate
# Install dependencies
pip install -r requirements.txt
# Start server (API running on http://localhost:8000)
uvicorn api.main:app --reload
```

### 2. Frontend Setup
From the project root:
```bash
cd frontend
# Install dependencies
npm install
# Start development mode (App running on http://localhost:3000)
npm run dev
```

## 🔄 Repository Update Commands
To keep your terminal always up-to-date with the latest improvements:
```bash
# 1. Pull latest changes
git pull origin main

# 2. Update Backend dependencies
cd backend
# (Ensure venv is activated)
pip install -r requirements.txt
cd ..

# 3. Update Frontend dependencies
cd frontend
npm install
cd ..
```


## 👨‍💻 Author
**Luis Fabio Yoplac Cortez**
- [GitHub](https://github.com/EconomiaUNMSM)
- [LinkedIn](https://www.linkedin.com/in/luis-yoplac-cortez-10397328b)
