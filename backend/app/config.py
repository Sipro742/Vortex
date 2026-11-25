"""Configuración centralizada del backend de VÓRTICE."""

import os
from pathlib import Path

# Directorio base del backend (carpeta backend/)
DIRECTORIO_BACKEND = Path(__file__).resolve().parent.parent
RUTA_DB_POR_DEFECTO = DIRECTORIO_BACKEND / "vortice.db"

# Clave secreta para firmar tokens JWT.
# En producción DEBE definirse mediante la variable de entorno VORTICE_SECRET_KEY.
SECRET_KEY: str = os.getenv(
    "VORTICE_SECRET_KEY",
    "vortice-dev-clave-secreta-local-cambiar-en-produccion-9f8a7b6c5d4e",
)

ALGORITMO_JWT: str = os.getenv("VORTICE_JWT_ALGORITMO", "HS256")
EXPIRACION_TOKEN_MINUTOS: int = int(
    os.getenv("VORTICE_JWT_EXPIRACION_MINUTOS", "480")
)

# URL de conexión a la base de datos SQLite
URL_BASE_DATOS: str = os.getenv(
    "VORTICE_DATABASE_URL",
    f"sqlite:///{RUTA_DB_POR_DEFECTO.as_posix()}",
)

# Orígenes permitidos para CORS en desarrollo local (separados por coma en env)
_origenes_env = os.getenv("VORTICE_CORS_ORIGINS", "")
if _origenes_env.strip():
    ORIGENES_CORS: list[str] = [
        origen.strip() for origen in _origenes_env.split(",") if origen.strip()
    ]
else:
    ORIGENES_CORS = [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
