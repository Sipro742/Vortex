"""Punto de entrada de la aplicación FastAPI para VÓRTICE."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ORIGENES_CORS
from app.database import Base, engine
from app.routers import admin, auth, calculo


@asynccontextmanager
async def ciclo_vida(_app: FastAPI) -> AsyncIterator[None]:
    """Crea las tablas SQLite automáticamente al arrancar el servidor."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="VÓRTICE - Calculadora de Estructuras API",
    description=(
        "Backend seguro para el cálculo estructural de techos y gestión de "
        "acceso con revocación instantánea."
    ),
    version="1.0.0",
    lifespan=ciclo_vida,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES_CORS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(calculo.router)
app.include_router(admin.router)


@app.get("/api/salud", tags=["Sistema"])
def verificar_salud() -> dict[str, str]:
    """Endpoint ligero para comprobar que el servidor está en línea."""
    return {"estado": "ok", "servicio": "VÓRTICE API"}
