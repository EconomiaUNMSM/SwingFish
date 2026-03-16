"""
Scraper de Wikipedia para obtener componentes del S&P 500.

"""

import requests
import pandas as pd
from io import StringIO
from typing import List

class WikipediaScraper:
    """Obtiene listas de tickers de Wikipedia."""
    
    SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    
    @staticmethod
    def get_sp500_tickers() -> List[str]:
        """
        Descarga la tabla de componentes del S&P 500.
        Retorna lista de tickers (ej: ['AAPL', 'MSFT', ...]).
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }
        
        try:
            response = requests.get(WikipediaScraper.SP500_URL, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Pandas lee tablas HTML directamente
            dfs = pd.read_html(StringIO(response.text))
            
            # La primera tabla suele ser la de componentes
            df = dfs[0]
            
            # Wikipedia usa puntos en lugar de guiones (ej: BRK.B vs BRK-B)
            # Yahoo Finance usa guiones. Hacemos el reemplazo.
            tickers = df['Symbol'].str.replace('.', '-', regex=False).tolist()
            
            return tickers
            
        except Exception as e:
            print(f"Error scraping Wikipedia: {e}")
            # Fallback a lista básica si falla
            return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'SPY']

if __name__ == "__main__":
    tickers = WikipediaScraper.get_sp500_tickers()
    print(f"Encontrados {len(tickers)} tickers.")
    print(tickers[:10])
