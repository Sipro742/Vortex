# VÓRTICE — Calculadora de Estructuras

Aplicación web Full-Stack con arquitectura **Cliente-Servidor segura** para el cálculo estructural de techos tipo **Pirámide** y **Cuatro Aguas**. Toda la lógica matemática y el control de acceso viven aislados en el backend con **FastAPI**, mientras que el frontend en **HTML5, CSS3 y JavaScript Vanilla** actúa únicamente como interfaz interactiva y visualizador 2D en `<canvas>`.

## Características principales

- **Motor matemático protegido en el servidor:** calcula vigas, limatesas, tensores, costaneras y láminas (agrupadas por medida y ordenadas de mayor a menor, descartando cortes `<= 0.05 m`), incluyendo la fórmula corregida para la altura inclinada de Cara 2.
- **Autenticación segura con JWT y bcrypt:** contraseñas almacenadas siempre como hashes `bcrypt` y sesiones firmadas con tokens Bearer JWT.
- **Revocación instantánea de acceso:** cada petición protegida valida el token y consulta en tiempo real el estado `activo` del usuario en SQLite. Si un administrador desactiva una cuenta con sesión abierta, su siguiente solicitud es rechazada inmediatamente con `403 Forbidden`.
- **Panel de Administración integrado:** permite crear usuarios (`admin` o `usuario`) y activar o desactivar accesos en un clic, con regla de negocio que impide al administrador desactivarse a sí mismo (`400 Bad Request`).
- **Frontend ligero y responsivo:** interfaz adaptable a móvil y escritorio con CSS Grid, vista previa 2D proporcional en `<canvas>` protegida contra valores inválidos y manejo automático de sesiones expiradas o revocadas (`401`/`403`).

## Stack tecnológico

| Capa | Tecnologías |
| :--- | :--- |
| **Backend** | Python 3.10+, FastAPI, Uvicorn, SQLAlchemy, SQLite, Pydantic v2, bcrypt, python-jose (JWT) |
| **Frontend** | HTML5, CSS3 (CSS Grid), JavaScript Vanilla (ES6 Modules, Fetch API), HTML5 Canvas 2D |

## Estructura del proyecto

```text
vortice-fullstack/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # App FastAPI, CORS, lifespan y registro de routers
│   │   ├── config.py          # Variables de entorno, JWT, SQLite y orígenes CORS
│   │   ├── database.py        # Engine SQLite, SessionLocal, Base y get_db
│   │   ├── models.py          # Modelo SQLAlchemy Usuario
│   │   ├── schemas.py         # Esquemas Pydantic v2 y validaciones estrictas
│   │   ├── security.py        # Hash bcrypt, JWT y dependencias de rol/estado
│   │   ├── calculadora.py     # Motor matemático estructural puro
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── auth.py        # POST /api/auth/login, GET /api/auth/me
│   │       ├── calculo.py     # POST /api/calcular
│   │       └── admin.py       # Gestión de usuarios y control de estado
│   ├── crear_admin.py         # Script CLI para crear o actualizar el admin inicial
│   └── requirements.txt
└── frontend/
    ├── index.html             # SPA con vistas de Login, Calculadora y Panel Admin
    ├── css/
    │   └── styles.css         # Estilos responsivos (móvil y escritorio)
    └── js/
        ├── api.js             # Cliente HTTP con Bearer Token y manejo de 401/403
        ├── canvas.js          # Dibujo 2D proporcional del techo
        └── main.js            # Control de sesiones, eventos y renderizado
```

## Instalación y puesta en marcha

### Requisitos previos

- Python 3.10 o superior instalado.

### 1. Configurar el backend

Entra a la carpeta `backend/` y crea el entorno virtual:

**Windows (PowerShell):**
```powershell
cd backend
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux / macOS:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Crear el usuario administrador inicial

Ejecuta el script CLI desde `backend/`:

```bash
python crear_admin.py
```

También puedes pasar los datos por parámetros si lo prefieres:

```bash
python crear_admin.py --username admin --password TuClaveSegura
```

Si el usuario ya existe, el script actualiza su contraseña y garantiza `rol="admin"` y `activo=True`.

### 3. Levantar el servidor backend

Desde `backend/`:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API disponible en: `http://127.0.0.1:8000`
- Documentación interactiva (Swagger UI): `http://127.0.0.1:8000/docs`
- Comprobación de estado: `http://127.0.0.1:8000/api/salud`

### 4. Servir el frontend localmente

Abre una segunda terminal en la carpeta `frontend/`:

```bash
cd frontend
python -m http.server 5500
```

Abre **`http://127.0.0.1:5500`** en tu navegador e inicia sesión con tu cuenta de administrador. Para detener cualquiera de los dos servidores, presiona `Ctrl + C` en su terminal correspondiente.

## Endpoints de la API

| Método | Ruta | Acceso | Descripción |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/salud` | Público | Verifica que el backend esté en ejecución |
| `POST` | `/api/auth/login` | Público | Autentica credenciales, valida `activo == True` y emite JWT |
| `GET` | `/api/auth/me` | Usuario activo | Devuelve el perfil del usuario autenticado actual |
| `POST` | `/api/calcular` | Usuario activo | Ejecuta el cálculo estructural y devuelve resumen, tensores, costaneras y láminas |
| `GET` | `/api/admin/usuarios` | Solo `admin` | Lista todos los usuarios registrados sin exponer `password_hash` |
| `POST` | `/api/admin/usuarios` | Solo `admin` | Crea un nuevo usuario (`username`, `password`, `rol`) |
| `PATCH` | `/api/admin/usuarios/{id}/estado` | Solo `admin` | Activa o desactiva un usuario (`{"activo": bool}`) con efecto inmediato |

## Variables de entorno

El backend funciona sin configuración adicional en desarrollo local, pero admite las siguientes variables de entorno para despliegues en producción:

| Variable | Descripción | Valor por defecto |
| :--- | :--- | :--- |
| `VORTICE_SECRET_KEY` | Clave secreta para firmar los tokens JWT | Clave local de desarrollo |
| `VORTICE_JWT_ALGORITMO` | Algoritmo de firma JWT | `HS256` |
| `VORTICE_JWT_EXPIRACION_MINUTOS` | Tiempo de vida de cada token en minutos | `480` (8 horas) |
| `VORTICE_DATABASE_URL` | Cadena de conexión de SQLAlchemy | `sqlite:///.../backend/vortice.db` |
| `VORTICE_CORS_ORIGINS` | Orígenes permitidos separados por coma | Puertos locales (`5500`, `8080`, `3000`, `5173`) |

## Recomendaciones para producción

- Define una clave criptográfica aleatoria en `VORTICE_SECRET_KEY` (por ejemplo, generada con `python -c "import secrets; print(secrets.token_hex(32))"`).
- Configura `VORTICE_CORS_ORIGINS` únicamente con el dominio real de tu frontend y actualiza `URL_BASE_API` en `frontend/js/api.js`.
- Sirve la aplicación siempre detrás de HTTPS (por ejemplo, con Nginx, Caddy o un proveedor cloud con TLS automático).
