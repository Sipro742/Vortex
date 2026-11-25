"""Seguridad: hash de contraseñas con bcrypt, JWT y revocación instantánea."""

from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import ALGORITMO_JWT, EXPIRACION_TOKEN_MINUTOS, SECRET_KEY
from app.database import get_db
from app.models import Usuario

esquema_bearer = HTTPBearer(auto_error=False)


def hashear_contrasena(contrasena_plana: str) -> str:
    """Genera un hash seguro con bcrypt a partir de una contraseña en texto plano."""
    bytes_contrasena = contrasena_plana.encode("utf-8")
    if len(bytes_contrasena) > 72:
        raise ValueError(
            "La contraseña excede el límite máximo de 72 bytes permitido por bcrypt."
        )
    sal = bcrypt.gensalt()
    return bcrypt.hashpw(bytes_contrasena, sal).decode("utf-8")


def verificar_contrasena(contrasena_plana: str, password_hash: str) -> bool:
    """Compara una contraseña en texto plano contra su hash bcrypt almacenado."""
    try:
        return bcrypt.checkpw(
            contrasena_plana.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False


def crear_token_acceso(usuario: Usuario) -> str:
    """Firma un token JWT con la identidad del usuario y fecha de expiración UTC."""
    ahora_utc = datetime.now(timezone.utc)
    expiracion = ahora_utc + timedelta(minutes=EXPIRACION_TOKEN_MINUTOS)
    carga_util = {
        "sub": str(usuario.id),
        "username": usuario.username,
        "rol": usuario.rol,
        "iat": int(ahora_utc.timestamp()),
        "exp": int(expiracion.timestamp()),
    }
    return jwt.encode(carga_util, SECRET_KEY, algorithm=ALGORITMO_JWT)


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(esquema_bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    """
    Decodifica el JWT y consulta la base de datos en tiempo real para verificar
    que el usuario sigue existiendo y permanece activo (revocación instantánea).
    """
    if credenciales is None or not credenciales.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación. Inicia sesión para continuar.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credenciales.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMO_JWT])
        sujeto = payload.get("sub")
        if sujeto is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: falta el identificador de usuario.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        usuario_id = int(sujeto)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tu sesión ha expirado o el token es inválido.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El usuario asociado a esta sesión ya no existe.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta ha sido desactivada. Contacta al administrador.",
        )

    return usuario


def requerir_admin(
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
) -> Usuario:
    """Restringe el acceso únicamente a usuarios activos con rol 'admin'."""
    if usuario_actual.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: se requieren permisos de administrador.",
        )
    return usuario_actual
