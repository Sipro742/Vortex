"""Motor matemático estructural puro de VÓRTICE (sin dependencias web)."""

import math
from typing import Any

TOLERANCIA_FLOTANTE = 1e-9
CORTE_MINIMO_LAMINA = 0.05


def _calcular_largo_cara_1(
    distancia_centro: float,
    largo_total: float,
    caballete: float,
    hipotenusa_central: float,
) -> float:
    """Calcula la longitud inclinada en Cara 1 según la distancia al eje central."""
    if distancia_centro <= caballete / 2:
        return hipotenusa_central
    tramo_inclinado = (largo_total - caballete) / 2
    return hipotenusa_central * (
        1.0 - (distancia_centro - caballete / 2) / tramo_inclinado
    )


def calcular_estructura(
    *,
    tipo: str,
    largo: float,
    ancho: float,
    alto: float,
    alero: float,
    cant_t1: int,
    cant_t2: int,
    sep_c: float,
    ancho_u: float,
    caballete: float = 0.0,
) -> dict[str, Any]:
    """
    Calcula tensores, costaneras, láminas y totales de una estructura de techo
    tipo 'piramide' o 'normal' (Cuatro Aguas).
    """
    largo_total = largo + (alero * 2)
    ancho_total = ancho + (alero * 2)
    cab = caballete if tipo == "normal" else 0.0

    hip_central = math.sqrt((ancho_total / 2) ** 2 + alto**2)
    brazo = math.sqrt(
        ((largo_total - cab) / 2) ** 2 + (ancho_total / 2) ** 2 + alto**2
    )
    # Fórmula corregida para la altura inclinada del triángulo de Cara 2
    alt_tri = math.sqrt(brazo**2 - (ancho_total / 2) ** 2)

    total_vigas = (brazo * 4) + cab
    total_costaneras = 0.0

    # --- 1. CÁLCULO DE TENSORES ---
    tensores_cara_1: list[dict[str, Any]] = []
    for i in range(1, cant_t1 + 1):
        d = abs((largo_total / (cant_t1 + 1)) * i - largo_total / 2)
        largo_tensor = _calcular_largo_cara_1(d, largo_total, cab, hip_central)
        if largo_tensor > 0:
            tensores_cara_1.append(
                {
                    "etiqueta": f"T-{i}",
                    "largo": round(largo_tensor, 2),
                }
            )
            total_vigas += largo_tensor * 2

    tensores_cara_2: list[dict[str, Any]] = []
    for i in range(1, cant_t2 + 1):
        d = abs((ancho_total / (cant_t2 + 1)) * i - ancho_total / 2)
        largo_tensor = alt_tri * (1.0 - d / (ancho_total / 2))
        if largo_tensor > 0:
            tensores_cara_2.append(
                {
                    "etiqueta": f"T-{i}",
                    "largo": round(largo_tensor, 2),
                }
            )
            total_vigas += largo_tensor * 2

    # --- 2. CÁLCULO DE COSTANERAS ---
    costaneras_cara_1: list[dict[str, float]] = []
    paso = 0
    while True:
        j = paso * sep_c
        if j > hip_central + TOLERANCIA_FLOTANTE:
            break
        largo_costanera = largo_total - (j / hip_central) * (largo_total - cab)
        if largo_costanera < 0 and abs(largo_costanera) <= TOLERANCIA_FLOTANTE:
            largo_costanera = 0.0
        costaneras_cara_1.append(
            {
                "posicion": round(j, 2),
                "largo": round(largo_costanera, 2),
            }
        )
        total_costaneras += largo_costanera * 2
        paso += 1

    costaneras_cara_2: list[dict[str, float]] = []
    paso = 0
    while True:
        j = paso * sep_c
        if j > alt_tri + TOLERANCIA_FLOTANTE:
            break
        largo_costanera = ancho_total - (j / alt_tri) * ancho_total
        if largo_costanera < 0 and abs(largo_costanera) <= TOLERANCIA_FLOTANTE:
            largo_costanera = 0.0
        costaneras_cara_2.append(
            {
                "posicion": round(j, 2),
                "largo": round(largo_costanera, 2),
            }
        )
        total_costaneras += largo_costanera * 2
        paso += 1

    # --- 3. CÁLCULO DE LÁMINAS (AGRUPADAS POR MEDIDA, DESCARTANDO <= 0.05 m) ---
    mapa_laminas_1: dict[float, int] = {}
    indice = 0
    while True:
        k = indice * ancho_u
        if k >= largo_total - TOLERANCIA_FLOTANTE:
            break
        d = abs((k + ancho_u / 2) - largo_total / 2)
        largo_lamina = _calcular_largo_cara_1(d, largo_total, cab, hip_central)
        if largo_lamina > CORTE_MINIMO_LAMINA:
            medida = round(largo_lamina, 2)
            mapa_laminas_1[medida] = mapa_laminas_1.get(medida, 0) + 2
        indice += 1

    mapa_laminas_2: dict[float, int] = {}
    indice = 0
    while True:
        k = indice * ancho_u
        if k >= ancho_total - TOLERANCIA_FLOTANTE:
            break
        d = abs((k + ancho_u / 2) - ancho_total / 2)
        largo_lamina = alt_tri * (1.0 - (d / (ancho_total / 2)))
        if largo_lamina > CORTE_MINIMO_LAMINA:
            medida = round(largo_lamina, 2)
            mapa_laminas_2[medida] = mapa_laminas_2.get(medida, 0) + 2
        indice += 1

    laminas_cara_1 = [
        {"cantidad": cantidad, "largo": medida}
        for medida, cantidad in sorted(
            mapa_laminas_1.items(), key=lambda par: par[0], reverse=True
        )
    ]
    laminas_cara_2 = [
        {"cantidad": cantidad, "largo": medida}
        for medida, cantidad in sorted(
            mapa_laminas_2.items(), key=lambda par: par[0], reverse=True
        )
    ]

    return {
        "resumen": {
            "total_vigas": round(total_vigas, 2),
            "total_costaneras": round(total_costaneras, 2),
            "caballete": round(cab, 2),
            "largo_total": round(largo_total, 2),
            "ancho_total": round(ancho_total, 2),
            "hipotenusa_central": round(hip_central, 2),
            "brazo_limatesa": round(brazo, 2),
            "altura_triangulo_cara2": round(alt_tri, 2),
        },
        "tensores": {
            "limatesas_cantidad": 4,
            "limatesas_largo": round(brazo, 2),
            "cara_1": tensores_cara_1,
            "cara_2": tensores_cara_2,
        },
        "costaneras": {
            "cara_1": costaneras_cara_1,
            "cara_2": costaneras_cara_2,
        },
        "laminas": {
            "cara_1": laminas_cara_1,
            "cara_2": laminas_cara_2,
        },
    }
