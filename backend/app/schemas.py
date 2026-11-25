"""Esquemas Pydantic v2 para autenticación, usuarios y cálculos estructurales."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# --- ESQUEMAS DE AUTENTICACIÓN Y USUARIOS ---


class LoginEntrada(BaseModel):
    """Credenciales enviadas en el inicio de sesión."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("username")
    @classmethod
    def normalizar_username(cls, valor: str) -> str:
        limpio = valor.strip().lower()
        if not limpio:
            raise ValueError("El nombre de usuario no puede estar vacío.")
        return limpio


class UsuarioCrear(BaseModel):
    """Datos requeridos por un administrador para registrar un nuevo usuario."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    rol: Literal["admin", "usuario"] = Field(default="usuario")

    @field_validator("username")
    @classmethod
    def validar_username(cls, valor: str) -> str:
        limpio = valor.strip().lower()
        if not limpio:
            raise ValueError("El nombre de usuario no puede estar vacío.")
        if " " in limpio:
            raise ValueError("El nombre de usuario no puede contener espacios.")
        return limpio

    @field_validator("password")
    @classmethod
    def validar_password_bytes(cls, valor: str) -> str:
        if len(valor.encode("utf-8")) > 72:
            raise ValueError(
                "La contraseña excede el límite máximo de 72 bytes para bcrypt."
            )
        return valor


class UsuarioEstadoActualizar(BaseModel):
    """Payload para activar o desactivar el acceso de un usuario."""

    activo: bool


class UsuarioSalida(BaseModel):
    """Representación pública de un usuario (sin exponer password_hash)."""

    id: int
    username: str
    rol: Literal["admin", "usuario"]
    activo: bool
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenRespuesta(BaseModel):
    """Respuesta del endpoint de login con JWT y datos del usuario."""

    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioSalida


# --- ESQUEMAS DEL MOTOR DE CÁLCULO ---


class CalculoEntrada(BaseModel):
    """Parámetros geométricos y constructivos de entrada para el cálculo."""

    tipo: Literal["piramide", "normal"] = Field(
        ..., description="Tipo de techo: 'piramide' o 'normal' (Cuatro Aguas)."
    )
    largo: float = Field(..., gt=0, description="Largo base del techo en metros.")
    ancho: float = Field(..., gt=0, description="Ancho base del techo en metros.")
    alto: float = Field(..., gt=0, description="Altura del techo en metros.")
    alero: float = Field(..., ge=0, description="Medida del alero en metros.")
    cant_t1: int = Field(
        ..., ge=0, description="Cantidad de tensores por lado en Cara 1."
    )
    cant_t2: int = Field(
        ..., ge=0, description="Cantidad de tensores por lado en Cara 2."
    )
    sep_c: float = Field(
        ..., gt=0, description="Separación entre costaneras en metros."
    )
    ancho_u: float = Field(
        ..., gt=0, description="Ancho útil de cada lámina en metros."
    )
    caballete: float = Field(
        default=0.0,
        ge=0,
        description="Longitud del caballete en metros (aplica a tipo 'normal').",
    )

    @model_validator(mode="after")
    def validar_consistencia_caballete(self) -> "CalculoEntrada":
        if self.tipo == "normal":
            largo_total = self.largo + (self.alero * 2)
            if self.caballete >= largo_total:
                raise ValueError(
                    "Para un techo de cuatro aguas ('normal'), el caballete "
                    "debe ser estrictamente menor que largo + 2 * alero "
                    f"({largo_total:.2f} m)."
                )
        return self


class ResumenCalculo(BaseModel):
    """Totales generales y dimensiones derivadas de la estructura."""

    total_vigas: float
    total_costaneras: float
    caballete: float
    largo_total: float
    ancho_total: float
    hipotenusa_central: float
    brazo_limatesa: float
    altura_triangulo_cara2: float


class ItemTensor(BaseModel):
    """Medida individual de un tensor."""

    etiqueta: str
    largo: float


class ReporteTensores(BaseModel):
    """Desglose de limatesas y tensores en ambas caras."""

    limatesas_cantidad: int
    limatesas_largo: float
    cara_1: list[ItemTensor]
    cara_2: list[ItemTensor]


class ItemCostanera(BaseModel):
    """Medida individual de una hilera de costanera."""

    posicion: float
    largo: float


class ReporteCostaneras(BaseModel):
    """Desglose de costaneras en ambas caras."""

    cara_1: list[ItemCostanera]
    cara_2: list[ItemCostanera]


class GrupoLamina(BaseModel):
    """Grupo de láminas con la misma longitud redondeada."""

    cantidad: int
    largo: float


class ReporteLaminas(BaseModel):
    """Desglose de láminas agrupadas por medida y ordenadas de mayor a menor."""

    cara_1: list[GrupoLamina]
    cara_2: list[GrupoLamina]


class CalculoSalida(BaseModel):
    """Resultado estructurado completo del cálculo estructural."""

    resumen: ResumenCalculo
    tensores: ReporteTensores
    costaneras: ReporteCostaneras
    laminas: ReporteLaminas
