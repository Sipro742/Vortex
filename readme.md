# VÓRTICE — Structural Calculator



Full-Stack web application for the structural calculation of Pyramid and Hip roofs, featuring role-based authentication, real-time access control, and 2D geometric visualization.



---



## Key Features



- **Centralized structural calculation:** determines beams, hip rafters, tie rods, purlins, and roofing sheets (grouped by length and sorted in descending order, discarding cuts less than or equal to `0.05 m`), including the slope height calculation for Face 2.

- **JWT & bcrypt authentication:** credentials secured via bcrypt hashes and sessions managed with JWT Bearer tokens.

- **Instant session revocation:** every protected request verifies token validity and the user's active status in the database, enforcing immediate blocks (`403 Forbidden`).

- **User management:** administrative panel to create accounts (`admin` or `user`) and toggle their active status, preventing administrator self-deactivation (`400 Bad Request`).

- **Responsive interface & 2D viewer:** adaptive design for desktop and mobile devices with proportional rendering on `<canvas>` and automatic handling of `401` and `403` responses.



---



## Tech Stack



| Layer | Technologies |

| :--- | :--- |

| **Backend** | Python 3.10+, FastAPI, Uvicorn, SQLAlchemy, SQLite, Pydantic v2, bcrypt, python-jose |

| **Frontend** | HTML5, CSS3 (CSS Grid), Vanilla JavaScript (ES6 Modules, Fetch API), HTML5 Canvas 2D |



---



## Project Structure



```text

vortice-fullstack/

├── backend/

│   ├── app/

│   │   ├── __init__.py

│   │   ├── main.py            # FastAPI setup, CORS, lifecycle, and routing

│   │   ├── config.py          # Environment variables and security parameters

│   │   ├── database.py        # Database connection and session management

│   │   ├── models.py          # Persistent models

│   │   ├── schemas.py         # Input/output contracts and validations

│   │   ├── security.py        # Hashing, JWT issuance/validation, and access control

│   │   ├── calculadora.py     # Geometric and structural calculation logic

│   │   └── routers/

│   │       ├── __init__.py

│   │       ├── auth.py        # Authentication and profile lookup

│   │       ├── calculo.py     # Structural calculation endpoint

│   │       └── admin.py       # User administration

│   ├── crear_admin.py         # CLI utility to initialize or update the administrator

│   └── requirements.txt

└── frontend/

    ├── index.html             # Main interface (login, calculator, and administration)

    ├── css/

    │   └── styles.css         # Responsive stylesheet

    └── js/

        ├── api.js             # HTTP communication and session control

        ├── canvas.js          # 2D rendering of the structure

        └── main.js            # View orchestration and UI events

```



---



## Installation & Setup



### Prerequisites



- Python 3.10 or higher.



### 1. Set up the backend environment



Navigate to `backend/` and create a virtual environment:



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



### 2. Create or update the administrator user



From `backend/`, run:



```bash

python crear_admin.py

```



You can also specify credentials via command-line arguments:



```bash

python crear_admin.py --username admin --password YourSecurePassword

```



If the user already exists, their password is updated and `rol="admin"` with `activo=True` is enforced.



### 3. Start the backend server



From `backend/`:



```bash

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

```



- **API:** `http://127.0.0.1:8000`

- **Interactive documentation (Swagger UI):** `http://127.0.0.1:8000/docs`

- **Health check:** `http://127.0.0.1:8000/api/salud`



### 4. Serve the frontend



In a second terminal, from `frontend/`:



```bash

cd frontend

python -m http.server 5500

```



Open `http://127.0.0.1:5500` in your browser and log in with the administrator account. To stop either service, press `Ctrl + C` in its respective terminal.



---



## API Endpoints



| Method | Endpoint | Access | Description |

| :--- | :--- | :--- | :--- |

| `GET` | `/api/salud` | Public | Verifies service status |

| `POST` | `/api/auth/login` | Public | Authenticates credentials, checks active status, and issues a JWT token |

| `GET` | `/api/auth/me` | Active user | Returns the authenticated user's profile |

| `POST` | `/api/calcular` | Active user | Calculates structural elements and returns summary, tie rods, purlins, and sheets |

| `GET` | `/api/admin/usuarios` | Admin only | Lists registered users without exposing password hashes |

| `POST` | `/api/admin/usuarios` | Admin only | Registers a new user (`username`, `password`, `rol`) |

| `PATCH` | `/api/admin/usuarios/{id}/estado` | Admin only | Enables or disables an account (`{"activo": bool}`) with immediate effect |



---



## Environment Variables



The project runs with default values in local development and supports the following variables in deployment environments:



| Variable | Description | Default Value |

| :--- | :--- | :--- |

| `VORTICE_SECRET_KEY` | Secret key used to sign JWT tokens | Local development key |

| `VORTICE_JWT_ALGORITMO` | Cryptographic JWT signing algorithm | `HS256` |

| `VORTICE_JWT_EXPIRACION_MINUTOS` | Token lifetime in minutes | `480` (8 hours) |

| `VORTICE_DATABASE_URL` | Database connection string | `sqlite:///.../backend/vortice.db` |

| `VORTICE_CORS_ORIGINS` | Comma-separated allowed origins | Local ports (`5500`, `8080`, `3000`, `5173`) |



---



## Production Recommendations



- Generate a secure random key for `VORTICE_SECRET_KEY` (e.g., using `python -c "import secrets; print(secrets.token_hex(32))"`).

- Restrict `VORTICE_CORS_ORIGINS` to your production frontend domain and update `URL_BASE_API` in `frontend/js/api.js`.

- Always serve the application over HTTPS using a reverse proxy or a cloud provider with TLS enabled.
