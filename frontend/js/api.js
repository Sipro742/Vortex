/**
 * Cliente HTTP para la API de VÓRTICE.
 * Gestiona el almacenamiento del Bearer Token y el manejo centralizado de 401/403.
 */

const URL_BASE_API = "http://127.0.0.1:8000";
const CLAVE_TOKEN_STORAGE = "vortice_access_token";

let manejadorSesionInvalida = null;

export function registrarManejadorSesionInvalida(callback) {
    manejadorSesionInvalida = callback;
}

export function obtenerToken() {
    return localStorage.getItem(CLAVE_TOKEN_STORAGE);
}

export function guardarToken(token) {
    localStorage.setItem(CLAVE_TOKEN_STORAGE, token);
}

export function limpiarToken() {
    localStorage.removeItem(CLAVE_TOKEN_STORAGE);
}

/**
 * Extrae un mensaje legible desde las respuestas de error de FastAPI/Pydantic.
 */
function extraerMensajeError(cuerpo, codigoEstado) {
    if (!cuerpo) {
        return `Error del servidor (código ${codigoEstado}).`;
    }
    if (typeof cuerpo.detail === "string") {
        return cuerpo.detail;
    }
    if (Array.isArray(cuerpo.detail) && cuerpo.detail.length > 0) {
        return cuerpo.detail
            .map((item) => {
                const campo = Array.isArray(item.loc)
                    ? item.loc[item.loc.length - 1]
                    : "";
                return campo ? `${campo}: ${item.msg}` : item.msg;
            })
            .join(" | ");
    }
    return `No se pudo completar la solicitud (código ${codigoEstado}).`;
}

/**
 * Ejecuta una petición HTTP hacia el backend inyectando el Bearer Token.
 */
async function peticionApi(ruta, opciones = {}) {
    const {
        metodo = "GET",
        cuerpo = null,
        requiereAuth = true,
        manejarExpiracion = true,
    } = opciones;

    const encabezados = {
        Accept: "application/json",
    };

    if (cuerpo !== null) {
        encabezados["Content-Type"] = "application/json";
    }

    if (requiereAuth) {
        const token = obtenerToken();
        if (token) {
            encabezados.Authorization = `Bearer ${token}`;
        }
    }

    let respuesta;
    try {
        respuesta = await fetch(`${URL_BASE_API}${ruta}`, {
            method: metodo,
            headers: encabezados,
            body: cuerpo !== null ? JSON.stringify(cuerpo) : undefined,
        });
    } catch (_errorRed) {
        throw new Error(
            "No se pudo conectar con el servidor de VÓRTICE. Verifica que el backend esté en ejecución."
        );
    }

    let datos = null;
    const tipoContenido = respuesta.headers.get("content-type") || "";
    if (tipoContenido.includes("application/json")) {
        datos = await respuesta.json();
    }

    if (!respuesta.ok) {
        const mensaje = extraerMensajeError(datos, respuesta.status);

        if (
            manejarExpiracion &&
            (respuesta.status === 401 || respuesta.status === 403)
        ) {
            limpiarToken();
            if (typeof manejadorSesionInvalida === "function") {
                manejadorSesionInvalida(mensaje);
            }
        }

        const error = new Error(mensaje);
        error.status = respuesta.status;
        throw error;
    }

    return datos;
}

// --- ENDPOINTS DE AUTENTICACIÓN ---

export async function iniciarSesionApi(username, password) {
    return peticionApi("/api/auth/login", {
        metodo: "POST",
        cuerpo: { username, password },
        requiereAuth: false,
        manejarExpiracion: false,
    });
}

export async function obtenerUsuarioActualApi() {
    return peticionApi("/api/auth/me", {
        metodo: "GET",
    });
}

// --- ENDPOINT DE CÁLCULO ESTRUCTURAL ---

export async function calcularEstructuraApi(parametros) {
    return peticionApi("/api/calcular", {
        metodo: "POST",
        cuerpo: parametros,
    });
}

// --- ENDPOINTS DE ADMINISTRACIÓN ---

export async function listarUsuariosApi() {
    return peticionApi("/api/admin/usuarios", {
        metodo: "GET",
    });
}

export async function crearUsuarioApi({ username, password, rol }) {
    return peticionApi("/api/admin/usuarios", {
        metodo: "POST",
        cuerpo: { username, password, rol },
    });
}

export async function cambiarEstadoUsuarioApi(usuarioId, activo) {
    return peticionApi(`/api/admin/usuarios/${usuarioId}/estado`, {
        metodo: "PATCH",
        cuerpo: { activo },
    });
}
