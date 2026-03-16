"""
Implementación del Beneish M-Score para detectar manipulación contable.
"""

import pandas as pd
import numpy as np
import logging
from ..models import FundamentalResult

logger = logging.getLogger(__name__)

class BeneishAnalyzer:
    """Calcula el M-Score de Beneish."""
    
    def analyze(self, ticker: str, financials: pd.DataFrame, balance_sheet: pd.DataFrame, cash_flow: pd.DataFrame) -> FundamentalResult:
        try:
            # Validar al menos 2 periodos
            if balance_sheet.shape[1] < 2 or financials.shape[1] < 2:
                return self._create_error_result("Datos insuficientes (min 2 años)")
                
            def safe_val(df, keys, period=0):
                for k in keys:
                    if k in df.index:
                        val = df.loc[k].iloc[period]
                        return float(val) if pd.notna(val) else 0.0
                return 0.0

            # --- Extracción de Variables ---
            # Periodo actual (t) y previo (t-1)
            
            # Ventas
            rev_t = safe_val(financials, ["Total Revenue", "Operating Revenue"], 0)
            rev_t1 = safe_val(financials, ["Total Revenue", "Operating Revenue"], 1)
            
            # Costo de Ventas
            cogs_t = safe_val(financials, ["Cost Of Revenue", "Cost of Goods Sold"], 0)
            cogs_t1 = safe_val(financials, ["Cost Of Revenue", "Cost of Goods Sold"], 1)
            
            # Cuentas por Cobrar
            rec_t = safe_val(balance_sheet, ["Net Receivables", "Accounts Receivable"], 0)
            rec_t1 = safe_val(balance_sheet, ["Net Receivables", "Accounts Receivable"], 1)
            
            # Activos Corrientes
            ca_t = safe_val(balance_sheet, ["Total current assets", "Current Assets"], 0)
            ca_t1 = safe_val(balance_sheet, ["Total current assets", "Current Assets"], 1)
            
            # Propiedad Planta y Equipo (PPE)
            ppe_t = safe_val(balance_sheet, ["Gross PPE", "Property Plant Equipment Net"], 0)
            ppe_t1 = safe_val(balance_sheet, ["Gross PPE", "Property Plant Equipment Net"], 1)
            
            # Activos Totales
            ta_t = safe_val(balance_sheet, ["Total Assets"], 0)
            ta_t1 = safe_val(balance_sheet, ["Total Assets"], 1)
            
            # Depreciación (Acumulada o Gasto?)
            # Beneish usa Depreciación (Gasto) / (PPE + Depreciación)
            # Si no tenemos gasto de depreciación directo, aproximamos con cambio en acumulada o usamos CashFlow
            dep_exp_t = safe_val(cash_flow, ["Depreciation", "Depreciation And Amortization"], 0)
            dep_exp_t1 = safe_val(cash_flow, ["Depreciation", "Depreciation And Amortization"], 1)
            
            # Gastos SG&A
            sga_t = safe_val(financials, ["Selling General And Administration", "Operating Expense"], 0)
            sga_t1 = safe_val(financials, ["Selling General And Administration", "Operating Expense"], 1)
            
            # Utilidad Neta y CFO (para TATA)
            ni_t = safe_val(financials, ["Net Income", "Net Income Common Stockholders"], 0)
            cfo_t = safe_val(cash_flow, ["Operating Cash Flow", "Net Cash Provided by Operating Activities"], 0)
            
            # Pasivos
            cl_t = safe_val(balance_sheet, ["Total current liabilities", "Current Liabilities"], 0)
            cl_t1 = safe_val(balance_sheet, ["Total current liabilities", "Current Liabilities"], 1)
            ltd_t = safe_val(balance_sheet, ["Long Term Debt"], 0)
            ltd_t1 = safe_val(balance_sheet, ["Long Term Debt"], 1)

            # Divisiones seguras
            def safe_div(n, d):
                return n / d if d != 0 and pd.notna(d) else 0.0

            # --- Índices Beneish ---
            
            # 1. DSRI: Days Sales in Receivables Index
            # (Rec_t / Rev_t) / (Rec_t1 / Rev_t1)
            dsri = safe_div(safe_div(rec_t, rev_t), safe_div(rec_t1, rev_t1))
            
            # 2. GMI: Gross Margin Index
            # ((Rev_t1 - Cogs_t1) / Rev_t1) / ((Rev_t - Cogs_t) / Rev_t)
            gm_t = safe_div(rev_t - cogs_t, rev_t)
            gm_t1 = safe_div(rev_t1 - cogs_t1, rev_t1)
            gmi = safe_div(gm_t1, gm_t)
            
            # 3. AQI: Asset Quality Index
            # (1 - (CA_t + PPE_t)/TA_t) / (1 - (CA_t1 + PPE_t1)/TA_t1)
            # Activos no corrientes no PPE
            aq_t = 1 - safe_div(ca_t + ppe_t, ta_t)
            aq_t1 = 1 - safe_div(ca_t1 + ppe_t1, ta_t1)
            aqi = safe_div(aq_t, aq_t1)
            
            # 4. SGI: Sales Growth Index
            sgi = safe_div(rev_t, rev_t1)
            
            # 5. DEPI: Depreciation Index
            # (Dep_t1 / (PPE_t1 + Dep_t1)) / (Dep_t / (PPE_t + Dep_t))
            rate_t = safe_div(dep_exp_t, ppe_t + dep_exp_t)
            rate_t1 = safe_div(dep_exp_t1, ppe_t1 + dep_exp_t1)
            depi = safe_div(rate_t1, rate_t)
            
            # 6. SGAI: SG&A Index
            # (SGA_t / Rev_t) / (SGA_t1 / Rev_t1)
            sgai = safe_div(safe_div(sga_t, rev_t), safe_div(sga_t1, rev_t1))
            
            # 7. LVGI: Leverage Index
            # ((CL_t + LTD_t) / TA_t) / ((CL_t1 + LTD_t1) / TA_t1)
            lev_t = safe_div(cl_t + ltd_t, ta_t)
            lev_t1 = safe_div(cl_t1 + ltd_t1, ta_t1)
            lvgi = safe_div(lev_t, lev_t1)
            
            # 8. TATA: Total Accruals to Total Assets
            # (NI_t - CFO_t) / TA_t
            tata = safe_div(ni_t - cfo_t, ta_t)
            
            # Fórmula M-Score (8 variables)
            m_score = -4.84 + 0.92*dsri + 0.528*gmi + 0.404*aqi + 0.892*sgi + 0.115*depi - 0.172*sgai + 4.679*tata - 0.327*lvgi
            
            # Interpretación
            # M > -1.78: Alta probabilidad de manipulación (Rojo)
            # M < -2.22: Baja probabilidad (Verde)
            # Entre medio: Zona Gris (Amarillo)
            
            risk_level = "Low"
            interpretation = "Bullish" # Low risk is bullish
            
            normalized_score = 0.0 # 0-10, donde 10 es "Muy seguro"
            
            if m_score > -1.78:
                risk_level = "High"
                interpretation = "Bearish" # High manipulation risk
                normalized_score = 0.0
            elif m_score < -2.22:
                risk_level = "Low"
                interpretation = "Bullish"
                normalized_score = 10.0
            else:
                risk_level = "Medium"
                interpretation = "Neutral"
                normalized_score = 5.0
                
            details = {
                "m_score": float(m_score),
                "risk_level": risk_level,
                "components": {
                    "dsri": dsri, "gmi": gmi, "aqi": aqi, "sgi": sgi,
                    "depi": depi, "sgai": sgai, "lvgi": lvgi, "tata": tata
                }
            }
            
            return FundamentalResult(
                score=normalized_score,
                max_score=10.0,
                details=details,
                interpretation=interpretation
            )

        except Exception as e:
            logger.error(f"Error en Beneish para {ticker}: {e}")
            return self._create_error_result(str(e))

    def _create_error_result(self, msg: str) -> FundamentalResult:
        return FundamentalResult(score=0.0, max_score=10.0, details={"error": msg}, interpretation="Unknown")
