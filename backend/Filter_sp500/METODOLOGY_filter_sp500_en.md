# S&P 500 Filter Methodology | Scoring Engine

## 1. Overview
The **Filter_sp500** module synthesizes complex corporate health into a single **Final Score (0-100)** by triangulating data from 5 proven quantitative models.

### 💡 Combating Subjectivity
Generic AI analysis often summarizes "market sentiment" without looking at balance sheet quality. SwingFish **combats hallucinations** by enforcing hard mathematical rules (Altman, Piotroski, Beneish) that cannot be "debated" by an LLM.

## 2. Weighted Sub-Models
1.  **Piotroski F-Score (15%)**: Financial strength based on 9 binary criteria.
2.  **Altman Z-Score (10%)**: Bankruptcy risk prediction.
3.  **Beneish M-Score (5%)**: Forensic accounting for manipulation detection.
4.  **Magic Formula (20%)**: Quality (ROC) and Yield (EY) synergy.
5.  **Growth & Momentum (30%)**: Revenue targets and trend validation.
6.  **Analyst Upside (20%)**: Wall Street targets vs current price.

## 3. Practical Utility
For a swing trader, the score acts as a **Liquidity and Quality Shield**. No matter how good the technical setup looks, if the engine triggers an `ACCOUNTING_RISK` flag, the asset is discarded.

---
**⚠️ Warning**: Designed specifically for **Individual US Equities**. Asset classes like REITs or Financials (Banks) may produce skewed results due to different balance sheet structures.
