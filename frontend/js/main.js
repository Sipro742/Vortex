/**
 * Controlador principal de la SPA VÓRTICE:
 * gestión de sesiones, eventos de la calculadora, renderizado de reportes y panel admin.
 */

import {
    calcularEstructuraApi,
    cambiarEstadoUsuarioApi,
    crearUsuarioApi,
    guardarToken,
    iniciarSesionApi,
    limpiarToken,
    listarUsuariosApi,
    obtenerToken,
    obtenerUsuarioActualApi,
    registrarManejadorSesionInvalida,
} from "./api.js";
import { dibujarPlantaTecho } from "./canvas.js";

// Estado global en memoria de la sesión activa
let usuarioAutenticado = null;
let enVistaAdmin = false;

// Referencias a elementos del DOM
const vistaLogin = document.getElementById("vistaLogin");
const vistaAplicacion = document.getElementById("vistaAplicacion");
const vistaCalculadora = document.getElementById("vistaCalculadora");
const vistaAdmin = document.getElementById("vistaAdmin");

const alertaLogin = document.getElementById("alertaLogin");
const formularioLogin = document.getElementById("formularioLogin");
const inputLoginUsername = document.getElementById("loginUsername");
const inputLoginPassword = document.getElementById("loginPassword");
const btnIniciarSesion = document.getElementById("btnIniciarSesion");

const nombreUsuarioActual = document.getElementById("nombreUsuarioActual");
const badgeRolUsuario = document.getElementById("badgeRolUsuario");
const btnAlternarAdmin = document.getElementById("btnAlternarAdmin");
const btnCerrarSesion = document.getElementById("btnCerrarSesion");

const alertaCalculo = document.getElementById("alertaCalculo");
const selectTipoTecho = document.getElementById("tipoTecho");
const boxCaballete = document.getElementById("boxCaballete");
const inputLargo = document.getElementById("largo");
const inputAncho = document.getElementById("ancho");
const inputAlto = document.getElementById("alto");
const inputCaballete = document.getElementById("caballete");
const inputAlero = document.getElementById("alero");
const inputCantT1 = document.getElementById("cantT1");
const inputCantT2 = document.getElementById("cantT2");
const inputSepC = document.getElementById("sepC");
const inputAnchoU = document.getElementById("anchoU");
const canvasTecho = document.getElementById("canvasTecho");
const btnCalcular = document.getElementById("btnCalcular");

const areaResultados = document.getElementById("resultados");
const totalEstructura = document.getElementById("totalEstructura");
const totalCostanerasMetraje = document.getElementById("totalCostanerasMetraje");
const largoCaballeteRes = document.getElementById("largoCaballeteRes");
const resTensores = document.getElementById("resTensores");
const resCostaneras = document.getElementById("resCostaneras");
const resLaminas = document.getElementById("resLaminas");

const alertaAdmin = document.getElementById("alertaAdmin");
const btnVolverCalculadora = document.getElementById("btnVolverCalculadora");
const formularioCrearUsuario = document.getElementById("formularioCrearUsuario");
const inputNuevoUsername = document.getElementById("nuevoUsername");
const inputNuevoPassword = document.getElementById("nuevoPassword");
const selectNuevoRol = document.getElementById("nuevoRol");
const btnCrearUsuario = document.getElementById("btnCrearUsuario");
const btnRecargarUsuarios = document.getElementById("btnRecargarUsuarios");
const cuerpoTablaUsuarios = document.getElementById("cuerpoTablaUsuarios");

// --- UTILIDADES DE INTERFAZ ---

function mostrarAlerta(elemento, mensaje, tipo = "error") {
    elemento.textContent = mensaje;
    elemento.classList.remove("oculto", "alerta-error", "alerta-exito");
    elemento.classList.add(tipo === "exito" ? "alerta-exito" : "alerta-error");
}

function ocultarAlerta(elemento) {
    elemento.textContent = "";
    elemento.classList.add("oculto");
}

function formatearMetros(valor) {
    return `${Number(valor).toFixed(2)} m`;
}

function crearFilaLista(etiqueta, valor, enNegrita = false) {
    const fila = document.createElement("div");
    fila.className = "item-lista";

    const izquierdo = document.createElement(enNegrita ? "b" : "span");
    izquierdo.textContent = etiqueta;

    const derecho = document.createElement(enNegrita ? "b" : "span");
    derecho.textContent = valor;

    fila.append(izquierdo, derecho);
    return fila;
}

function crearSubtituloReporte(texto) {
    const etiqueta = document.createElement("span");
    etiqueta.className = "sub-titulo";
    etiqueta.textContent = texto;
    return etiqueta;
}

// --- CONTROL DE VISTAS Y SESIÓN ---

function mostrarVistaLogin(mensajeMotivo = "") {
    usuarioAutenticado = null;
    enVistaAdmin = false;
    vistaAplicacion.classList.add("oculto");
    vistaAdmin.classList.add("oculto");
    vistaCalculadora.classList.remove("oculto");
    vistaLogin.classList.remove("oculto");
    areaResultados.classList.add("oculto");
    ocultarAlerta(alertaCalculo);
    ocultarAlerta(alertaAdmin);

    if (mensajeMotivo) {
        mostrarAlerta(alertaLogin, mensajeMotivo, "error");
    } else {
        ocultarAlerta(alertaLogin);
    }

    inputLoginPassword.value = "";
    inputLoginUsername.focus();
}

function mostrarVistaAplicacion(usuario) {
    usuarioAutenticado = usuario;
    nombreUsuarioActual.textContent = usuario.username;
    badgeRolUsuario.textContent = usuario.rol;

    if (usuario.rol === "admin") {
        btnAlternarAdmin.classList.remove("oculto");
    } else {
        btnAlternarAdmin.classList.add("oculto");
    }

    vistaLogin.classList.add("oculto");
    vistaAplicacion.classList.remove("oculto");
    mostrarVistaCalculadora();
    actualizarVistaPreviaTecho();
}

function mostrarVistaCalculadora() {
    enVistaAdmin = false;
    vistaAdmin.classList.add("oculto");
    vistaCalculadora.classList.remove("oculto");
    btnAlternarAdmin.textContent = "Panel Admin";
}

async function mostrarVistaAdmin() {
    if (!usuarioAutenticado || usuarioAutenticado.rol !== "admin") {
        return;
    }
    enVistaAdmin = true;
    vistaCalculadora.classList.add("oculto");
    vistaAdmin.classList.remove("oculto");
    btnAlternarAdmin.textContent = "Calculadora";
    ocultarAlerta(alertaAdmin);
    await cargarTablaUsuarios();
}

function cerrarSesion(mensajeMotivo = "") {
    limpiarToken();
    mostrarVistaLogin(mensajeMotivo);
}

// --- VISTA PREVIA 2D ---

function actualizarVistaPreviaTecho() {
    const tipo = selectTipoTecho.value;
    if (tipo === "normal") {
        boxCaballete.classList.remove("oculto");
    } else {
        boxCaballete.classList.add("oculto");
    }

    dibujarPlantaTecho(canvasTecho, {
        tipo,
        largo: parseFloat(inputLargo.value),
        ancho: parseFloat(inputAncho.value),
        caballete: parseFloat(inputCaballete.value),
    });
}

// --- CÁLCULO ESTRUCTURAL VÍA API ---

function renderizarResultados(datos) {
    totalEstructura.textContent = formatearMetros(datos.resumen.total_vigas);
    totalCostanerasMetraje.textContent = formatearMetros(
        datos.resumen.total_costaneras
    );
    largoCaballeteRes.textContent = formatearMetros(datos.resumen.caballete);

    // Reporte de Tensores
    resTensores.innerHTML = "";
    resTensores.appendChild(
        crearFilaLista(
            `Limatesas (x${datos.tensores.limatesas_cantidad}):`,
            formatearMetros(datos.tensores.limatesas_largo),
            true
        )
    );
    resTensores.appendChild(crearSubtituloReporte("Cara 1 (x2)"));
    if (datos.tensores.cara_1.length === 0) {
        resTensores.appendChild(crearFilaLista("Sin tensores", "—"));
    } else {
        datos.tensores.cara_1.forEach((item) => {
            resTensores.appendChild(
                crearFilaLista(`${item.etiqueta}:`, formatearMetros(item.largo))
            );
        });
    }

    resTensores.appendChild(crearSubtituloReporte("Cara 2 (x2)"));
    if (datos.tensores.cara_2.length === 0) {
        resTensores.appendChild(crearFilaLista("Sin tensores", "—"));
    } else {
        datos.tensores.cara_2.forEach((item) => {
            resTensores.appendChild(
                crearFilaLista(`${item.etiqueta}:`, formatearMetros(item.largo))
            );
        });
    }

    // Reporte de Costaneras
    resCostaneras.innerHTML = "";
    resCostaneras.appendChild(crearSubtituloReporte("Cara 1"));
    datos.costaneras.cara_1.forEach((item) => {
        resCostaneras.appendChild(
            crearFilaLista("Largo:", formatearMetros(item.largo))
        );
    });
    resCostaneras.appendChild(crearSubtituloReporte("Cara 2"));
    datos.costaneras.cara_2.forEach((item) => {
        resCostaneras.appendChild(
            crearFilaLista("Largo:", formatearMetros(item.largo))
        );
    });

    // Reporte de Láminas
    resLaminas.innerHTML = "";
    resLaminas.appendChild(crearSubtituloReporte("Cara 1"));
    if (datos.laminas.cara_1.length === 0) {
        resLaminas.appendChild(crearFilaLista("Sin cortes válidos", "—"));
    } else {
        datos.laminas.cara_1.forEach((grupo) => {
            resLaminas.appendChild(
                crearFilaLista(
                    `${grupo.cantidad} láminas`,
                    formatearMetros(grupo.largo)
                )
            );
        });
    }

    resLaminas.appendChild(crearSubtituloReporte("Cara 2"));
    if (datos.laminas.cara_2.length === 0) {
        resLaminas.appendChild(crearFilaLista("Sin cortes válidos", "—"));
    } else {
        datos.laminas.cara_2.forEach((grupo) => {
            resLaminas.appendChild(
                crearFilaLista(
                    `${grupo.cantidad} láminas`,
                    formatearMetros(grupo.largo)
                )
            );
        });
    }

    areaResultados.classList.remove("oculto");
}

async function manejarCalculo() {
    ocultarAlerta(alertaCalculo);
    btnCalcular.disabled = true;
    btnCalcular.textContent = "CALCULANDO...";

    const payload = {
        tipo: selectTipoTecho.value,
        largo: parseFloat(inputLargo.value),
        ancho: parseFloat(inputAncho.value),
        alto: parseFloat(inputAlto.value),
        alero: parseFloat(inputAlero.value),
        cant_t1: parseInt(inputCantT1.value, 10),
        cant_t2: parseInt(inputCantT2.value, 10),
        sep_c: parseFloat(inputSepC.value),
        ancho_u: parseFloat(inputAnchoU.value),
        caballete:
            selectTipoTecho.value === "normal"
                ? parseFloat(inputCaballete.value)
                : 0,
    };

    try {
        const resultado = await calcularEstructuraApi(payload);
        renderizarResultados(resultado);
    } catch (error) {
        if (error.status !== 401 && error.status !== 403) {
            mostrarAlerta(alertaCalculo, error.message, "error");
        }
    } finally {
        btnCalcular.disabled = false;
        btnCalcular.textContent = "CALCULAR ESTRUCTURA";
    }
}

// --- PANEL DE ADMINISTRACIÓN ---

function renderizarTablaUsuarios(usuarios) {
    cuerpoTablaUsuarios.innerHTML = "";

    if (usuarios.length === 0) {
        const filaVacia = document.createElement("tr");
        const celda = document.createElement("td");
        celda.colSpan = 5;
        celda.className = "texto-centrado";
        celda.textContent = "No hay usuarios registrados.";
        filaVacia.appendChild(celda);
        cuerpoTablaUsuarios.appendChild(filaVacia);
        return;
    }

    usuarios.forEach((usuario) => {
        const fila = document.createElement("tr");

        const tdId = document.createElement("td");
        tdId.textContent = String(usuario.id);

        const tdUsuario = document.createElement("td");
        tdUsuario.textContent = usuario.username;

        const tdRol = document.createElement("td");
        const spanRol = document.createElement("span");
        spanRol.className = "badge-rol";
        spanRol.textContent = usuario.rol;
        tdRol.appendChild(spanRol);

        const tdEstado = document.createElement("td");
        const spanEstado = document.createElement("span");
        spanEstado.className = `estado-pill ${
            usuario.activo ? "estado-activo" : "estado-inactivo"
        }`;
        spanEstado.textContent = usuario.activo ? "Activo" : "Inactivo";
        tdEstado.appendChild(spanEstado);

        const tdAccion = document.createElement("td");
        const btnEstado = document.createElement("button");
        btnEstado.type = "button";
        btnEstado.className = `btn-toggle ${
            usuario.activo ? "btn-desactivar" : "btn-activar"
        }`;
        btnEstado.textContent = usuario.activo ? "Desactivar" : "Activar";

        const esPropioAdmin =
            usuarioAutenticado && usuario.id === usuarioAutenticado.id;
        if (esPropioAdmin && usuario.activo) {
            btnEstado.disabled = true;
            btnEstado.title = "No puedes desactivar tu propia cuenta";
        } else {
            btnEstado.addEventListener("click", () =>
                alternarEstadoUsuario(usuario, btnEstado)
            );
        }

        tdAccion.appendChild(btnEstado);
        fila.append(tdId, tdUsuario, tdRol, tdEstado, tdAccion);
        cuerpoTablaUsuarios.appendChild(fila);
    });
}

async function cargarTablaUsuarios() {
    try {
        const usuarios = await listarUsuariosApi();
        renderizarTablaUsuarios(usuarios);
    } catch (error) {
        if (error.status !== 401 && error.status !== 403) {
            mostrarAlerta(alertaAdmin, error.message, "error");
        }
    }
}

async function alternarEstadoUsuario(usuario, boton) {
    ocultarAlerta(alertaAdmin);
    boton.disabled = true;

    try {
        const nuevoEstado = !usuario.activo;
        const actualizado = await cambiarEstadoUsuarioApi(
            usuario.id,
            nuevoEstado
        );
        mostrarAlerta(
            alertaAdmin,
            `Acceso de '${actualizado.username}' ${
                actualizado.activo ? "activado" : "desactivado"
            } correctamente.`,
            "exito"
        );
        await cargarTablaUsuarios();
    } catch (error) {
        if (error.status !== 401 && error.status !== 403) {
            mostrarAlerta(alertaAdmin, error.message, "error");
        }
        boton.disabled = false;
    }
}

async function manejarCrearUsuario(evento) {
    evento.preventDefault();
    ocultarAlerta(alertaAdmin);
    btnCrearUsuario.disabled = true;

    const username = inputNuevoUsername.value.trim();
    const password = inputNuevoPassword.value;
    const rol = selectNuevoRol.value;

    try {
        const creado = await crearUsuarioApi({ username, password, rol });
        formularioCrearUsuario.reset();
        mostrarAlerta(
            alertaAdmin,
            `Usuario '${creado.username}' (${creado.rol}) creado correctamente.`,
            "exito"
        );
        await cargarTablaUsuarios();
    } catch (error) {
        if (error.status !== 401 && error.status !== 403) {
            mostrarAlerta(alertaAdmin, error.message, "error");
        }
    } finally {
        btnCrearUsuario.disabled = false;
    }
}

// --- INICIO DE SESIÓN Y ARRANQUE ---

async function manejarLogin(evento) {
    evento.preventDefault();
    ocultarAlerta(alertaLogin);
    btnIniciarSesion.disabled = true;
    btnIniciarSesion.textContent = "VERIFICANDO...";

    const username = inputLoginUsername.value.trim();
    const password = inputLoginPassword.value;

    try {
        const respuesta = await iniciarSesionApi(username, password);
        guardarToken(respuesta.access_token);
        mostrarVistaAplicacion(respuesta.usuario);
    } catch (error) {
        mostrarAlerta(alertaLogin, error.message, "error");
    } finally {
        btnIniciarSesion.disabled = false;
        btnIniciarSesion.textContent = "INICIAR SESIÓN";
    }
}

async function inicializarAplicacion() {
    registrarManejadorSesionInvalida((motivo) => {
        mostrarVistaLogin(motivo);
    });

    formularioLogin.addEventListener("submit", manejarLogin);
    btnCerrarSesion.addEventListener("click", () => cerrarSesion(""));
    btnAlternarAdmin.addEventListener("click", () => {
        if (enVistaAdmin) {
            mostrarVistaCalculadora();
        } else {
            mostrarVistaAdmin();
        }
    });
    btnVolverCalculadora.addEventListener("click", mostrarVistaCalculadora);
    btnRecargarUsuarios.addEventListener("click", cargarTablaUsuarios);
    formularioCrearUsuario.addEventListener("submit", manejarCrearUsuario);

    [selectTipoTecho, inputLargo, inputAncho, inputCaballete].forEach(
        (elemento) => {
            elemento.addEventListener("input", actualizarVistaPreviaTecho);
            elemento.addEventListener("change", actualizarVistaPreviaTecho);
        }
    );
    btnCalcular.addEventListener("click", manejarCalculo);

    // Restaurar sesión si existe token guardado
    const tokenGuardado = obtenerToken();
    if (!tokenGuardado) {
        mostrarVistaLogin("");
        return;
    }

    try {
        const usuario = await obtenerUsuarioActualApi();
        mostrarVistaAplicacion(usuario);
    } catch (_error) {
        // El manejador de 401/403 ya redirige al login con el motivo; si fue error de red:
        if (!vistaLogin.classList.contains("oculto")) {
            return;
        }
        mostrarVistaLogin(
            "No se pudo validar tu sesión actual. Inicia sesión nuevamente."
        );
    }
}

inicializarAplicacion();
