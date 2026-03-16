from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "SwingFish API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = ["*"] # Permitir todo por defecto para desarrollo local
    
    # Rutas base
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    PROJECT_ROOT: str = os.path.dirname(BASE_DIR)
    
    REPORTS_DIR: str = os.path.join(BASE_DIR, "multiagent_analysis", "reports")
    SCREENER_DATA_DIR: str = os.path.join(BASE_DIR, "Filter_sp500", "financial_data")

    # API Keys (cargadas desde .env)
    FRED_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    class Config:
        # Apuntar al .env en la raíz del proyecto (SwingFish/.env)
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), ".env")
        extra = "ignore"

settings = Settings()
