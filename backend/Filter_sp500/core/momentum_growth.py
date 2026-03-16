"""
Análisis de Crecimiento (Growth) y Momentum Fundamental/Técnico.
"""

import pandas as pd
import numpy as np
import logging
from ..models import FundamentalResult

logger = logging.getLogger(__name__)

class GrowthMomentumAnalyzer:
    """Evalúa el crecimiento histórico y el momentum de precio/fundamentales."""
    
    def analyze(self, ticker: str, financials: pd.DataFrame, history: pd.DataFrame) -> FundamentalResult:
        try:
            # Validar datos
            if financials.empty:
                return self._create_error_result("Datos financieros vacíos")
            
            # --- Crecimiento (Revenue & EPS) ---
            # Usamos CAGR de 3 años si es posible, sino YoY
            
            def get_cagr(series, years=3):
                if len(series) < years:
                    return 0.0
                start = series.iloc[years-1] # Más antiguo
                end = series.iloc[0] # Más reciente
                if start <= 0 or end <= 0: return 0.0
                return (end / start)**(1/years) - 1

            # Helpers
            def safe_series(df, keys):
                for k in keys:
                    if k in df.index:
                        return df.loc[k]
                return pd.Series()

            rev_series = safe_series(financials, ["Total Revenue", "Operating Revenue"])
            eps_series = safe_series(financials, ["Basic EPS", "Diluted EPS", "Net Income"]) # Fallback a Net Income si no hay EPS
            
            rev_cagr = get_cagr(rev_series, 3) * 100
            eps_cagr = get_cagr(eps_series, 3) * 100
            
            # Puntuación Crecimiento (Max 5 pts)
            # > 20% CAGR = 5 pts
            # > 10% CAGR = 3 pts
            # > 0%  CAGR = 1 pt
            
            growth_score = 0
            if rev_cagr > 20: growth_score += 2.5
            elif rev_cagr > 10: growth_score += 1.5
            elif rev_cagr > 0: growth_score += 0.5
            
            if eps_cagr > 20: growth_score += 2.5
            elif eps_cagr > 10: growth_score += 1.5
            elif eps_cagr > 0: growth_score += 0.5
            
            # --- Momentum de Precio (Relative Strength) ---
            # Comparar precio actual vs hace 3, 6, 12 meses
            momentum_score = 0
            if not history.empty and len(history) > 252:
                current_price = history["Close"].iloc[-1]
                price_3m = history["Close"].iloc[-63] if len(history) > 63 else current_price
                price_6m = history["Close"].iloc[-126] if len(history) > 126 else current_price
                price_12m = history["Close"].iloc[-252] if len(history) > 252 else current_price
                
                ret_3m = (current_price / price_3m) - 1
                ret_6m = (current_price / price_6m) - 1
                ret_12m = (current_price / price_12m) - 1
                
                # Puntuación Momentum (Max 5 pts)
                # Tendencia alcista sólida
                if ret_12m > 0: momentum_score += 1
                if ret_6m > 0: momentum_score += 1
                if ret_3m > 0: momentum_score += 1
                # Aceleración (3m > 6m) ? Opcional
                if ret_3m > 0.05: momentum_score += 2 # Momentum fuerte corto plazo

            # Total Score (Max 10)
            total_score = min(growth_score + momentum_score, 10.0)
            
            interpretation = "Neutral"
            if total_score >= 7:
                interpretation = "Bullish"
            elif total_score <= 3:
                interpretation = "Bearish"
                
            details = {
                "revenue_cagr_3y": rev_cagr,
                "eps_cagr_3y": eps_cagr,
                "momentum_score": momentum_score,
                "growth_score": growth_score
            }
            
            return FundamentalResult(
                score=float(total_score),
                max_score=10.0,
                details=details,
                interpretation=interpretation
            )

        except Exception as e:
            logger.error(f"Error Growth/Momentum para {ticker}: {e}")
            return self._create_error_result(str(e))

    def _create_error_result(self, msg: str) -> FundamentalResult:
        return FundamentalResult(score=0.0, max_score=10.0, details={"error": msg}, interpretation="Unknown")
