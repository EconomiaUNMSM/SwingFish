"""
Script de prueba interactivo para el Módulo de Fundamentales.
Permite ejecutar un scan rápido sobre una lista personalizada o el S&P 500.
"""

import sys
import logging
import argparse
from pathlib import Path

# Agregar raíz al path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.MODULO_FUNDAMENTALES.engine import FundamentalsEngine

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    print("="*60)
    print("   MOTOR DE ANÁLISIS FUNDAMENTAL - TEST FLOW")
    print("="*60)
    
    engine = FundamentalsEngine()
    
    print("\nOpciones:")
    print("1. Analizar lista personalizada de tickers")
    print("2. Analizar todo el S&P 500 (Toma tiempo)")
    print("3. Analizar Top 10 S&P 500 (Rápido)")
    
    choice = input("\nSeleccione una opción [1]: ").strip() or "1"
    
    tickers = []
    
    if choice == "1":
        input_str = input("Ingrese tickers separados por coma (ej: AAPL, TSLA, DECK): ").strip()
        if input_str:
            tickers = [t.strip().upper() for t in input_str.split(",")]
        else:
            print("Lista vacía. Usando default: AAPL, MSFT, GOOGL")
            tickers = ["AAPL", "MSFT", "GOOGL"]
            
    elif choice == "2":
        print("Obteniendo S&P 500 completo...")
        # engine.run_market_scan maneja la obtención si tickers=None
        tickers = None 
        
    elif choice == "3":
        # Simulación rápida
        tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "LLY", "V"]
        
    print(f"\nIniciando análisis para {len(tickers) if tickers else 'S&P 500'}...")
    
    # Ejecutar scan
    df_results = engine.run_market_scan(tickers=tickers)
    
    if not df_results.empty:
        print("\n" + "="*60)
        print("   TOP 10 RESULTADOS")
        print("="*60)
        
        # Columnas clave para mostrar
        cols = ["ticker", "final_score", "recommendation", "growth_score", "upside", "risk_flags"]
        print(df_results[cols].head(10).to_string(index=False))
        
        print("\n" + "="*60)
        print(f"Total procesados: {len(df_results)}")
        print("Reporte completo guardado en carpeta 'reports'.")
    else:
        print("\nNo se obtuvieron resultados válidos.")

if __name__ == "__main__":
    main()
