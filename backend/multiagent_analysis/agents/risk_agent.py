import sys
import os
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

current_dir = os.path.dirname(os.path.abspath(__file__))              # agents/
multiagent_dir = os.path.dirname(current_dir)                         # multiagent_analysis/
if multiagent_dir not in sys.path:
    sys.path.append(multiagent_dir)

from state import AnalystState
from tools import get_current_date

@tool
def get_risk_metrics(ticker: str) -> str:
    """
    Calcula el perfil de riesgo complejo de un activo: 
    - VaR y CVaR (Monte Carlo a 1 año, 95% de confianza).
    - Drawdowns históricos en periodos de estrés conocidos.
    - Estacionalidad (retorno promedio mensual).
    """
    try:
        close = yf.download(ticker, period="max", progress=False, multi_level_index=False)['Close']
        if close.empty:
            return f"No hay datos históricos suficientes para evaluar riesgo de {ticker}."
            
        returns = close.pct_change().dropna()
        
        # ===================== 1. Monte Carlo VaR / CVaR =====================
        mu = float(returns.mean())
        sigma = float(returns.std())
        simulations = 10000
        days = 252
        
        # Simulamos retornos logarítmicos acumulados y convertimos a retorno simple
        log_returns = np.random.normal(
            (mu - 0.5 * sigma**2) * days, 
            sigma * np.sqrt(days), 
            simulations
        )
        simple_returns = np.exp(log_returns) - 1
        
        var_95 = float(np.percentile(simple_returns, 5))
        cvar_95 = float(simple_returns[simple_returns <= var_95].mean())
        
        # ===================== 2. Drawdowns en Periodos de Estrés =====================
        def calc_drawdown(start_date, end_date):
            mask = (close.index >= start_date) & (close.index <= end_date)
            sub = close[mask]
            if len(sub) < 2: 
                return 0.0
            roll_max = sub.cummax()
            dd = (sub - roll_max) / roll_max
            return float(dd.min())
            
        dd_covid = calc_drawdown("2020-01-01", "2020-04-30")
        dd_2022 = calc_drawdown("2022-01-01", "2022-12-31")
        
        # Drawdown Histórico Máximo
        roll_max_all = close.cummax()
        max_dd = float(((close - roll_max_all) / roll_max_all).min())
        
        # ===================== 3. Estacionalidad =====================
        current_month = datetime.now().month
        month_name = datetime.now().strftime('%B')
        
        monthly_prices = close.resample('ME').last()
        monthly_returns = monthly_prices.pct_change().dropna()
        same_month = monthly_returns[monthly_returns.index.month == current_month]
        
        if len(same_month) > 0:
            win_rate_month = float((same_month > 0).mean() * 100)
            avg_return_month = float(same_month.mean() * 100)
        else:
            win_rate_month = 0.0
            avg_return_month = 0.0

        report = f"""PERFIL DE RIESGO AVANZADO PARA {ticker}:

1. Análisis Cuantitativo Prospectivo (Monte Carlo - 1 Año, N=10000):
- Value at Risk (VaR 95%): {var_95:.2%} (Pérdida máxima esperada con 95% certidumbre en 1 año).
- Conditional VaR (CVaR 95%): {cvar_95:.2%} (Pérdida esperada promedio en el 5% de los peores escenarios).

2. Comportamiento en Crisis (Max Drawdowns):
- Caída Máxima Histórica (Max DD): {max_dd:.2%}
- Crash COVID-19 (Ene-Abr 2020): {dd_covid:.2%}
- Bear Market Inflación (2022): {dd_2022:.2%}

3. Estacionalidad del Mes Actual ({month_name}):
- Retorno histórico promedio de {month_name}: {avg_return_month:.2f}%
- Tasa de acierto (Win Rate) del mes: {win_rate_month:.1f}% de los años cerró en verde."""
        return report
    except Exception as e:
        import traceback
        return f"Error calculando métricas de riesgo para {ticker}: {str(e)}\n{traceback.format_exc()}"

def risk_analyst_node(state: AnalystState):
    ticker = state["ticker"]
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    
    risk_context = state.get("raw_risk", "No hay datos de riesgo disponibles.")
    current_date = get_current_date.invoke({})
    language = state.get("language", "en")
    
    lang_map = {
        "en": "English", "es": "Spanish (Español)", "pt": "Portuguese (Português)", "zh": "Chinese (Mandarin/Simplified)"
    }
    target_lang = lang_map.get(language, "English")
    
    system_prompt = f"""Eres el Chief Risk Officer (CRO) Cuantitativo del fondo de Swing Trading.
Fecha actual: {current_date}. 

REGLA DE IDIOMA: Debes escribir TODO tu reporte INTEGRAMENTE en {target_lang}.

Evalúa el perfil de riesgo inherente de {ticker} usando los datos del simulador Monte Carlo y Drawdowns.

REGLA CRÍTICA: Usa EXACTAMENTE los mismos valores numéricos que aparecen en los datos provistos.
NO inventes, redondees ni alteres ningún número. Cita los valores tal cual aparecen.

En tu reporte debes dictaminar:
1. Nivel de estrés latente: ¿Sobrevivirá el portafolio a una caída similar al CVaR proyectado?
2. Contexto de Crisis: ¿Es este activo altamente sensible a shocks sistémicos o es refugio?
3. Estacionalidad: ¿Es prudente o peligroso operar en el mes actual basándonos en la tasa de acierto histórica?

Usa un tono cauteloso y analítico.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Reporte Cuantitativo de Riesgo:\n{risk_context}")
    ]
    
    response = llm.invoke(messages)
    
    # Inyectar datos crudos REALES + interpretación del LLM
    combined = f"=== DATOS CRUDOS VERIFICADOS ===\n{risk_context}\n\n=== INTERPRETACIÓN DEL ANALISTA ===\n{response.content}"
    return {"risk_analysis": combined}
