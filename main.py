"""Punto de entrada para ejecutar GastaIA API."""

import uvicorn
from app.api import app


def main():
    """Ejecutar servidor FastAPI."""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()


