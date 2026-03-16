from datetime import datetime
from langchain_core.tools import tool

@tool
def get_current_date() -> str:
    """
    Devuelve la fecha actual en formato YYYY-MM-DD.
    Debe ser usada siempre que se requiera conocer la actualidad para poner el análisis en contexto.
    """
    return datetime.now().strftime("%Y-%m-%d")

# Aquí agregaremos herramientas comunes que varios agentes pudieran necesitar
