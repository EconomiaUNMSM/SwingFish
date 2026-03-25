import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from graph import build_multiagent_graph
from pdf_generator import ReportGenerator, AuditReportGenerator

# Directorio donde se guardan los reportes PDF
REPORTS_DIR = os.path.join(current_dir, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def run_multiagent_analysis(ticker: str, language: str = "es"):
    print(f"\n[+] Iniciando Escuadrón de Análisis para: {ticker} (Idioma: {language})")
    print("[+] Compilando Grafo de LangGraph...")
    
    app = build_multiagent_graph()
    initial_state = {"ticker": ticker, "language": language}
    
    print("[+] Fase 1: DataFetcher extrayendo datos financieros (secuencial)...")
    print("[+] Fase 2: Analistas LLM interpretando datos (paralelo)...")
    print("[+] Fase 3: Portfolio Manager sintetizando veredicto...")
    
    try:
        final_state = app.invoke(initial_state)
    except Exception as e:
        print(f"[-] Hubo un error crítico en el orquestador: {e}")
        import traceback
        traceback.print_exc()
        return
        
    print("\n[+] Análisis completado exitosamente.")
    print("--------------------------------------------------")
    print(final_state.get("manager_decision", "Sin decisión final."))
    print("--------------------------------------------------\n")
    
    # === Generar PDF de Reporte Principal ===
    print("[+] Generando Reporte Principal PDF...")
    try:
        generator = ReportGenerator(ticker)
        pdf_path = generator.generate_pdf(final_state, output_dir=REPORTS_DIR)
        print(f"[SUCCESS] Reporte Principal: {pdf_path}")
    except Exception as e:
        print(f"[-] Error al generar el PDF principal: {e}")
        import traceback
        traceback.print_exc()
    
    # === Generar PDF de Audit Trail ===
    print("[+] Generando Audit Trail PDF (Datos Crudos vs LLM)...")
    try:
        audit_gen = AuditReportGenerator(ticker)
        audit_path = audit_gen.generate_audit_pdf(final_state, output_dir=REPORTS_DIR)
        print(f"[SUCCESS] Audit Trail: {audit_path}")
    except Exception as e:
        print(f"[-] Error al generar el Audit Trail PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Multiagent Analysis para Swing Trading.")
    parser.add_argument("ticker", type=str, help="El Ticker o Símbolo a analizar (Ej. AAPL, NVDA).")
    parser.add_argument("--lang", type=str, default="es", choices=["en", "es", "pt", "zh"], help="Idioma del reporte.")
    args = parser.parse_args()
    
    run_multiagent_analysis(args.ticker, args.lang)
