import yfinance as yf
import pandas as pd
import numpy as np
from langchain_core.tools import tool

@tool
def get_technical_indicators(ticker: str) -> str:
    """
    Obtiene métricas técnicas clave para un activo dado:
    Nubes de Ichimoku, Índice Ulcer, SMAs (20, 50, 200), RSI, y RVI (Índice de Volatilidad Relativa).
    """
    try:
        data = yf.download(ticker, period="2y", progress=False, multi_level_index=False)
        if data.empty:
            return f"No se encontraron datos para el ticker {ticker}."

        close = data['Close']
        high = data['High']
        low = data['Low']
        
        # ===================== 1. SMAs =====================
        sma_20 = close.rolling(window=20).mean()
        sma_50 = close.rolling(window=50).mean()
        sma_200 = close.rolling(window=200).mean()
        
        last_close = float(close.iloc[-1])
        last_sma20 = float(sma_20.iloc[-1])
        last_sma50 = float(sma_50.iloc[-1])
        last_sma200 = float(sma_200.iloc[-1])
        
        # Rachas sobre SMA 50
        above_sma50 = close > sma_50
        above_sma50 = above_sma50.dropna()
        current_streak = 0
        is_above = bool(above_sma50.iloc[-1])
        for val in reversed(above_sma50.tolist()[-200:]):
            if bool(val) == is_above:
                current_streak += 1
            else:
                break
        racha_str = f"{current_streak} días " + ("por encima" if is_above else "por debajo") + " de la SMA 50"
        
        # ===================== 2. RSI (14) =====================
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(com=13, adjust=False).mean()
        avg_loss = loss.ewm(com=13, adjust=False).mean()
        rs = avg_gain / avg_loss
        rsi_series = 100 - (100 / (1 + rs))
        rsi = float(rsi_series.iloc[-1])
        
        # ===================== 3. Ichimoku (9, 26, 52) =====================
        tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2
        kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2
        span_a_raw = (tenkan + kijun) / 2
        span_b_raw = (high.rolling(52).max() + low.rolling(52).min()) / 2
        
        span_a = float(span_a_raw.iloc[-1])
        span_b = float(span_b_raw.iloc[-1])
        
        if last_close > max(span_a, span_b):
            cloud_status = "Por encima de la nube (Alcista)"
        elif last_close < min(span_a, span_b):
            cloud_status = "Por debajo de la nube (Bajista)"
        else:
            cloud_status = "Dentro de la nube (Consolidación / Transición)"
        
        # ===================== 4. Ulcer Index (14) =====================
        rolling_max_ui = close.rolling(14).max()
        pct_dd = ((close - rolling_max_ui) / rolling_max_ui) * 100
        ulcer_sq = (pct_dd ** 2).rolling(14).mean()
        ulcer_index = float(np.sqrt(ulcer_sq.iloc[-1]))
        
        # ===================== 5. RVI (Relative Volatility Index) =====================
        std_10 = close.rolling(10).std()
        price_diff = close.diff()
        up_std = std_10.where(price_diff > 0, 0.0)
        down_std = std_10.where(price_diff < 0, 0.0)
        up_ema = up_std.ewm(span=14, adjust=False).mean()
        down_ema = down_std.ewm(span=14, adjust=False).mean()
        denom = up_ema + down_ema
        rvi_series = 100 * up_ema / denom
        rvi = float(rvi_series.iloc[-1])

        # ===================== 6. ATR (Average True Range) =====================
        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr_series = tr.rolling(window=14).mean()
        atr = float(atr_series.iloc[-1])

        report = f"""ANÁLISIS TÉCNICO ACTUAL PARA {ticker}:
Precio de Cierre Actual: ${last_close:.2f}

1. MEDIAS MÓVILES E INERCIA:
- SMA 20: ${last_sma20:.2f}
- SMA 50: ${last_sma50:.2f}
- SMA 200: ${last_sma200:.2f}
- Persistencia de Tendencia: El precio lleva {racha_str}.

2. OSCILADORES DE MOMENTUM Y VOLATILIDAD DE PRECIO:
- RSI (14): {rsi:.2f} (>70 Sobrecomprado, <30 Sobrevendido)
- Índice de Volatilidad Relativa (RVI 14): {rvi:.2f} (>50 volatilidad alcista, <50 volatilidad bajista)
- Average True Range (ATR 14): ${atr:.2f} (Tamaño promedio de la vela/movimiento en los últimos 14 días)

3. SOPORTES Y RESISTENCIAS CLAVE (Ichimoku Cloud):
- Senkou Span A (Soporte/Resistencia 1): ${span_a:.2f}
- Senkou Span B (Soporte/Resistencia 2): ${span_b:.2f}
- Relación actual: {cloud_status}.

4. RIESGO DOWNSIDE:
- Índice Ulcer (UI): {ulcer_index:.4f} (Mide profundidad y duración de drawdowns recientes; valores altos = alto estrés)."""
        
        return report
        
    except Exception as e:
        import traceback
        return f"Error calculando indicadores técnicos para {ticker}: {str(e)}\n{traceback.format_exc()}"

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

def technical_analyst_node(state: AnalystState):
    ticker = state["ticker"]
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    
    # Lee datos PRE-CARGADOS del state (extraídos secuencialmente por DataFetcher)
    prompt_context = state.get("raw_technical", "No hay datos técnicos disponibles.")
    current_date = get_current_date.invoke({})
    language = state.get("language", "en")
    
    # Mapeo de nombres descriptivos de lenguajes
    lang_map = {
        "en": "English",
        "es": "Spanish (Español)",
        "pt": "Portuguese (Português)",
        "zh": "Chinese (Mandarin/Simplified)"
    }
    target_lang = lang_map.get(language, "English")
    
    system_prompt = f"""Eres un Analista Técnico Cuantitativo Experto.
Tu tarea es interpretar los siguientes indicadores técnicos crudos de nivel institucional para el activo {ticker}.
Fecha actual del análisis: {current_date}.

REGLA DE IDIOMA: Debes escribir TODO tu reporte INTEGRAMENTE en {target_lang}.

REGLA CRÍTICA: Usa EXACTAMENTE los mismos valores numéricos que aparecen en los datos provistos.
NO inventes, redondees ni alteres ningún número. Cita los valores tal cual aparecen.

Debes proveer un Reporte Ejecutivo Técnico estructurado incluyendo:
- Evaluación del régimen de tendencia actual.
- Fuerza relativa (RSI/RVI) y volatilidad implícita del precio (evalúa el tamaño del ATR para proyecciones de velas futuras).
- Riesgo de downside (Ulcer Index).
- Zonas de soporte y resistencia críticas según Ichimoku.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Contexto técnico crudo:\n{prompt_context}")
    ]
    
    response = llm.invoke(messages)
    
    # Inyectar datos crudos REALES + interpretación del LLM
    combined = f"=== DATOS CRUDOS VERIFICADOS ===\n{prompt_context}\n\n=== INTERPRETACIÓN DEL ANALISTA ===\n{response.content}"
    return {"technical_analysis": combined}
