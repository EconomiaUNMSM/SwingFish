import sys
import os
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

current_dir = os.path.dirname(os.path.abspath(__file__))              # agents/
multiagent_dir = os.path.dirname(current_dir)                         # multiagent_analysis/
if multiagent_dir not in sys.path:
    sys.path.append(multiagent_dir)

from state import AnalystState
from tools import get_current_date

def manager_node(state: AnalystState):
    """
    Nodo Final de LangGraph. 
    El Portfolio Manager recibe el State completo con los reportes
    de todos los analistas especializados y expide un mandato ejecutivo.
    """
    ticker = state["ticker"]
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)  # Usamos el modelo mayor (gpt-4o) para el manager para un razonamiento superior
    
    current_date = get_current_date.invoke({})
    language = state.get("language", "en")
    
    lang_map = {
        "en": "English", "es": "Spanish (Español)", "pt": "Portuguese (Português)", "zh": "Chinese (Mandarin/Simplified)"
    }
    target_lang = lang_map.get(language, "English")
    
    # Recabamos los reportes del State
    tech = state.get("technical_analysis", "No disponible")
    sent = state.get("sentiment_analysis", "No disponible")
    macro = state.get("macro_analysis", "No disponible")
    opt = state.get("options_analysis", "No disponible")
    risk = state.get("risk_analysis", "No disponible")
    fund = state.get("fundamental_analysis", "No disponible")
    
    system_prompt = f"""Eres el Portfolio Manager Principal y Jefe de Swing Trading de un Fondo de Cobertura de Alto Nivel.
Fecha actual: {current_date}. 

REGLA DE IDIOMA: Debes escribir TODO tu reporte INTEGRAMENTE en {target_lang}.

Tu comité de 6 analistas cuantitativos especialistas acaba de entregarte sus reportes ejecutivos sobre el activo {ticker}.

REGLA ABSOLUTAMENTE CRÍTICA: 
Cada reporte contiene una sección "=== DATOS CRUDOS VERIFICADOS ===" con números reales extraídos de APIs financieras.
SIEMPRE usa los valores numéricos de esa sección como fuente de verdad. Si la "INTERPRETACIÓN DEL ANALISTA" 
contradice los datos crudos, IGNORA la interpretación y usa los datos crudos.

Debes sintetizar toda la información y tomar una DECISIÓN DE INVERSIÓN FINAL Y DIRECTIVA.
Tu salida final debe ser un reporte maestro (Executive Summary) estructurado de la siguiente manera:

1. THE VERDICT (El Veredicto): [LONG / SHORT / CASH (No operar)]
2. SÍNTESIS DEL COMITÉ MÚLTIPLE: 
   Sintetiza de forma cruzada usando SOLO los datos crudos verificados.
3. PROTOCOLO DE EXPOSICIÓN Y GESTIÓN DE RIESGO:
   - Tentativa de Take Profit (TP) y Stop Loss (SL) lógicos fundamentados en el análisis técnico de Ichimoku, el rango dictado por el ATR (Average True Range), y el Expected Move de opciones. USA los valores exactos de los datos crudos para definir la volatilidad esperada.
   - Duración (Time window) estimada para el Swing Trade.
   - Peso en el portafolio (Allocation size %): basado en el VaR/CVaR de los DATOS CRUDOS del Risk Agent.

Escribe con autoridad absoluta, concisión institucional y profesionalismo extremo. Cero introducciones conversacionales.
    """
    
    human_prompt = f"""
--- REPORTE TÉCNICO ---
{tech}

--- REPORTE DE SENTIMIENTO ---
{sent}

--- REPORTE MACROECONÓMICO ---
{macro}

--- REPORTE DE OPCIONES ---
{opt}

--- REPORTE DE RIESGO ---
{risk}

--- REPORTE FUNDAMENTAL ---
{fund}

Con base en lo anterior, emite el Executive Summary y mandato de trading para {ticker}.
"""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ]
    
    response = llm.invoke(messages)
    return {"manager_decision": response.content}
