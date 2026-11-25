"""Rutas de autenticación: inicio de sesión y consulta del usuario actual."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.schemas import LoginEntrada, TokenRespuesta, UsuarioSalida
from app.security import (
    crear_token_acceso,
    obtener_usuario_actual,
    verificar_contrasena,
)

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenRespuesta)
def iniciar_sesion(
    credenciales: LoginEntrada,
    db: Session = Depends(get_db),
) -> TokenRespuesta:
    """Autentica al usuario, valida que esté activo y emite un token JWT."""
    usuario = (
        db.query(Usuario)
        .filter(Usuario.username == credenciales.username)
        .first()
    )

    if usuario is None or not verificar_contrasena(
        credenciales.password, usuario.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta ha sido desactivada. Contacta al administrador.",
        )

    token = crear_token_acceso(usuario)
    return TokenRespuesta(
        access_token=token,
        token_type="bearer",
        usuario=UsuarioSalida.model_validate(usuario),
    )


@router.get("/me", response_model=UsuarioSalida)
def obtener_perfil_actual(
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
) -> UsuarioSalida:
    """Devuelve los datos del usuario autenticado actualmente."""
    return UsuarioSalida.model_validate(usuario_actual)
