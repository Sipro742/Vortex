/**
 * Visualizador 2D en planta del techo en HTML5 Canvas.
 * Solo dibuja la geometría proporcional; no realiza cálculos estructurales.
 */

export function dibujarPlantaTecho(canvas, { tipo, largo, ancho, caballete }) {
    if (!canvas) {
        return;
    }

    const ctx = canvas.getContext("2d");
    const anchoCanvas = canvas.width;
    const altoCanvas = canvas.height;

    ctx.clearRect(0, 0, anchoCanvas, altoCanvas);

    // Protección contra valores no válidos o menores o iguales a cero
    if (
        !Number.isFinite(largo) ||
        !Number.isFinite(ancho) ||
        largo <= 0 ||
        ancho <= 0
    ) {
        ctx.fillStyle = "#5f6368";
        ctx.font = "14px sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(
            "Ingresa largo y ancho mayores a 0 para ver la vista 2D",
            anchoCanvas / 2,
            altoCanvas / 2
        );
        return;
    }

    const margenX = 40;
    const margenY = 25;
    const escala = Math.min(
        (anchoCanvas - margenX * 2) / largo,
        (altoCanvas - margenY * 2) / ancho
    );

    const w = largo * escala;
    const h = ancho * escala;
    const x = (anchoCanvas - w) / 2;
    const y = (altoCanvas - h) / 2;

    ctx.strokeStyle = "#0044cc";
    ctx.lineWidth = 2;
    ctx.strokeRect(x, y, w, h);

    ctx.beginPath();
    if (tipo === "piramide") {
        const centroX = x + w / 2;
        const centroY = y + h / 2;
        ctx.moveTo(x, y);
        ctx.lineTo(centroX, centroY);
        ctx.moveTo(x + w, y);
        ctx.lineTo(centroX, centroY);
        ctx.moveTo(x, y + h);
        ctx.lineTo(centroX, centroY);
        ctx.moveTo(x + w, y + h);
        ctx.lineTo(centroX, centroY);
    } else {
        const cabSeguro =
            Number.isFinite(caballete) && caballete > 0
                ? Math.min(caballete, largo * 0.95)
                : 0;
        const anchoCab = cabSeguro * escala;
        const xIzqCab = x + (w - anchoCab) / 2;
        const xDerCab = x + (w + anchoCab) / 2;
        const centroY = y + h / 2;

        // Línea de caballete
        ctx.moveTo(xIzqCab, centroY);
        ctx.lineTo(xDerCab, centroY);

        // Limatesas hacia las cuatro esquinas
        ctx.moveTo(x, y);
        ctx.lineTo(xIzqCab, centroY);
        ctx.moveTo(x, y + h);
        ctx.lineTo(xIzqCab, centroY);
        ctx.moveTo(x + w, y);
        ctx.lineTo(xDerCab, centroY);
        ctx.moveTo(x + w, y + h);
        ctx.lineTo(xDerCab, centroY);
    }
    ctx.stroke();
}
