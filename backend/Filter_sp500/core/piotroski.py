"""
Implementación del Piotroski F-Score.
"""

import pandas as pd
import logging
from typing import Dict, Any, Optional
from ..models import FundamentalResult

logger = logging.getLogger(__name__)

class PiotroskiAnalyzer:
    """Calcula el F-Score (0-9) para evaluar la fortaleza financiera."""
    
    def analyze(self, ticker: str, financials: pd.DataFrame, balance_sheet: pd.DataFrame, cash_flow: pd.DataFrame) -> FundamentalResult:
        """
        Calcula los 9 indicadores de Piotroski.
        """
        try:
            # Validar datos mínimos
            if balance_sheet.shape[1] < 2 or financials.shape[1] < 2 or cash_flow.shape[1] < 1:
                return self._create_error_result("Datos insuficientes para F-Score")
            
            # Helpers para extracción segura (usando iloc para periodos: 0=actual, 1=previo)
            def safe_val(df, keys, period=0):
                for k in keys:
                    if k in df.index:
                        val = df.loc[k].iloc[period]
                        return float(val) if pd.notna(val) else 0.0
                return 0.0

            # Mapeo de claves
            keys = {
                'NetIncome': ['Net Income', 'Net Income Common Stockholders'],
                'TotalAssets': ['Total Assets'],
                'CashFlowOps': ['Operating Cash Flow', 'Net Cash Provided by Operating Activities'],
                'LongTermDebt': ['Long Term Debt'],
                'CurrAssets': ['Total current assets', 'Current Assets'],
                'CurrLiab': ['Total current liabilities', 'Current Liabilities'],
                'CommStock': ['Common Stock', 'Common Stock Issuance'],
                'GrossProfit': ['Gross Profit'],
                'TotRevenue': ['Total Revenue', 'Operating Revenue']
            }

            # Extracción de valores
            ni_0 = safe_val(financials, keys['NetIncome'], 0)
            ni_1 = safe_val(financials, keys['NetIncome'], 1)
            
            ta_0 = safe_val(balance_sheet, keys['TotalAssets'], 0)
            ta_1 = safe_val(balance_sheet, keys['TotalAssets'], 1)
            ta_2 = safe_val(balance_sheet, keys['TotalAssets'], 2) if balance_sheet.shape[1] > 2 else ta_1 # Fallback
            
            cfo_0 = safe_val(cash_flow, keys['CashFlowOps'], 0)
            
            ltd_0 = safe_val(balance_sheet, keys['LongTermDebt'], 0)
            ltd_1 = safe_val(balance_sheet, keys['LongTermDebt'], 1)
            
            ca_0 = safe_val(balance_sheet, keys['CurrAssets'], 0)
            ca_1 = safe_val(balance_sheet, keys['CurrAssets'], 1)
            cl_0 = safe_val(balance_sheet, keys['CurrLiab'], 0)
            cl_1 = safe_val(balance_sheet, keys['CurrLiab'], 1)
            
            cs_0 = safe_val(balance_sheet, keys['CommStock'], 0)
            cs_1 = safe_val(balance_sheet, keys['CommStock'], 1)
            
            gp_0 = safe_val(financials, keys['GrossProfit'], 0)
            gp_1 = safe_val(financials, keys['GrossProfit'], 1)
            rev_0 = safe_val(financials, keys['TotRevenue'], 0)
            rev_1 = safe_val(financials, keys['TotRevenue'], 1)

            # --- Cálculos de Puntos ---
            
            # Rentabilidad
            roa_0 = ni_0 / ((ta_0 + ta_1) / 2) if (ta_0 + ta_1) > 0 else 0
            roa_1 = ni_1 / ((ta_1 + ta_2) / 2) if (ta_1 + ta_2) > 0 else 0
            
            p1_roa_pos = 1 if roa_0 > 0 else 0
            p2_cfo_pos = 1 if cfo_0 > 0 else 0
            p3_roa_up = 1 if roa_0 > roa_1 else 0
            p4_quality = 1 if cfo_0 > ni_0 else 0
            
            # Apalancamiento / Liquidez
            p5_lev_down = 1 if ltd_0 < ltd_1 else 0
            
            cr_0 = ca_0 / cl_0 if cl_0 > 0 else 0
            cr_1 = ca_1 / cl_1 if cl_1 > 0 else 0
            p6_liq_up = 1 if cr_0 > cr_1 else 0
            
            p7_no_dilution = 1 if cs_0 <= cs_1 else 0
            
            # Eficiencia Operativa
            gm_0 = gp_0 / rev_0 if rev_0 > 0 else 0
            gm_1 = gp_1 / rev_1 if rev_1 > 0 else 0
            p8_gm_up = 1 if gm_0 > gm_1 else 0
            
            ato_0 = rev_0 / ta_0 if ta_0 > 0 else 0
            ato_1 = rev_1 / ta_1 if ta_1 > 0 else 0
            p9_ato_up = 1 if ato_0 > ato_1 else 0
            
            total_score = p1_roa_pos + p2_cfo_pos + p3_roa_up + p4_quality + p5_lev_down + p6_liq_up + p7_no_dilution + p8_gm_up + p9_ato_up
            
            # Interpretación
            interpretation = "Neutral"
            if total_score >= 8:
                interpretation = "Bullish" # Muy fuerte
            elif total_score <= 2:
                interpretation = "Bearish" # Muy débil
            
            details = {
                "roa_positive": bool(p1_roa_pos),
                "cfo_positive": bool(p2_cfo_pos),
                "roa_increasing": bool(p3_roa_up),
                "earnings_quality": bool(p4_quality),
                "leverage_decreasing": bool(p5_lev_down),
                "liquidity_improving": bool(p6_liq_up),
                "no_dilution": bool(p7_no_dilution),
                "gross_margin_improving": bool(p8_gm_up),
                "asset_turnover_improving": bool(p9_ato_up)
            }
            
            return FundamentalResult(
                score=float(total_score),
                max_score=9.0,
                details=details,
                interpretation=interpretation
            )
            
        except Exception as e:
            logger.error(f"Error en Piotroski para {ticker}: {e}")
            return self._create_error_result(str(e))

    def _create_error_result(self, msg: str) -> FundamentalResult:
        return FundamentalResult(score=0.0, max_score=9.0, details={"error": msg}, interpretation="Unknown")
