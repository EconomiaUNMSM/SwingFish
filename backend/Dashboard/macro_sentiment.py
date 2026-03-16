import pandas as pd
import requests
from fake_useragent import UserAgent
import xml.etree.ElementTree as ET
import yfinance as yf
from fredapi import Fred
import cot_reports as cot

# --- Helper para Headers Seguros ---
def get_safe_headers() -> dict:
    try:
        ua = UserAgent().chrome
    except Exception:
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    return {"User-Agent": ua}

# --- Calendario Económico ---
def get_economic_calendar() -> list:
    """
    Extrae el calendario económico de Forex Factory mediante su feed XML gratuito, 
    filtrando y devolviendo solo eventos de Alto Impacto en formato JSON (lista de diccionarios).
    """
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
    headers = get_safe_headers()
    eventos = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parsear XML
        root = ET.fromstring(response.content)
        eventos_totales = len(root.findall('event'))
        
        for event in root.findall('event'):
            impact_node = event.find('impact')
            impact = impact_node.text if impact_node is not None else ""
            
            # Filtrar solo Alto Impacto
            if impact and impact.strip().lower() == 'high':
                
                # Función segura para sacar texto de los tags
                def get_text(tag_name):
                    node = event.find(tag_name)
                    return node.text.strip() if node is not None and node.text is not None else ""
                    
                evento = {
                    "fecha": get_text('date'),
                    "hora": get_text('time'),
                    "moneda": get_text('country'),
                    "impacto": "Alto",
                    "evento": get_text('title'),
                    "esperado": get_text('forecast'),
                    "previo": get_text('previous')
                }
                eventos.append(evento)
                
        # Si no hay eventos de alto impacto pero sí leyó la tabla
        if not eventos and eventos_totales > 0:
            return [{"info": f"Se procesaron {eventos_totales} eventos esta semana, pero NINGUNO tiene 'Alto Impacto'."}]
            
    except Exception as e:
        return [{"error": f"Error de ejecución al extraer ForexFactory XML: {str(e)}"}]
        
    return eventos

# --- Eventos Económicos (FRED) ---
def get_economic_events(fred_api_key: str) -> dict:
    """
    Descarga indicadores macroeconómicos importantes usando FRED y datos del S&P500.
    Retorna un diccionario JSON estructurado con los datos históricos más recientes.
    """
    fred = Fred(api_key=fred_api_key)
    
    data_dict = {}
    try:
        # Tasa de Desempleo (UNRATE)
        unrate = fred.get_series(series_id="UNRATE").dropna()
        sp500 = yf.download("^GSPC", period="max", multi_level_index=False)["Close"].dropna()
        
        # Tomar solo los últimos 24 registros para ser concisos en backend
        data_dict["unemployment_vs_sp500"] = {
            "dates": unrate.tail(24).index.strftime("%Y-%m-%d").tolist(),
            "unemployment_rate": unrate.tail(24).tolist(),
            "sp500_close": sp500.reindex(unrate.tail(24).index, method='nearest').apply(lambda x: round(x, 2)).tolist()
        }
        
        indicator_codes = {
            "consumer_confidence": "UMCSENT",
            "gdp": "GDP",
            "cpi": "CPIAUCSL",
            "real_gdp": "A191RL1Q225SBEA"
        }
        
        for name, code in indicator_codes.items():
            series = fred.get_series(series_id=code).dropna().tail(24)
            data_dict[name] = {
                "dates": series.index.strftime("%Y-%m-%d").tolist(),
                "values": series.apply(lambda x: round(x, 4)).tolist()
            }
            
    except Exception as e:
         data_dict["error"] = str(e)
         
    return data_dict

# --- COT Report ---
def get_cot_report(market: str = "CANADIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE") -> list:
    """
    Extrae y calcula el reporte COT para el mercado especificado.
    Retorna la data en formato JSON (lista de diccionarios).
    """

    """
    Contratos Disponibles para la extracción.

    Divisas (Currencies):
        
    - USD INDEX - ICE FUTURES U.S.

    - CANADIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE

    - EURO FX/BRITISH POUND XRATE - CHICAGO MERCANTILE

    - EURO FX - CHICAGO MERCANTILE EXCHANGE

    - JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE

    - BRITISH POUND - CHICAGO MERCANTILE EXCHANGE

    - SWISS FRANC - CHICAGO MERCANTILE EXCHANGE

    - AUSTRALIAN DOLLAR - CHICAGO MERCANTILE

    - NZ DOLLAR - CHICAGO MERCANTILE EXCHANGE

    - MEXICAN PESO - CHICAGO MERCANTILE EXCHANGE

    - SO AFRICAN RAND - CHICAGO MERCANTILE EXCHANGE

    - BRAZILIAN REAL - CHICAGO MERCANTILE EXCHANGE

    Índices Bursátiles (Stock Indices):
        
    - S&P 500 Consolidated - CHICAGO MERCANTILE EXCHANGE

    - E-MINI S&P CONSU STAPLES INDEX - CHICAGO MERCANTILE EXCHANGE

    - E-MINI S&P ENERGY INDEX - CHICAGO MERCANTILE EXCHANGE

    - E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE

    - E-MINI S&P FINANCIAL INDEX - CHICAGO MERCANTILE EXCHANGE

    - E-MINI S&P MATERIALS INDEX - CHICAGO MERCANTILE EXCHANGE

    - E-MINI S&P TECHNOLOGY INDEX - CHICAGO MERCANTILE EXCHANGE

    - E-MINI S&P UTILITIES INDEX - CHICAGO MERCANTILE EXCHANGE

    - E-MINI S&P COMMUNICATION INDEX - CHICAGO MERCANTILE EXCHANGE

    - MICRO E-MINI S&P 500 INDEX - CHICAGO MERCANTILE EXCHANGE

    - ADJUSTED INT RATE S&P 500 TOTL - CHICAGO MERCANTILE EXCHANGE

    - NASDAQ-100 Consolidated - CHICAGO MERCANTILE EXCHANGE

    - NASDAQ MINI - CHICAGO MERCANTILE EXCHANGE

    - MICRO E-MINI NASDAQ-100 INDEX - CHICAGO MERCANTILE EXCHANGE

    - RUSSELL E-MINI - CHICAGO MERCANTILE EXCHANGE

    - EMINI RUSSELL 1000 VALUE INDEX - CHICAGO MERCANTILE EXCHANGE

    - MICRO E-MINI RUSSELL 2000 INDX - CHICAGO MERCANTILE EXCHANGE

    - NIKKEI STOCK AVERAGE - CHICAGO MERCANTILE EXCHANGE

    - NIKKEI STOCK AVERAGE YEN DENOM - CHICAGO MERCANTILE EXCHANGE

    - DJIA Consolidated - CHICAGO BOARD OF TRADE

    - DJIA x $5 - CHICAGO BOARD OF TRADE

    - DOW JONES U.S. REAL ESTATE IDX - CHICAGO BOARD OF TRADE

    - MICRO E-MINI DJIA (x$0.5) - CHICAGO BOARD OF TRADE

    - MSCI EAFE  - ICE FUTURES U.S.

    - MSCI EM INDEX - ICE FUTURES U.S.

    - E-MINI S&P 400 STOCK INDEX - CHICAGO MERCANTILE EXCHANGE

    - S&P 500 ANNUAL DIVIDEND INDEX - CHICAGO MERCANTILE EXCHANGE

    - S&P 500 QUARTERLY DIVIDEND IND - CHICAGO MERCANTILE EXCHANGE
        
    Soft Commodities:
        
    - BBG COMMODITY - CHICAGO BOARD OF TRADE
        
    Criptomonedas (Cryptocurrencies):
        
    - BITCOIN - CHICAGO MERCANTILE EXCHANGE

    - MICRO BITCOIN - CHICAGO MERCANTILE EXCHANGE

    - Nano Bitcoin  - LMX LABS LLC

    - ETHER CASH SETTLED - CHICAGO MERCANTILE EXCHANGE

    - MICRO ETHER  - CHICAGO MERCANTILE EXCHANGE

    - NANO ETHER - LMX LABS LLC

    - LITECOIN CASH - LMX LABS LLC

    - DOGECOIN - LMX LABS LLC

    - POLKADOT - LMX LABS LLC

    - CHAINLINK - LMX LABS LLC

    - AVALANCHE - LMX LABS LLC

    - 1K SHIB - LMX LABS LLC

    - NANO STELLAR - LMX LABS LLC

    - NANO SOLANA - LMX LABS LLC

    Otros (Others):
        
    - VIX FUTURES - CBOE FUTURES EXCHANGE

    - FED FUNDS - CHICAGO BOARD OF TRADE

    - UST BOND - CHICAGO BOARD OF TRADE

    - ULTRA UST BOND - CHICAGO BOARD OF TRADE

    - UST 2Y NOTE - CHICAGO BOARD OF TRADE

    - UST 10Y NOTE - CHICAGO BOARD OF TRADE

    - ULTRA UST 10Y - CHICAGO BOARD OF TRADE

    - MICRO 10 YEAR YIELD - CHICAGO BOARD OF TRADE

    - UST 5Y NOTE - CHICAGO BOARD OF TRADE 

    - EURO SHORT TERM RATE - CHICAGO MERCANTILE EXCHANGE

    - SOFR-3M - CHICAGO MERCANTILE EXCHANGE

    - SOFR-1M - CHICAGO MERCANTILE EXCHANGE

    - 2 YEAR ERIS SOFR SWAP - CHICAGO BOARD OF TRADE

    - 10 YEAR ERIS SOFR SWAP - CHICAGO BOARD OF TRADE

    - 5 YEAR ERIS SOFR SWAP - CHICAGO BOARD OF TRADE

    """
    try:
        df = cot.cot_all(cot_report_type="traders_in_financial_futures_fut")
        
        new_df = df.loc[:, ['Market_and_Exchange_Names',
                            'Report_Date_as_YYYY-MM-DD',
                            'Pct_of_OI_Dealer_Long_All',
                            'Pct_of_OI_Dealer_Short_All',
                            'Pct_of_OI_Lev_Money_Long_All',                    
                            'Pct_of_OI_Lev_Money_Short_All']]
                            
        new_df['Report_Date_as_YYYY-MM-DD'] = pd.to_datetime(new_df['Report_Date_as_YYYY-MM-DD'])
        new_df = new_df.sort_values(by='Report_Date_as_YYYY-MM-DD')
        data = new_df[new_df['Market_and_Exchange_Names'] == market].copy()
        
        if data.empty:
            return []
            
        data['Net_COT'] = (data['Pct_of_OI_Lev_Money_Long_All'] - \
                           data['Pct_of_OI_Lev_Money_Short_All']) - \
                          (data['Pct_of_OI_Dealer_Long_All'] -\
                           data['Pct_of_OI_Dealer_Short_All'])
                           
        # Tomar los últimos 20 registros
        data = data.tail(20)
        data['Report_Date_as_YYYY-MM-DD'] = data['Report_Date_as_YYYY-MM-DD'].dt.strftime('%Y-%m-%d')
        
        # Rellenar nulos
        data = data.fillna(0)
        return data.to_dict(orient="records")
    except Exception as e:
        return [{"error": str(e)}]
