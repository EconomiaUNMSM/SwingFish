"""
Implementación de la Fórmula Mágica de Greenblatt.
"""

import pandas as pd
import logging
from ..models import FundamentalResult

logger = logging.getLogger(__name__)

class MagicFormulaAnalyzer:
    """Calcula Earnings Yield y Return on Capital (ROC)."""
    
    def analyze(self, ticker: str, financials: pd.DataFrame, balance_sheet: pd.DataFrame, info: dict) -> FundamentalResult:
        try:
            # Helpers de extracción
            def safe_val(df, keys, period=0):
                for k in keys:
                    if k in df.index:
                        val = df.loc[k].iloc[period]
                        return float(val) if pd.notna(val) else 0.0
                return 0.0
            
            # --- Extracción (Periodo más reciente) ---
            ebit = safe_val(financials, ["EBIT", "Operating Income"]) # TTM idealmente
            
            # Capital Empleado = Total Assets - Current Liabilities (exceso de caja no se resta a veces, pero usaremos la fórmula clásica)
            ta = safe_val(balance_sheet, ["Total Assets"])
            cl = safe_val(balance_sheet, ["Total current liabilities", "Current Liabilities"])
            
            if ta == 0:
                return self._create_error_result("Total Assets es 0")

            capital_employed = ta - cl
            
            # Earnings Yield = EBIT / Enterprise Value
            market_cap = info.get("marketCap", 0.0)
            total_debt = safe_val(balance_sheet, ["Total Debt"])
            cash = safe_val(balance_sheet, ["Cash And Cash Equivalents"])
            
            if market_cap == 0:
                return self._create_error_result("Market Cap 0")

            enterprise_value = market_cap + total_debt - cash
            
            if capital_employed <= 0:
                capital_employed = ta * 0.1 # Fallback para evitar div/0 (asumimos 10% de activos si working capital negativo)
            
            if enterprise_value <= 0:
                enterprise_value = market_cap # Fallback simple

            # --- Cálculos ---
            roc = ebit / capital_employed
            earnings_yield = ebit / enterprise_value
            
            # --- Puntuación (Heurística) ---
            # ROC > 20% es excelente (5 pts)
            # EY > 10% es excelente (5 pts)
            
            score_roc = min(roc / 0.20, 1.0) * 5.0 if roc > 0 else 0
            score_ey = min(earnings_yield / 0.10, 1.0) * 5.0 if earnings_yield > 0 else 0
            
            total_score = score_roc + score_ey # Max 10.0
            
            interpretation = "Neutral"
            if total_score > 7:
                interpretation = "Bullish"
            elif total_score < 3:
                interpretation = "Bearish"
                
            details = {
                "roc_pct": roc * 100,
                "earnings_yield_pct": earnings_yield * 100,
                "ebit": ebit,
                "capital_employed": capital_employed,
                "enterprise_value": enterprise_value
            }
            
            return FundamentalResult(
                score=float(total_score),
                max_score=10.0,
                details=details,
                interpretation=interpretation
            )

        except Exception as e:
            logger.error(f"Error Magic Formula para {ticker}: {e}")
            return self._create_error_result(str(e))

    def _create_error_result(self, msg: str) -> FundamentalResult:
        return FundamentalResult(score=0.0, max_score=10.0, details={"error": msg}, interpretation="Unknown")
