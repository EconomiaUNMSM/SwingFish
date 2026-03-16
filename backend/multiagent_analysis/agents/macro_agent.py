import os
import sys
import pandas as pd
import yfinance as yf
import requests
import xml.etree.ElementTree as ET
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

current_dir = os.path.dirname(os.path.abspath(__file__))              # agents/
multiagent_dir = os.path.dirname(current_dir)                         # multiagent_analysis/
backend_dir = os.path.dirname(multiagent_dir)                         # backend/

for p in [multiagent_dir, backend_dir]:
    if p not in sys.path:
        sys.path.append(p)

from state import AnalystState
from tools import get_current_date

@tool
def get_macro_environment() -> str:
    """
    Obtiene referencias macroeconómicas generales de mercado para evaluar régimen.
    Utiliza yfinance para VIX (Volatilidad), Bonos a 10 años (TNX), e indicadores de crédito corporativo (LQD/HYG).
    """
    try:
        reporte = "ENTORNO MACROECONÓMICO Y RÉGIMEN ACTUAL:\n"
        
        # Función helper segura para extraer último valor
        def safe_last(symbol, label):
            try:
                raw = yf.download(symbol, period="5d", progress=False, multi_level_index=False)
                if raw.empty:
                    return f"- {label}: No disponible\n", 0.0
                val = float(raw['Close'].iloc[-1])
                return f"- {label}: {val:.2f}\n", val
            except Exception:
                return f"- {label}: Error\n", 0.0
        
        # 1. Volatilidad (VIX)
        vix_str, vix_val = safe_last("^VIX", "Índice de Volatilidad (VIX)")
        reporte += vix_str
            
        # 2. Rendimiento Bonos a 10 años (TNX)
        tnx_str, tnx_val = safe_last("^TNX", "Rendimiento Tesoro 10Y (%)")
        reporte += tnx_str
            
        # 3. Spread de crédito proxy (HYG / LQD ratio)
        try:
            lqd_raw = yf.download("LQD", period="5d", progress=False, multi_level_index=False)
            hyg_raw = yf.download("HYG", period="5d", progress=False, multi_level_index=False)
            lqd_val = float(lqd_raw['Close'].iloc[-1])
            hyg_val = float(hyg_raw['Close'].iloc[-1])
            ratio = hyg_val / lqd_val
            reporte += f"- Ratio High Yield / Inv. Grade (HYG/LQD): {ratio:.3f} (>1 = apetito al riesgo)\n"
        except Exception:
            reporte += "- Ratio HYG/LQD: No disponible\n"
        
        # 4. DXY (Dollar Index proxy via UUP ETF)
        dxy_str, _ = safe_last("UUP", "Fortaleza del Dólar (UUP ETF)")
        reporte += dxy_str

        return reporte
    except Exception as e:
        return f"Error extrayendo contexto macro: {str(e)}"

@tool
def get_upcoming_economic_events() -> str:
    """
    Extrae los eventos de alto impacto de la semana actual desde el calendario de Forex Factory (XML feed gratuito).
    Permite al analista macro considerar riesgos por datos próximos a publicarse.
    """
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        eventos_high = []
        
        for event in root.findall('event'):
            impact_node = event.find('impact')
            impact = impact_node.text.strip().lower() if impact_node is not None and impact_node.text else ""
            
            if impact == 'high':
                def get_text(tag):
                    n = event.find(tag)
                    return n.text.strip() if n is not None and n.text else ""
                
                eventos_high.append({
                    "fecha": get_text('date'),
                    "hora": get_text('time'),
                    "moneda": get_text('country'),
                    "evento": get_text('title'),
                    "esperado": get_text('forecast'),
                    "previo": get_text('previous')
                })
        
        if not eventos_high:
            return "No hay eventos de alto impacto programados esta semana."
            
        reporte = "EVENTOS DE ALTO IMPACTO ESTA SEMANA:\n"
        for ev in eventos_high:
            reporte += f"- [{ev['fecha']} {ev['hora']}] {ev['moneda']}: {ev['evento']} | Esperado: {ev['esperado']} | Previo: {ev['previo']}\n"
        return reporte
        
    except Exception as e:
        return f"Error extrayendo calendario económico: {str(e)}"

def macro_analyst_node(state: AnalystState):
    """
    Nodo de LangGraph para el Analista Macro.
    Evalúa el régimen del mercado actual basándose en volatilidad, crédito, liquidez, riesgo sistémico
    y eventos económicos próximos de alto impacto.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    
    macro_context = state.get("raw_macro", "No hay datos macro disponibles.")
    calendar_context = state.get("raw_calendar", "No hay calendario disponible.")
    current_date = get_current_date.invoke({})
    language = state.get("language", "en")
    
    lang_map = {
        "en": "English", "es": "Spanish (Español)", "pt": "Portuguese (Português)", "zh": "Chinese (Mandarin/Simplified)"
    }
    target_lang = lang_map.get(language, "English")
    
    system_prompt = f"""Eres un Analista Macroeconómico Institucional.
Fecha actual: {current_date}. 

REGLA DE IDIOMA: Debes escribir TODO tu reporte INTEGRAMENTE en {target_lang}.

Tu objetivo es auditar el régimen general del mercado para orientar la exposición de un portafolio de Swing Trading.

Debes estructurar un reporte respondiendo a:
- Estado del Régimen (Risk-on, Risk-off, Transición).
- Nivel de estrés crediticio y de volatilidad.
- Expectativas sobre flujos hacia renta variable.
- Riesgos por eventos económicos inminentes que puedan alterar la tesis macro.

Usa lenguaje directo de gestor de fondos. Justifica tu lectura de régimen con los números del reporte.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Datos Macro en Tiempo Real:\n{macro_context}\n\nCalendario Económico Próximo:\n{calendar_context}")
    ]
    
    response = llm.invoke(messages)
    raw = f"{macro_context}\n{calendar_context}"
    combined = f"=== DATOS CRUDOS VERIFICADOS ===\n{raw}\n\n=== INTERPRETACIÓN DEL ANALISTA ===\n{response.content}"
    return {"macro_analysis": combined}
