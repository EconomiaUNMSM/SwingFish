import sys
import os
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

# Configuración de variables de entorno (Asegura cargar OPENAI_API_KEY)
# Asegurar que multiagent_analysis esté en sys.path para ejecución directa
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, ".env")
load_dotenv(dotenv_path)

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from state import AnalystState
from data_fetcher import data_fetcher_node
from agents.technical_agent import technical_analyst_node
from agents.sentiment_agent import sentiment_analyst_node
from agents.macro_agent import macro_analyst_node
from agents.options_agent import options_analyst_node
from agents.risk_agent import risk_analyst_node
from agents.fundamental_agent import fundamental_analyst_node
from agents.manager_agent import manager_node

def build_multiagent_graph():
    """
    Construye el grafo de ejecución:
    1. DataFetcher: Pre-carga TODOS los datos financieros secuencialmente (yfinance NO es thread-safe).
    2. 6 Analistas LLM: Se ejecutan en paralelo (solo hacen llamadas OpenAI, que SÍ son thread-safe).
    3. Portfolio Manager: Sintetiza todos los reportes y emite el veredicto.
    """
    workflow = StateGraph(AnalystState)
    
    # 1. Nodo de pre-carga secuencial de datos
    workflow.add_node("DataFetcher", data_fetcher_node)
    
    # 2. Nodos analistas (solo LLM, sin yfinance)
    workflow.add_node("Technical", technical_analyst_node)
    workflow.add_node("Sentiment", sentiment_analyst_node)
    workflow.add_node("Macro", macro_analyst_node)
    workflow.add_node("Options", options_analyst_node)
    workflow.add_node("Risk", risk_analyst_node)
    workflow.add_node("Fundamental", fundamental_analyst_node)
    
    # 3. Portfolio Manager
    workflow.add_node("Portfolio_Manager", manager_node)
    
    # === FLUJO ===
    # Entry -> DataFetcher (secuencial: pre-carga todos los datos)
    workflow.set_entry_point("DataFetcher")
    
    # DataFetcher -> Fan-out paralelo a los 6 analistas LLM
    workflow.add_edge("DataFetcher", "Technical")
    workflow.add_edge("DataFetcher", "Sentiment")
    workflow.add_edge("DataFetcher", "Macro")
    workflow.add_edge("DataFetcher", "Options")
    workflow.add_edge("DataFetcher", "Risk")
    workflow.add_edge("DataFetcher", "Fundamental")
    
    # Todos convergen en el Manager
    workflow.add_edge("Technical", "Portfolio_Manager")
    workflow.add_edge("Sentiment", "Portfolio_Manager")
    workflow.add_edge("Macro", "Portfolio_Manager")
    workflow.add_edge("Options", "Portfolio_Manager")
    workflow.add_edge("Risk", "Portfolio_Manager")
    workflow.add_edge("Fundamental", "Portfolio_Manager")
    
    # El grafo termina tras la decisión del manager
    workflow.add_edge("Portfolio_Manager", END)
    
    app = workflow.compile()
    return app

if __name__ == "__main__":
    app = build_multiagent_graph()
    print("Multiagent Graph compilado correctamente.")
