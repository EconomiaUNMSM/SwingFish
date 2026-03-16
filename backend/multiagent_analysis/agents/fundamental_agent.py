import sys
import os
import yfinance as yf
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

current_dir = os.path.dirname(os.path.abspath(__file__))              # agents/
multiagent_dir = os.path.dirname(current_dir)                         # multiagent_analysis/
backend_dir = os.path.dirname(multiagent_dir)                         # backend/

for p in [multiagent_dir, backend_dir]:
    if p not in sys.path:
        sys.path.append(p)

from Dashboard.asset_details import AssetDetailsAnalyzer
from state import AnalystState
from tools import get_current_date

@tool
def get_fundamental_and_insiders(ticker: str) -> str:
    """
    Usa el analizador de detalles del activo (AssetDetailsAnalyzer) y yfinance directo para extraer:
    - Ratios financieros (PE, PB, PS, EV/EBITDA).
    - Estimaciones de precio de analistas (Target Alto/Medio/Bajo).
    - Recomendaciones de analistas institucionales.
    - Acciones de compras/ventas recientes de ejecutivos (Insiders).
    - Propiedad institucional.
    """
    try:
        analyzer = AssetDetailsAnalyzer(ticker)
        details = analyzer.get_full_details()
        
        info = details.get("general_info", {})
        insider_data = details.get("insider_data", {})
        
        if "error" in info:
            return f"Error extrayendo datos fundamentales: {info['error']}"
        
        # Extraer ratios directamente de yfinance.info
        yf_ticker = yf.Ticker(ticker)
        yf_info = yf_ticker.info
        
        # Precio actual y targets
        precio_actual = info.get('precio_actual', yf_info.get('currentPrice', 'N/A'))
        target_alto = info.get('estimacion_alta', yf_info.get('targetHighPrice', 'N/A'))
        target_medio = info.get('estimacion_media', yf_info.get('targetMeanPrice', 'N/A'))
        target_bajo = info.get('estimacion_baja', yf_info.get('targetLowPrice', 'N/A'))
        recomendacion = info.get('recomendacion', yf_info.get('recommendationKey', 'N/A'))
        num_analistas = yf_info.get('numberOfAnalystOpinions', 'N/A')
        
        # Calcular upside potencial
        upside = ""
        if isinstance(precio_actual, (int, float)) and isinstance(target_medio, (int, float)) and precio_actual > 0:
            upside_pct = ((target_medio - precio_actual) / precio_actual) * 100
            upside = f" (Upside potencial: {upside_pct:+.1f}%)"
            
        report = f"""PERFIL FUNDAMENTAL Y CORPORATIVO DE {ticker}:

1. MÉTRICAS CLAVE Y VALORACIÓN:
- Nombre: {info.get('nombre', 'N/A')}
- Precio Actual: ${precio_actual}
- Beta: {info.get('beta', 'N/A')}
- Volumen Promedio: {info.get('volumen_promedio', 'N/A')}

Ratios de Valoración:
- P/E Trailing: {yf_info.get('trailingPE', 'N/A')}
- P/E Forward: {yf_info.get('forwardPE', 'N/A')}
- Price to Book: {yf_info.get('priceToBook', 'N/A')}
- Price to Sales (TTM): {yf_info.get('priceToSalesTrailing12Months', 'N/A')}
- EV/EBITDA: {yf_info.get('enterpriseToEbitda', 'N/A')}
- Profit Margin: {yf_info.get('profitMargins', 'N/A')}
- Revenue Growth: {yf_info.get('revenueGrowth', 'N/A')}

ESTIMACIONES DE ANALISTAS DE WALL STREET:
- Número de Analistas con opinión: {num_analistas}
- Target Precio ALTO: ${target_alto}
- Target Precio MEDIO (Consenso): ${target_medio}{upside}
- Target Precio BAJO: ${target_bajo}
- Recomendación Consenso: {recomendacion}
- Propiedad de Insiders: {info.get('insiders_prop', 'N/A')}%
- Propiedad Institucional: {info.get('inst_prop', 'N/A')}%

2. ACTIVIDAD DE INSIDERS (Últimas transacciones clave):
"""
        insider_txns = insider_data.get("insider_transactions", [])
        if insider_txns:
            for tx in insider_txns[:7]:
                nombre = tx.get('filerName', 'N/A')
                transaccion = tx.get('transactionText', 'N/A')
                acciones = tx.get('shares', 'N/A')
                valor = tx.get('value', 'N/A')
                fecha = tx.get('startDate', 'N/A')
                if isinstance(fecha, dict):
                    fecha = fecha.get('fmt', str(fecha))
                report += f"- [{fecha}] {nombre}: {transaccion} | {acciones} acciones | Valor: ${valor}\n"
        else:
            report += "- No hay datos recientes de transacciones insiders.\n"

        report += "\n3. PROPIEDAD INSTITUCIONAL (Top Holders):\n"
        inst_ownership = insider_data.get("institutional_ownership", [])
        if inst_ownership:
            for holder in inst_ownership[:5]:
                org = holder.get('organization', 'N/A')  
                pct = holder.get('pctHeld', 'N/A')
                shares = holder.get('position', 'N/A')
                if isinstance(pct, float):
                    pct = f"{pct:.2%}"
                report += f"- {org}: {shares} acciones ({pct})\n"
        else:
            report += "- No hay datos de propiedad institucional.\n"
            
        return report.strip()
        
    except Exception as e:
        import traceback
        return f"Excepción crítica al extraer data fundamental para {ticker}: {str(e)}\n{traceback.format_exc()}"

def fundamental_analyst_node(state: AnalystState):
    ticker = state["ticker"]
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    
    fundamental_context = state.get("raw_fundamental", "No hay datos fundamentales disponibles.")
    current_date = get_current_date.invoke({})
    language = state.get("language", "en")
    
    lang_map = {
        "en": "English", "es": "Spanish (Español)", "pt": "Portuguese (Português)", "zh": "Chinese (Mandarin/Simplified)"
    }
    target_lang = lang_map.get(language, "English")
    
    system_prompt = f"""Eres un Analista Fundamental de Equities Senior.
Fecha actual: {current_date}. 

REGLA DE IDIOMA: Debes escribir TODO tu reporte INTEGRAMENTE en {target_lang}.

Examina la infraestructura corporativa de {ticker} en base a la información extraída.

Tu reporte DEBE indicar claramente:
1. Valuación: ¿El activo está infravalorado, en precio justo o es una burbuja especulativa según sus ratios (PE, PB, EV/EBITDA)?
2. Estimaciones de Wall Street: Compara el precio actual contra los targets de precio de los analistas (Alto, Medio, Bajo). Calcula y menciona explícitamente el potencial de upside o downside respecto al consenso.
3. Confianza corporativa: ¿Las transacciones de Insiders denotan pánico, toma de ganancias o acumulación?
4. Capilaridad Institucional: ¿Tiene respaldo del dinero inteligente (Smart Money)?

IMPORTANTE: Siempre menciona los targets de precio de los analistas y el upside/downside potencial.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Reporte Crudo de Fundamentales e Insiders:\n{fundamental_context}")
    ]
    
    response = llm.invoke(messages)
    combined = f"=== DATOS CRUDOS VERIFICADOS ===\n{fundamental_context}\n\n=== INTERPRETACIÓN DEL ANALISTA ===\n{response.content}"
    return {"fundamental_analysis": combined}
