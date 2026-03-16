import json
from macro_sentiment import (
    get_economic_calendar,
    get_economic_events,
    get_cot_report
)
from market_scanner import get_market_screener
from asset_details import AssetDetailsAnalyzer

def print_json(title: str, data: any):
    print(f"\n{'='*50}")
    print(f"--- {title} ---")
    print(f"{'='*50}")
    # Convertimos a JSON formateado para verificar correcta serialización
    print(json.dumps(data, indent=2, ensure_ascii=False))

def test_macro_sentiment():
    print("Iniciando pruebas de Macro Sentiment...\n")
    
    # 1. Calendario Económico (Alto Impacto)
    print("Extrayendo Calendario Económico (Alto Impacto)...")
    calendar = get_economic_calendar()
    print_json("Calendario Económico", calendar)
    
    # 2. Eventos Económicos de FRED (Requiere API Key válida)
    print("\nExtrayendo Eventos Económicos (FRED)...")
    # Usa tu API key real o una de prueba para que corra
    fred_api_key = "7c8df3029e7de155fe90daa6c5aeabb2" 
    events = get_economic_events(fred_api_key)
    print_json("Eventos Económicos FRED / SP500", events)
    
    # 3. Reporte COT
    print("\nExtrayendo Reporte COT (CAD)...")
    cot_data = get_cot_report("CANADIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE")
    print_json("COT Report (Últimos 20)", cot_data)
    



def test_market_scanner():
    print("Iniciando pruebas de Market Scanner...\n")
    print("Extrayendo Escáner de Mercado (Most Active / Most Volatile)...")
    
    screener_data = get_market_screener()
    
    # Solo imprimimos los 3 primeros de cada uno para no inundar la terminal
    active_sample = screener_data.get("most_active", [])[:3]
    volatile_sample = screener_data.get("most_volatile", [])[:3]
    
    print_json("Most Active (Muestra de 3)", active_sample)
    print_json("Most Volatile (Muestra de 3)", volatile_sample)


def test_asset_details(ticker: str = "DECK"):
    print(f"Iniciando pruebas de Detalles de Activo para {ticker}...\n")
    
    analyzer = AssetDetailsAnalyzer(ticker)
    
    print(f"Extrayendo Detalles Completos ({ticker})...")
    full_details = analyzer.get_full_details()
    
    # Mostramos resumen general
    print_json(f"Detalle Completo - {ticker} (General Info)", full_details.get("general_info"))
    
    # Resumen de insider transaction y propiedad, sample para terminal
    insider_data = full_details.get("insider_data", {})
    if insider_data.get("has_insider_transactions"):
        insider_data["insider_transactions"] = insider_data["insider_transactions"][:2] # truncamos a 2
    if insider_data.get("has_institutional_ownership"):
        insider_data["institutional_ownership"] = insider_data["institutional_ownership"][:2] # truncamos a 2
        
    print_json(f"Detalle Completo - {ticker} (Muestra Insiders & Propiedad)", insider_data)


if __name__ == "__main__":
    print(r"""
      ____            _     _                         _ 
     |  _ \  __ _ ___| |__ | |__   ___   __ _ _ __ __| |
     | | | |/ _` / __| '_ \| '_ \ / _ \ / _` | '__/ _` |
     | |_| | (_| \__ \ | | | | | | (_) | (_| | | | (_| |
     |____/ \__,_|___/_| |_|_| |_|\___/ \__,_|_|  \__,_|
                                                        
     Test de Componentes - Módulo Backend               
    """)
    
    # Descomenta los siguientes si deseas probar todos al mismo tiempo, 
    # por ahora los llamamos uno por uno.
    
    try:
        test_macro_sentiment()
        # test_market_scanner()
        # test_asset_details("AAPL")
    except Exception as e:
        print(f"Error en el test: {str(e)}")
