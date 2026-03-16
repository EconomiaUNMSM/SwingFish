"""
Scraper robusto de datos fundamentales usando yfinance.
Maneja reintentos, caché simple y fallback de datos transitorios.
"""

import yfinance as yf
import pandas as pd
import time
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

class YFinanceScraper:
    """Descarga datos financieros, balances, flujos de caja y precios históricos."""
    
    def __init__(self, retries: int = 3, delay: float = 1.0):
        self.retries = retries
        self.delay = delay
        # Caché en memoria: almacena el último fetch válido por ticker
        self._cache: Dict[str, Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]] = {}

    def fetch_full_data(self, ticker: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        """
        Descarga TODO lo necesario para el análisis fundamental.
        Si yfinance devuelve datos vacíos pero tenemos caché válido, usa el caché.
        
        Returns:
            (financials, balance_sheet, cash_flow, history_prices, info_dict)
        """
        # Pausa obligatoria entre solicitudes para evitar bloqueo de IP
        time.sleep(1.5)
        
        try:
            t = yf.Ticker(ticker)
            
            # 1. Estados Financieros (Annual)
            fin = t.financials
            bs = t.balancesheet
            cf = t.cashflow
            
            # 2. Información General
            try:
                info = t.info
            except Exception:
                info = {}
            
            # 3. Precios Históricos
            hist = t.history(period="2y")
            
            # Validar integridad mínima
            if fin.empty and bs.empty:
                # yfinance devolvió vacío — podría ser ventana post-earnings o soft-ban
                if ticker in self._cache:
                    logger.warning(
                        f"{ticker}: yfinance devolvió datos financieros vacíos. "
                        f"Usando datos cacheados de la última descarga exitosa."
                    )
                    cached = self._cache[ticker]
                    # Actualizamos solo los precios históricos (esos sí suelen funcionar)
                    if not hist.empty:
                        return cached[0], cached[1], cached[2], hist, cached[4]
                    return cached
                else:
                    logger.warning(f"Datos vacíos para {ticker} y sin caché disponible.")
                    return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}
            
            # Datos válidos — actualizar caché
            self._cache[ticker] = (fin, bs, cf, hist, info)
            
            return fin, bs, cf, hist, info
            
        except Exception as e:
            msg = str(e)
            if "Too Many Requests" in msg or "429" in msg:
                logger.critical(f"RATE LIMIT (429) detectado en {ticker}. Deteniendo ejecución masiva.")
                raise ConnectionError("RATE_LIMIT_HIT")
            
            # Otros errores — intentar fallback a caché
            if ticker in self._cache:
                logger.warning(f"Error en {ticker}: {e}. Usando datos cacheados como fallback.")
                return self._cache[ticker]
            
            logger.warning(f"Error obteniendo datos de {ticker}: {e}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}

    def get_analyst_upside(self, info: dict, current_price: float) -> float:
        """Calcula el upside potencial basado en target price de analistas."""
        try:
            target_mean = info.get("targetMeanPrice")
            target_median = info.get("targetMedianPrice")
            
            # Preferir Median, luego Mean
            target = target_median if target_median else target_mean
            
            if not target or not current_price:
                return 0.0
                
            upside = (target - current_price) / current_price
            return upside * 100 # Porcentaje
            
        except Exception:
            return 0.0
