"""
DataFetcher: Nodo secuencial que pre-carga TODOS los datos financieros
antes de que los analistas LLM inicien su ejecución en paralelo.

yfinance NO es thread-safe. Múltiples llamadas concurrentes a yf.download()
corrompen resultados silenciosamente (precios incorrectos, NaN, datos vacíos).
Este nodo resuelve el problema ejecutando todas las extracciones secuencialmente.
"""
import sys
import os

# Asegurar que multiagent_analysis y backend estén en sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))        # multiagent_analysis/
backend_dir = os.path.dirname(current_dir)                      # backend/
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from state import AnalystState
from agents.technical_agent import get_technical_indicators
from agents.risk_agent import get_risk_metrics
from agents.fundamental_agent import get_fundamental_and_insiders
from agents.macro_agent import get_macro_environment, get_upcoming_economic_events
from agents.options_agent import get_options_data
from agents.sentiment_agent import get_news_sentiment


def data_fetcher_node(state: AnalystState):
    """
    Pre-carga todos los datos financieros de forma SECUENCIAL.
    Almacena los resultados crudos en el state para que los nodos
    analistas los lean sin necesidad de llamar a yfinance.
    """
    ticker = state["ticker"]
    
    print("[DataFetcher] Extrayendo datos técnicos...")
    raw_tech = get_technical_indicators.invoke({"ticker": ticker})
    
    print("[DataFetcher] Extrayendo métricas de riesgo...")
    raw_risk = get_risk_metrics.invoke({"ticker": ticker})
    
    print("[DataFetcher] Extrayendo fundamentales e insiders...")
    raw_fund = get_fundamental_and_insiders.invoke({"ticker": ticker})
    
    print("[DataFetcher] Extrayendo entorno macro...")
    raw_macro = get_macro_environment.invoke({})
    
    print("[DataFetcher] Extrayendo calendario económico...")
    raw_cal = get_upcoming_economic_events.invoke({})
    
    print("[DataFetcher] Extrayendo cadena de opciones...")
    raw_opts = get_options_data.invoke({"ticker": ticker})
    
    print("[DataFetcher] Extrayendo sentimiento de noticias...")
    raw_sent = get_news_sentiment.invoke({"ticker": ticker})
    
    print("[DataFetcher] ✓ Todos los datos financieros pre-cargados exitosamente.")
    
    return {
        "raw_technical": raw_tech,
        "raw_risk": raw_risk,
        "raw_fundamental": raw_fund,
        "raw_macro": raw_macro,
        "raw_calendar": raw_cal,
        "raw_options": raw_opts,
        "raw_sentiment": raw_sent,
    }
