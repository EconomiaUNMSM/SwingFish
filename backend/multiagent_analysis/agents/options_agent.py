import sys
import os
import numpy as np
import yfinance as yf
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))              # agents/
multiagent_dir = os.path.dirname(current_dir)                         # multiagent_analysis/
if multiagent_dir not in sys.path:
    sys.path.append(multiagent_dir)

from state import AnalystState
from tools import get_current_date

@tool
def get_options_data(ticker: str) -> str:
    """
    Extrea datos del mercado de opciones vía yfinance:
    - Volumen total y Open Interest
    - Put/Call Ratio
    - Expected Move usando Implied Volatility o straddle ATM de la expiración más cercana.
    """
    try:
        tkt = yf.Ticker(ticker)
        expirations = tkt.options
        if not expirations:
            return f"No hay datos de opciones disponibles para {ticker}."
            
        # Tomar la expiración más cercana (normalmente la primera, mayor liquidez a corto plazo)
        nearest_exp = expirations[0]
        chain = tkt.option_chain(nearest_exp)
        calls = chain.calls
        puts = chain.puts
        
        # 1. PCR Ratio y Volumen
        total_call_vol = calls['volume'].sum() if 'volume' in calls else 0
        total_put_vol = puts['volume'].sum() if 'volume' in puts else 0
        
        call_oi = calls['openInterest'].sum() if 'openInterest' in calls else 0
        put_oi = puts['openInterest'].sum() if 'openInterest' in puts else 0
        
        vol_pcr = total_put_vol / total_call_vol if total_call_vol > 0 else 0
        oi_pcr = put_oi / call_oi if call_oi > 0 else 0
        
        # 2. Skew (Asimetría) = IV de Puts OTM vs IV de Calls OTM
        # Para simplificar, comparamos el IV promedio global de puts vs calls (siempre que lo devuelva YF)
        avg_call_iv = calls['impliedVolatility'].mean() if 'impliedVolatility' in calls else 0
        avg_put_iv = puts['impliedVolatility'].mean() if 'impliedVolatility' in puts else 0
        skew_sentiment = "Sesgo Bajista (Puts más caros)" if avg_put_iv > avg_call_iv else "Sesgo Alcista (Calls más caros)"
        
        # 3. Movimiento Esperado (Straddle ATM)
        current_price = tkt.history(period="1d")['Close'].iloc[-1]
        
        # Encontrar Strike más cercano al precio actual ATM
        atm_strike_call = calls.iloc[(calls['strike'] - current_price).abs().argsort()[:1]]
        atm_strike_put = puts.iloc[(puts['strike'] - current_price).abs().argsort()[:1]]
        
        if not atm_strike_call.empty and not atm_strike_put.empty:
            atm_call_price = atm_strike_call['lastPrice'].values[0]
            atm_put_price = atm_strike_put['lastPrice'].values[0]
            expected_move_abs = atm_call_price + atm_put_price
            expected_move_pct = (expected_move_abs / current_price) * 100
        else:
            expected_move_abs = 0
            expected_move_pct = 0
            
        report = f"""MERCADO DE OPCIONES PARA {ticker}:
Expiración más cercana analizada: {nearest_exp}
Precio actual: ${current_price:.2f}

- Volumen Total de Opciones (Front Month): {total_call_vol} Calls / {total_put_vol} Puts
- Interés Abierto (OI): {call_oi} Calls / {put_oi} Puts
- Volumen Put/Call Ratio: {vol_pcr:.2f}
- OI Put/Call Ratio: {oi_pcr:.2f}

IV Skew (Asimetría de Volatilidad Implícita):
- IV Medio Puts: {avg_put_iv:.2%}
- IV Medio Calls: {avg_call_iv:.2%}
- Inclinación: {skew_sentiment}

Movimiento Esperado Cotizado (Expected Move hasta {nearest_exp}):
- Movimiento Absoluto: +/- ${expected_move_abs:.2f}
- Variación Porcentual: +/- {expected_move_pct:.2f}%
"""
        return report.strip()
    except Exception as e:
        return f"Error analizando cadena de opciones de {ticker}: {str(e)}"

def options_analyst_node(state: AnalystState):
    """
    Nodo de LangGraph para el Analista de Opciones.
    Extrae expectativas probabilísticas del mercado de derivados.
    """
    ticker = state["ticker"]
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    
    options_context = state.get("raw_options", "No hay datos de opciones disponibles.")
    current_date = get_current_date.invoke({})
    language = state.get("language", "en")
    
    lang_map = {
        "en": "English", "es": "Spanish (Español)", "pt": "Portuguese (Português)", "zh": "Chinese (Mandarin/Simplified)"
    }
    target_lang = lang_map.get(language, "English")
    
    system_prompt = f"""Eres un Analista Cuantitativo de Derivados Institucionales.
Fecha actual: {current_date}. 

REGLA DE IDIOMA: Debes escribir TODO tu reporte INTEGRAMENTE en {target_lang}.

Analiza los datos de opciones proveídos para {ticker}.

Debes proporcionar en tu reporte:
1. Posicionamiento: ¿Qué indica el Put/Call Ratio sobre el nerviosismo?
2. Skew: Interpretación de la asimetría de volatilidad (miedo a caídas vs optimismo).
3. Rango de Trading: Según el Expected Move, acota los rangos razonables de precio para el swing trade.

Evita repeticiones crudas, proporciona análisis concluyente derivado de los números bajo una perspectiva del market-maker institucional.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Datos de cadena de opciones:\n{options_context}")
    ]
    
    response = llm.invoke(messages)
    combined = f"=== DATOS CRUDOS VERIFICADOS ===\n{options_context}\n\n=== INTERPRETACIÓN DEL ANALISTA ===\n{response.content}"
    return {"options_analysis": combined}
