"""Aplicación FastAPI de GastaIA - Configuración principal."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.endpoints import router
from app.db import db


def create_app() -> FastAPI:
    """Crear y configurar la aplicación FastAPI."""
    app = FastAPI(
        title="GastaIA API",
        description="API REST para gestionar gastos personales con IA",
        version="0.1.0",
    )

    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Inicializar base de datos
    db.init_db()

    # Incluir routers
    app.include_router(router, prefix="/api/v1", tags=["expenses"])

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
