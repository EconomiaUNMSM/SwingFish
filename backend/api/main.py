from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from api.core.config import settings
from api.routes import dashboard, screener, analysis

def get_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Set up CORS middleware
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
    # Montar archivos estáticos para poder descargar los PDFs de multiagente
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    app.mount("/reports", StaticFiles(directory=settings.REPORTS_DIR), name="reports")

    # Incluir routers
    app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"])
    app.include_router(screener.router, prefix=f"{settings.API_V1_STR}/screener", tags=["Screener"])
    app.include_router(analysis.router, prefix=f"{settings.API_V1_STR}/analysis", tags=["Multiagent Analysis"])

    @app.get("/")
    def root():
        return {
            "message": "Bienvenido a SwingFish API", 
            "docs_url": "/docs",
            "version": settings.VERSION
        }

    return app

app = get_application()
