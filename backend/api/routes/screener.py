from fastapi import APIRouter, HTTPException, Body, BackgroundTasks
from typing import List, Optional
import sys
import os
import glob
import pandas as pd

from api.core.config import settings

# Agregar la ruta base al sys.path
if settings.BASE_DIR not in sys.path:
    sys.path.append(settings.BASE_DIR)

# Importamos el motor unificado de Filter_sp500
from Filter_sp500.engine import FundamentalsEngine

router = APIRouter()

def read_last_csv_report():
    """Encuentra el CSV más reciente en Filter_sp500/reports y lo retorna como JSON."""
    reports_dir = os.path.join(settings.BASE_DIR, 'Filter_sp500', 'reports')
    csv_files = glob.glob(os.path.join(reports_dir, 'fundamentals_scan_*.csv'))
    
    if not csv_files:
        return {"message": "Aún no se ha generado un reporte S&P 500. Ejecute el motor del screener."}
        
    latest_csv = max(csv_files, key=os.path.getmtime)
    df = pd.read_csv(latest_csv)
    
    # Mapeo de normalización para asegurar retrocompatibilidad con CSVs antiguos
    column_mapping = {
        "ticker": "Ticker",
        "price": "Price",
        "final_score": "Final_Score",
        "recommendation": "Recommendation",
        "sector": "Sector",
        "upside": "Upside_Pct",
        "risk_flags": "Risk_Flags",
        "piotroski": "Piotroski_Score",
        "altman_z": "Altman_Score",
        "beneish_m": "Beneish_Score"
    }
    df = df.rename(columns=column_mapping)
    
    return df.fillna("N/A").to_dict(orient="records")

@router.get("/sp500", summary="Obtener el último escaneo del S&P 500")
def get_sp500_screener_results():
    """
    Recupera el último reporte CSV generado por el motor de análisis 
    fundamental del S&P 500 y lo devuelve estructurado.
    """
    try:
        data = read_last_csv_report()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sp500/run", summary="Ejecutar escaneo completo del S&P 500 en segundo plano")
def trigger_sp500_scan(background_tasks: BackgroundTasks):
    """
    Inicia la ejecución del motor Engine para los 500 tickers en background.
    Tardará varios minutos, pero retornará un mensaje de que ha empezado al instante.
    """
    def run_scan():
        try:
            engine = FundamentalsEngine()
            # Se permite algo de paralelismo, pero el propio scraper controla el rate-limit
            engine.run_market_scan(max_workers=3)
        except Exception as e:
            print(f"Error background scan: {str(e)}")
            
    background_tasks.add_task(run_scan)
    return {"message": "El escaneo completo del S&P 500 ha comenzado en segundo plano. Esto tomará de 5 a 15 minutos."}

@router.post("/custom", summary="Ejecutar Screener en Custom Tickers")
def run_custom_screener(tickers: List[str] = Body(..., examples=[["AAPL", "MSFT", "TSLA"]])):
    """
    Ejecuta el motor de análisis sobre una lista de tickers provistos por el usuario.
    Si la lista es muy larga, puede tardar varios minutos.
    """
    if not tickers:
        raise HTTPException(status_code=400, detail="Debe proveer una lista válida de Tickers.")
    
    try:
        engine = FundamentalsEngine()
        # Se ejecuta usando todos los analizadores para la lista custom
        df_results = engine.run_market_scan(tickers=tickers, max_workers=5)
        
        if df_results.empty:
            return {"message": "No se encontraron resultados válidos o suficientes datos para los tickers solicitados."}
            
        return df_results.fillna("N/A").to_dict(orient="records")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error en el escáner: {str(e)}")
