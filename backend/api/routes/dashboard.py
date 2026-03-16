from fastapi import APIRouter, HTTPException, Query
import sys
import os

from api.core.config import settings

# Agregar la ruta base al sys.path para poder importar los módulos del backend
if settings.BASE_DIR not in sys.path:
    sys.path.append(settings.BASE_DIR)

from Dashboard.asset_details import AssetDetailsAnalyzer
from Dashboard.macro_sentiment import get_economic_calendar, get_economic_events, get_cot_report
from Dashboard.market_scanner import get_market_screener

router = APIRouter()

@router.get("/asset/{ticker}", summary="Detalles completos de un Activo")
def get_asset_details(ticker: str):
    """
    Obtiene información general, estimaciones de consenso, analistas y 
    datos de transacciones y propiedad de Insiders e Instituciones.
    """
    try:
        analyzer = AssetDetailsAnalyzer(ticker)
        details = analyzer.get_full_details()
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/macro/calendar", summary="Calendario Económico (ForexFactory)")
def get_macro_calendar():
    """
    Retorna el calendario económico de la semana filtrado solo por eventos de Alto Impacto.
    """
    try:
        events = get_economic_calendar()
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/macro/events", summary="Eventos Macro FRED")
def get_macro_events(fred_api_key: str = Query(None, description="API Key de FRED (opcional, por defecto de .env)")):
    """
    Retorna series históricas estructuradas de FRED:
    Tasa de desempleo vs SP500, PIB, Inflación, y Confianza del Consumidor.
    """
    try:
        key_to_use = fred_api_key or settings.FRED_API_KEY
        if not key_to_use:
            raise HTTPException(status_code=500, detail="Missing FRED_API_KEY in environment or query param.")
            
        data = get_economic_events(key_to_use)
        if "error" in data:
            raise HTTPException(status_code=500, detail=data["error"])
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/macro/cot", summary="Reporte COT (CFTC)")
def get_macro_cot_report(market: str = Query("E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE")):
    """
    Obtiene el reporte formativo del Commitment of Traders (COT).
    Por defecto usa el S&P 500 E-Mini.
    """
    try:
        report = get_cot_report(market=market)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scanner", summary="Escáner Finviz (Activos y Volátiles)")
def get_scanner():
    """
    Escanea y retorna los instrumentos bursátiles más Activos (volumen) 
    y más Volátiles (Momentum) del mercado actual.
    """
    try:
        results = get_market_screener()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/macro/cot/contracts", summary="Lista de Contratos COT Disponibles")
def get_cot_contracts():
    """Retorna la lista completa de contratos disponibles para el COT report."""
    return {
        "currencies": [
            "USD INDEX - ICE FUTURES U.S.",
            "CANADIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE",
            "EURO FX - CHICAGO MERCANTILE EXCHANGE",
            "JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE",
            "BRITISH POUND - CHICAGO MERCANTILE EXCHANGE",
            "SWISS FRANC - CHICAGO MERCANTILE EXCHANGE",
            "AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE",
            "NZ DOLLAR - CHICAGO MERCANTILE EXCHANGE",
            "MEXICAN PESO - CHICAGO MERCANTILE EXCHANGE",
            "BRAZILIAN REAL - CHICAGO MERCANTILE EXCHANGE",
        ],
        "indices": [
            "E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE",
            "S&P 500 Consolidated - CHICAGO MERCANTILE EXCHANGE",
            "NASDAQ MINI - CHICAGO MERCANTILE EXCHANGE",
            "RUSSELL E-MINI - CHICAGO MERCANTILE EXCHANGE",
            "DJIA x $5 - CHICAGO BOARD OF TRADE",
        ],
        "crypto": [
            "BITCOIN - CHICAGO MERCANTILE EXCHANGE",
            "MICRO BITCOIN - CHICAGO MERCANTILE EXCHANGE",
            "ETHER CASH SETTLED - CHICAGO MERCANTILE EXCHANGE",
        ],
        "rates": [
            "VIX FUTURES - CBOE FUTURES EXCHANGE",
            "FED FUNDS - CHICAGO BOARD OF TRADE",
            "UST BOND - CHICAGO BOARD OF TRADE",
            "UST 10Y NOTE - CHICAGO BOARD OF TRADE",
            "UST 2Y NOTE - CHICAGO BOARD OF TRADE",
        ]
    }
