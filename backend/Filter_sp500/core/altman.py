"""
Implementación del Altman Z-Score (para manufactura y no manufactura).
"""

import pandas as pd
import numpy as np
import logging
from ..models import FundamentalResult

logger = logging.getLogger(__name__)

class AltmanAnalyzer:
    """Calcula el Z-Score para predecir riesgo de quiebra."""
    
    def analyze(self, ticker: str, financials: pd.DataFrame, balance_sheet: pd.DataFrame, info: dict) -> FundamentalResult:
        try:
            # Validar datos mínimos
            if balance_sheet.empty or financials.empty:
                return self._create_error_result("Datos vacíos")
                
            def safe_val(df, keys):
                for k in keys:
                    if k in df.index:
                        val = df.loc[k].iloc[0] # Usar el más reciente
                        return float(val) if pd.notna(val) else 0.0
                return 0.0
            
            # Extracción de Datos
            cur_assets = safe_val(balance_sheet, ["Total current assets", "Current Assets"])
            cur_liab = safe_val(balance_sheet, ["Total current liabilities", "Current Liabilities"])
            tot_assets = safe_val(balance_sheet, ["Total Assets"])
            tot_liab = safe_val(balance_sheet, ["Total Liabilities Net Minority Interest", "Total Liabilities"])
            retained_earn = safe_val(balance_sheet, ["Retained Earnings", "Retained Earnings (Accumulated Deficit)", "Deficit"])
            ebit = safe_val(financials, ["EBIT", "Operating Income"])
            market_cap = info.get("marketCap", 0.0)
            
            if tot_assets == 0 or tot_liab == 0:
                return self._create_error_result("Activos o Pasivos Totales son 0")

            # --- Altman Z-Score Original (Manufactura) ---
            # X1 = (Working Capital) / Total Assets
            x1 = (cur_assets - cur_liab) / tot_assets
            
            # X2 = Retained Earnings / Total Assets
            x2 = retained_earn / tot_assets
            
            # X3 = EBIT / Total Assets
            x3 = ebit / tot_assets
            
            # X4 = Market Value of Equity / Total Liabilities
            x4 = market_cap / tot_liab
            
            # X5 = Sales / Total Assets (Omitido en la versión Z'' Double Prime para no manufacturas emergentes, pero usaremos la Z' estándar o Z normal)
            # Para generalizar, usaremos Z-Score Double Prime (Z'') que es más robusta para empresas de servicios y no-manufactura.
            
            # Fórmula Z'' (Double Prime) - Adaptada para empresas no manufactureras y mercados emergentes
            # Z'' = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4
            # X1 = (Current Assets - Current Liabilities) / Total Assets
            # X2 = Retained Earnings / Total Assets
            # X3 = EBIT / Total Assets
            # X4 = Book Value of Equity / Total Liabilities -> A menudo se usa Market Value si Book no está disponible o para adaptar, pero la fórmula original Z'' usa Book Value. 
            # Sin embargo, el script original `Z_Score_Altman.py` usaba Market Cap en X4 y la fórmula 6.56...
            # Seguiremos la lógica del script original del usuario para mantener consistencia.
            
            z_score = 6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4
            
            # Interpretación basada en Z''
            # > 2.60: Zona Segura ("Safe")
            # 1.10 - 2.60: Zona Gris ("Grey")
            # < 1.10: Zona de Peligro ("Distress")
            
            rating = "Distress"
            score_type = "Bearish"
            
            if z_score > 2.60:
                rating = "Safe"
                score_type = "Bullish"
            elif z_score > 1.10:
                rating = "Grey"
                score_type = "Neutral"
            
            # Mapeo a puntaje normalizado (0-10 para consistencia)
            # Safe (>2.6) -> 10
            # Grey (1.1 - 2.6) -> 5
            # Distress (<1.1) -> 0
            
            normalized_score = 0.0
            if z_score > 2.6:
                normalized_score = 10.0
            elif z_score > 1.1:
                # Interpolación lineal entre 1.1 y 2.6 para dar 0 a 10? No, simplifiquemos.
                # Grey Zone interpolar entre 4 y 7
                normalized_score = 5.0
            else:
                normalized_score = 0.0 # Riesgo alto
                
            details = {
                "z_score": float(z_score),
                "zone": rating,
                "components": {
                    "X1_Liquidity": x1,
                    "X2_Accumulated_Earnings": x2,
                    "X3_Profitability": x3,
                    "X4_Leverage": x4
                }
            }
            
            return FundamentalResult(
                score=normalized_score,
                max_score=10.0, # Normalizado para nuestro sistema
                details=details,
                interpretation=score_type
            )

        except Exception as e:
            logger.error(f"Error en Altman para {ticker}: {e}")
            return self._create_error_result(str(e))

    def _create_error_result(self, msg: str) -> FundamentalResult:
        return FundamentalResult(score=0.0, max_score=10.0, details={"error": msg}, interpretation="Unknown")
