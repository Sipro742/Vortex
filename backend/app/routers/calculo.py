"""Ruta protegida para ejecutar el cálculo estructural de techos."""

from fastapi import APIRouter, Depends

from app.calculadora import calcular_estructura
from app.models import Usuario
from app.schemas import CalculoEntrada, CalculoSalida
from app.security import obtener_usuario_actual

router = APIRouter(prefix="/api", tags=["Cálculo Estructural"])


@router.post("/calcular", response_model=CalculoSalida)
def ejecutar_calculo(
    datos: CalculoEntrada,
    _usuario_actual: Usuario = Depends(obtener_usuario_actual),
) -> CalculoSalida:
    """
    Recibe las medidas del techo, valida la sesión activa del usuario y
    devuelve el desglose completo de vigas, tensores, costaneras y láminas.
    """
    resultado = calcular_estructura(
        tipo=datos.tipo,
        largo=datos.largo,
        ancho=datos.ancho,
        alto=datos.alto,
        alero=datos.alero,
        cant_t1=datos.cant_t1,
        cant_t2=datos.cant_t2,
        sep_c=datos.sep_c,
        ancho_u=datos.ancho_u,
        caballete=datos.caballete,
    )
    return CalculoSalida(**resultado)
