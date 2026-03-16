from typing import TypedDict, Dict, Any

class AnalystState(TypedDict, total=False):
    """
    Estado global compartido entre los analistas del grafo.
    
    Flujo:
    1. DataFetcher pre-carga TODOS los datos financieros secuencialmente (yfinance no es thread-safe).
    2. Cada analista lee los datos pre-cargados del state y solo ejecuta su LLM.
    3. El Manager sintetiza las 6 interpretaciones.
    """
    ticker: str
    
    # Datos crudos pre-cargados por el DataFetcher (secuencial, thread-safe)
    raw_technical: str
    raw_risk: str
    raw_fundamental: str
    raw_macro: str
    raw_calendar: str
    raw_options: str
    raw_sentiment: str
    
    # Análisis generados por cada LLM (paralelo, thread-safe)
    technical_analysis: str
    sentiment_analysis: str
    macro_analysis: str
    options_analysis: str
    risk_analysis: str
    fundamental_analysis: str
    
    # La respuesta final del manager
    manager_decision: str
    
    # Configuración de salida
    language: str # 'en', 'es', 'pt', 'zh'
