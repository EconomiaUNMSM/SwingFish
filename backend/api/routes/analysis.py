from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os

from api.core.config import settings

if settings.BASE_DIR not in sys.path:
    sys.path.append(settings.BASE_DIR)

from multiagent_analysis.graph import build_multiagent_graph
from multiagent_analysis.pdf_generator import ReportGenerator, AuditReportGenerator

router = APIRouter()

class MultiagentResponse(BaseModel):
    ticker: str
    decision: dict
    report_pdf_url: str
    audit_pdf_url: str
    # Agregamos los reportes detallados para que el frontend pueda mostrarlos por separado
    technical_analysis: Optional[str] = None
    fundamental_analysis: Optional[str] = None
    macro_analysis: Optional[str] = None
    sentiment_analysis: Optional[str] = None
    options_analysis: Optional[str] = None
    risk_analysis: Optional[str] = None

@router.post("/multiagent/{ticker}", summary="Ejecutar Análisis Multiagente")
def run_multiagent(ticker: str, language: Optional[str] = "en"):
    """
    Activa todo el comité de Agentes IA (LangGraph) para analizar el ticker.
    Devuelve la decisión final del Manager y las URLs para descargar los PDF
    con el razonamiento formal y auditorías de los LLMs.
    """
    ticker = ticker.upper()
    try:
        # Prevenimos el print excesivo capturando o asumiendo un entorno backend asíncrono
        app = build_multiagent_graph()
        initial_state = {"ticker": ticker, "language": language}
        
        # Ejecutar grafo. Esto puede tardar varios segundos (10-30s)
        final_state = app.invoke(initial_state)
        
        manager_decision = final_state.get("manager_decision", "Sin decisión final")
        
        # Parseo crudo de string para JSON frontend (si es posible), sino se devuelve como string
        decision_payload = {"executive_summary": manager_decision}
        
        # Generar PDFs (en la carpeta mapeada a genéricos estáticos)
        generator = ReportGenerator(ticker)
        pdf_path = generator.generate_pdf(final_state, output_dir=settings.REPORTS_DIR)
        
        audit_gen = AuditReportGenerator(ticker)
        audit_path = audit_gen.generate_audit_pdf(final_state, output_dir=settings.REPORTS_DIR)
        
        # Obtener sólo los nombres de archivos para la URL relativa
        report_file = os.path.basename(pdf_path)
        audit_file = os.path.basename(audit_path)
        
        return MultiagentResponse(
            ticker=ticker,
            decision=decision_payload,
            report_pdf_url=f"/reports/{report_file}",
            audit_pdf_url=f"/reports/{audit_file}",
            technical_analysis=final_state.get("technical_analysis"),
            fundamental_analysis=final_state.get("fundamental_analysis"),
            macro_analysis=final_state.get("macro_analysis"),
            sentiment_analysis=final_state.get("sentiment_analysis"),
            options_analysis=final_state.get("options_analysis"),
            risk_analysis=final_state.get("risk_analysis")
        )

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
