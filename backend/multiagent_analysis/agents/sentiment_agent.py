import sys
import os
import pandas as pd
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

current_dir = os.path.dirname(os.path.abspath(__file__))              # agents/
multiagent_dir = os.path.dirname(current_dir)                         # multiagent_analysis/
backend_dir = os.path.dirname(multiagent_dir)                         # backend/

for p in [multiagent_dir, backend_dir]:
    if p not in sys.path:
        sys.path.append(p)

from data.finviz_finbert_news import FinvizFinbertScraper
from state import AnalystState
from tools import get_current_date

@tool
def get_news_sentiment(ticker: str) -> str:
    """
    Extrae noticias recientes de Finviz y evalúa su sentimiento mediante FinBERT.
    Devuelve un resumen de los titulares en formato string detallando el gap (pesimismo vs optimismo).
    """
    try:
        scraper = FinvizFinbertScraper()
        df = scraper.get_news_sentiment(ticker, max_news=15)
        
        if df.empty:
            return f"No se encontraron noticias recientes para {ticker}."
            
        promedio_gap = df["Gap"].mean()
        promedio_pos = df["pos_%"].mean()
        promedio_neg = df["neg_%"].mean()
        
        # Formatear el reporte crudo a partir del dataframe
        reporte = f"Resumen de Sentimiento (FinBERT) para {ticker}:\n"
        reporte += f"Sentimiento General:\n- Positivo Medio: {promedio_pos:.2f}%\n- Negativo Medio: {promedio_neg:.2f}%\n- Gap Medio (Optimismo neto): {promedio_gap:.2f}%\n\n"
        reporte += "Noticias Recientes (Gap individual):\n"
        
        for _, row in df.iterrows():
            reporte += f"- [{row['Fecha']} {row['Hora']}] {row['Titular']} (Gap: {row['Gap']}%)\n"
            
        return reporte
        
    except Exception as e:
        return f"Error en extracción y análisis NLP: {str(e)}"

def sentiment_analyst_node(state: AnalystState):
    """
    Nodo de LangGraph para el Analista de Sentimiento.
    Usa el motor de FinBERT para extraer la psique narrativa del mercado sobre el activo.
    """
    ticker = state["ticker"]
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    
    # Lee datos PRE-CARGADOS del state (extraídos secuencialmente por DataFetcher)
    prompt_context = state.get("raw_sentiment", "No hay datos de sentimiento disponibles.")
    current_date = get_current_date.invoke({})
    language = state.get("language", "en")
    
    lang_map = {
        "en": "English", "es": "Spanish (Español)", "pt": "Portuguese (Português)", "zh": "Chinese (Mandarin/Simplified)"
    }
    target_lang = lang_map.get(language, "English")
    
    system_prompt = f"""Eres un Analista de Sentimientos de Mercado Senior y NLP Specialist.
Fecha actual: {current_date}. 

REGLA DE IDIOMA: Debes escribir TODO tu reporte INTEGRAMENTE en {target_lang}.

Tu objetivo es auditar los recientes titulares de noticias sobre {ticker} y el análisis de sentimiento computado por 'FinBERT'.

Debes elaborar un reporte enfocado en:
- Qué narrativa prevalece (Optimismo/Pesimismo neto).
- ¿Qué expectativas está descontando ya el mercado?
- Vulnerabilidad emocional ante cisnes negros o eventos inminentes a juzgar por el tono mediático.

Evita repeticiones innecesarias de las noticias copiadas palabra por palabra, resume el "mood" general de manera perspicaz. Usa lenguaje analítico de fondos de inversión cuantitativos.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Sentimientos Crudos extraídos:\n{prompt_context}")
    ]
    
    response = llm.invoke(messages)
    combined = f"=== DATOS CRUDOS VERIFICADOS ===\n{prompt_context}\n\n=== INTERPRETACIÓN DEL ANALISTA ===\n{response.content}"
    return {"sentiment_analysis": combined}
