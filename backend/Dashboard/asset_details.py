import yfinance as yf
from yahooquery import Ticker
import pandas as pd

class AssetDetailsAnalyzer:
    """
    Concentra la información detallada de un activo (Ticker).
    Retorna la información en un diccionario (JSON) apta para FastAPI y el Dashboard.
    """
    
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.yq_ticker = Ticker(self.ticker)
        self.yf_ticker = yf.Ticker(self.ticker)
        
    def get_general_info(self) -> dict:
        """
        Obtiene la información general de un activo desde yfinance.
        """
        try:
            info = self.yf_ticker.info
            
            try:
                holders = self.yf_ticker.major_holders
                if holders is not None and not holders.empty and "insidersPercentHeld" in holders.index:
                    insiders_prop = round(float(holders.loc["insidersPercentHeld"].iloc[0]) * 100, 3)
                    inst_prop = round(float(holders.loc["institutionsPercentHeld"].iloc[0]) * 100, 3)
                else:
                    insiders_prop = "N/A"
                    inst_prop = "N/A"
            except Exception:
                insiders_prop = "N/A"
                inst_prop = "N/A"
                
            return {
                "nombre": info.get("longName") or info.get("displayName"),
                "precio_actual": info.get("currentPrice") or info.get("regularMarketPrice"),
                "volumen_promedio": info.get("averageVolume", "N/A"),
                "beta": info.get("beta", "N/A"),
                "estimacion_alta": info.get("targetHighPrice", "N/A"),
                "estimacion_media": info.get("targetMeanPrice", "N/A"),
                "estimacion_baja": info.get("targetLowPrice", "N/A"),
                "recomendacion": info.get("recommendationKey", "N/A"),
                "insiders_prop": insiders_prop,
                "inst_prop": inst_prop
            }
        except Exception as e:
            return {"error": f"Error al obtener información general de {self.ticker}: {str(e)}"}

    def get_insider_summary(self) -> dict:
        """
        Genera un resumen consolidado de las transacciones de insiders 
        y la estructura de propiedad utilizando yahooquery.
        """
        summary = {
            "has_insider_transactions": False,
            "insider_transactions": [],
            "has_institutional_ownership": False,
            "institutional_ownership": [],
            "profile": {},
            "major_holders": {}
        }
        
        try:
            # Perfil
            profile = self.yq_ticker.summary_profile
            if isinstance(profile, dict):
                summary["profile"] = profile.get(self.ticker, {})
                
            # Mayores accionistas
            holders = self.yq_ticker.major_holders
            if isinstance(holders, dict):
                summary["major_holders"] = holders.get(self.ticker, {})
                
            # Insider Transactions
            transactions = self.yq_ticker.insider_transactions
            if isinstance(transactions, pd.DataFrame) and not transactions.empty:
                summary["has_insider_transactions"] = True
                summary["insider_transactions"] = transactions.fillna("N/A").to_dict(orient="records")
            elif isinstance(transactions, dict) and self.ticker in transactions:
                df = transactions[self.ticker]
                if isinstance(df, pd.DataFrame) and not df.empty:
                    summary["has_insider_transactions"] = True
                    summary["insider_transactions"] = df.fillna("N/A").to_dict(orient="records")
                    
            # Propiedad Institucional
            ownership = self.yq_ticker.institution_ownership
            if isinstance(ownership, pd.DataFrame) and not ownership.empty:
                summary["has_institutional_ownership"] = True
                summary["institutional_ownership"] = ownership.fillna("N/A").head(20).to_dict(orient="records")
            elif isinstance(ownership, dict) and self.ticker in ownership:
                df = ownership[self.ticker]
                if isinstance(df, pd.DataFrame) and not df.empty:
                    summary["has_institutional_ownership"] = True
                    summary["institutional_ownership"] = df.fillna("N/A").head(20).to_dict(orient="records")
                    
        except Exception as e:
            summary["error"] = f"Error al generar resumen de insiders: {str(e)}"
            
        return summary
        
    def get_full_details(self) -> dict:
        """
        Retorna la información unificada del activo, 
        lista para exportarse por API.
        """
        return {
            "ticker": self.ticker,
            "general_info": self.get_general_info(),
            "insider_data": self.get_insider_summary()
        }
