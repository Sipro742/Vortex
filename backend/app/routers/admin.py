"""Rutas de administración de usuarios protegidas por rol 'admin'."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.schemas import UsuarioCrear, UsuarioEstadoActualizar, UsuarioSalida
from app.security import hashear_contrasena, requerir_admin

router = APIRouter(prefix="/api/admin", tags=["Administración"])


@router.get("/usuarios", response_model=list[UsuarioSalida])
def listar_usuarios(
    db: Session = Depends(get_db),
    _admin_actual: Usuario = Depends(requerir_admin),
) -> list[UsuarioSalida]:
    """Lista todos los usuarios registrados sin exponer hashes de contraseña."""
    usuarios = db.query(Usuario).order_by(Usuario.id.asc()).all()
    return [UsuarioSalida.model_validate(u) for u in usuarios]


@router.post(
    "/usuarios",
    response_model=UsuarioSalida,
    status_code=status.HTTP_201_CREATED,
)
def crear_usuario(
    datos: UsuarioCrear,
    db: Session = Depends(get_db),
    _admin_actual: Usuario = Depends(requerir_admin),
) -> UsuarioSalida:
    """Registra un nuevo usuario con contraseña hasheada en bcrypt."""
    existente = (
        db.query(Usuario)
        .filter(Usuario.username == datos.username)
        .first()
    )
    if existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El nombre de usuario '{datos.username}' ya está registrado.",
        )

    nuevo_usuario = Usuario(
        username=datos.username,
        password_hash=hashear_contrasena(datos.password),
        rol=datos.rol,
        activo=True,
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return UsuarioSalida.model_validate(nuevo_usuario)


@router.patch("/usuarios/{usuario_id}/estado", response_model=UsuarioSalida)
def actualizar_estado_usuario(
    usuario_id: int,
    datos: UsuarioEstadoActualizar,
    db: Session = Depends(get_db),
    admin_actual: Usuario = Depends(requerir_admin),
) -> UsuarioSalida:
    """Activa o desactiva el acceso de un usuario con efecto inmediato."""
    if usuario_id == admin_actual.id and not datos.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propia cuenta de administrador.",
        )

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )

    usuario.activo = datos.activo
    db.commit()
    db.refresh(usuario)
    return UsuarioSalida.model_validate(usuario)
