"""Script CLI para crear o actualizar el usuario administrador inicial."""

import argparse
import getpass
import sys

from app.database import Base, SessionLocal, engine
from app.models import Usuario
from app.security import hashear_contrasena


def solicitar_datos_interactivos(
    username_arg: str | None,
    password_arg: str | None,
) -> tuple[str, str]:
    """Solicita usuario y contraseña por consola si no se pasaron por bandera."""
    if username_arg:
        username = username_arg.strip().lower()
    else:
        username = input("Nombre de usuario administrador [admin]: ").strip().lower()
        if not username:
            username = "admin"

    if len(username) < 3 or " " in username:
        print(
            "Error: El usuario debe tener al menos 3 caracteres y no contener espacios.",
            file=sys.stderr,
        )
        sys.exit(1)

    if password_arg:
        password = password_arg
    else:
        password = getpass.getpass("Contraseña (mínimo 6 caracteres): ")
        confirmacion = getpass.getpass("Confirmar contraseña: ")
        if password != confirmacion:
            print("Error: Las contraseñas no coinciden.", file=sys.stderr)
            sys.exit(1)

    if len(password) < 6:
        print(
            "Error: La contraseña debe tener al menos 6 caracteres.",
            file=sys.stderr,
        )
        sys.exit(1)

    if len(password.encode("utf-8")) > 72:
        print(
            "Error: La contraseña excede el límite de 72 bytes para bcrypt.",
            file=sys.stderr,
        )
        sys.exit(1)

    return username, password


def crear_o_actualizar_admin(username: str, password: str) -> None:
    """Crea el administrador inicial o actualiza su contraseña y permisos."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.username == username).first()
        hash_seguro = hashear_contrasena(password)

        if usuario is None:
            nuevo_admin = Usuario(
                username=username,
                password_hash=hash_seguro,
                rol="admin",
                activo=True,
            )
            db.add(nuevo_admin)
            db.commit()
            print(f"Administrador '{username}' creado correctamente.")
        else:
            usuario.password_hash = hash_seguro
            usuario.rol = "admin"
            usuario.activo = True
            db.commit()
            print(
                f"Administrador '{username}' actualizado (contraseña, rol='admin' y activo=True)."
            )
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crea o actualiza el usuario administrador inicial de VÓRTICE."
    )
    parser.add_argument(
        "--username",
        "-u",
        help="Nombre de usuario administrador (opcional; si se omite se solicita por consola).",
    )
    parser.add_argument(
        "--password",
        "-p",
        help="Contraseña del administrador (opcional; si se omite se solicita de forma oculta).",
    )
    args = parser.parse_args()

    username, password = solicitar_datos_interactivos(args.username, args.password)
    crear_o_actualizar_admin(username, password)


if __name__ == "__main__":
    main()
