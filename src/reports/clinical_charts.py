# -*- coding: utf-8 -*-
"""
SportsLabResearch - BreastCancer Wellbeing Analyzer
Gráfico clínico longitudinal de frecuencia cardiaca.

Ejecución:
    py .\clinical_heart_rate_chart.py
    py .\clinical_heart_rate_chart.py --input .\datos_fc.xlsx
    py .\clinical_heart_rate_chart.py --input .\datos_fc.csv --output .\resultados\fc_clinica.png

Columnas esperadas:
    Fecha
    FC
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
from scipy.interpolate import make_interp_spline


COLOR_AZUL = "#0B2C6B"
COLOR_AZUL_CLARO = "#3298FF"
COLOR_VERDE = "#2E9E44"
COLOR_AMARILLO = "#F4B400"
COLOR_ROJO = "#E53935"
COLOR_GRIS = "#666666"
COLOR_BORDE = "#D5DAE3"

plt.rcParams["font.family"] = "DejaVu Sans"


def cargar_datos(ruta: Path | None) -> pd.DataFrame:
    if ruta is None:
        return pd.DataFrame(
            {
                "Fecha": [
                    "2025-02-01",
                    "2025-02-15",
                    "2025-03-01",
                    "2025-03-15",
                    "2025-04-01",
                    "2025-04-15",
                    "2025-05-01",
                    "2025-05-15",
                ],
                "FC": [78, 85, 79, 86, 78, 82, 75, 78],
            }
        )

    if not ruta.exists():
        raise FileNotFoundError(f"No existe el archivo: {ruta}")

    extension = ruta.suffix.lower()

    if extension == ".csv":
        df = pd.read_csv(ruta)
    elif extension in {".xlsx", ".xls"}:
        df = pd.read_excel(ruta)
    else:
        raise ValueError("Formato no admitido. Use CSV, XLSX o XLS.")

    columnas = {str(c).strip().lower(): c for c in df.columns}

    if "fecha" not in columnas:
        raise ValueError("Falta la columna obligatoria: Fecha")

    posibles_fc = ["fc", "frecuencia cardiaca", "frecuencia cardíaca", "heart rate"]

    columna_fc = None
    for nombre in posibles_fc:
        if nombre in columnas:
            columna_fc = columnas[nombre]
            break

    if columna_fc is None:
        raise ValueError(
            "Falta la columna de frecuencia cardiaca. "
            "Use una de estas columnas: FC, Frecuencia cardiaca o Heart Rate."
        )

    resultado = pd.DataFrame(
        {
            "Fecha": pd.to_datetime(df[columnas["fecha"]], errors="coerce"),
            "FC": pd.to_numeric(df[columna_fc], errors="coerce"),
        }
    )

    resultado = resultado.dropna(subset=["Fecha", "FC"]).sort_values("Fecha")

    if resultado.empty:
        raise ValueError("No hay registros válidos para generar el gráfico.")

    return resultado.reset_index(drop=True)


def estado_clinico(valor: float) -> tuple[str, str]:
    if valor > 100:
        return "RIESGO", COLOR_ROJO
    if valor >= 90:
        return "ALERTA", COLOR_AMARILLO
    return "ESTABLE", COLOR_VERDE


def dibujar_tarjeta(
    ax,
    y: float,
    titulo: str,
    valor: str,
    subtitulo: str | None = None,
    color_valor: str = COLOR_AZUL,
) -> None:
    caja = FancyBboxPatch(
        (0.03, y - 0.115),
        0.94,
        0.11,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        facecolor="white",
        edgecolor=COLOR_BORDE,
        linewidth=1,
    )
    ax.add_patch(caja)

    icono = Circle(
        (0.16, y - 0.058),
        0.055,
        facecolor=COLOR_AZUL,
        edgecolor=COLOR_AZUL,
    )
    ax.add_patch(icono)

    ax.text(
        0.16,
        y - 0.058,
        "●",
        ha="center",
        va="center",
        fontsize=17,
        color="white",
        fontweight="bold",
    )

    ax.text(
        0.31,
        y - 0.038,
        titulo,
        fontsize=12,
        color=COLOR_AZUL,
        va="center",
    )

    ax.text(
        0.31,
        y - 0.080,
        valor,
        fontsize=18,
        color=color_valor,
        fontweight="bold",
        va="center",
    )

    if subtitulo:
        ax.text(
            0.31,
            y - 0.105,
            subtitulo,
            fontsize=9,
            color=COLOR_AZUL,
            va="center",
        )


def crear_figura_fc(
    df: pd.DataFrame,
    salida: Path,
    nombre_proyecto: str = "Breast Cancer Wellbeing Analyzer",
) -> None:
    fechas = pd.to_datetime(df["Fecha"])
    fc = pd.to_numeric(df["FC"])

    media = float(fc.mean())
    ultimo = float(fc.iloc[-1])
    primero = float(fc.iloc[0])
    cambio = ((ultimo - primero) / primero * 100) if primero != 0 else 0.0
    sd = float(fc.std(ddof=1)) if len(fc) > 1 else 0.0
    estado, color_estado = estado_clinico(ultimo)

    fig = plt.figure(figsize=(16, 10), facecolor="white")

    ax = fig.add_axes([0.05, 0.28, 0.68, 0.52])
    panel = fig.add_axes([0.76, 0.22, 0.21, 0.64])
    tabla = fig.add_axes([0.04, 0.07, 0.46, 0.13])
    texto = fig.add_axes([0.52, 0.07, 0.45, 0.13])

    fig.text(
        0.07,
        0.93,
        "SportsLab",
        fontsize=28,
        color=COLOR_AZUL,
        fontweight="bold",
    )
    fig.text(
        0.195,
        0.93,
        "Research",
        fontsize=28,
        color=COLOR_AZUL_CLARO,
        fontweight="bold",
    )
    fig.text(
        0.07,
        0.90,
        "Science. Health. Performance.",
        fontsize=14,
        color=COLOR_AZUL,
    )

    fig.text(
        0.55,
        0.93,
        "EVOLUCIÓN DE LA FRECUENCIA CARDÍACA",
        fontsize=24,
        color=COLOR_AZUL,
        fontweight="bold",
    )
    fig.text(
        0.79,
        0.89,
        "Seguimiento longitudinal",
        fontsize=16,
        color=COLOR_GRIS,
    )

    fig.lines.append(
        plt.Line2D(
            [0.05, 0.97],
            [0.875, 0.875],
            transform=fig.transFigure,
            color=COLOR_AZUL,
            linewidth=0.8,
        )
    )

    ax.set_ylim(50, 110)
    ax.axhspan(100, 110, color="#FDE7E7", zorder=0)
    ax.axhspan(90, 100, color="#FFF5D9", zorder=0)
    ax.axhspan(50, 90, color="#F4FAF5", zorder=0)

    x = np.arange(len(fc))

    if len(fc) >= 4:
        xs = np.linspace(x.min(), x.max(), 300)
        ys = make_interp_spline(x, fc, k=3)(xs)
        ax.plot(xs, ys, color="black", linewidth=2.2, zorder=3)
    else:
        ax.plot(x, fc, color="black", linewidth=2.2, zorder=3)

    ax.scatter(
        x,
        fc,
        s=150,
        facecolor="white",
        edgecolor="black",
        linewidth=1.4,
        zorder=4,
    )

    ax.scatter(
        [x[-1]],
        [ultimo],
        s=650,
        facecolor="none",
        edgecolor="black",
        linewidth=1.3,
        zorder=2,
    )

    ax.axhline(
        media,
        linestyle=(0, (6, 4)),
        color="#6F6F7B",
        linewidth=1.2,
    )

    ax.text(
        len(fc) - 0.65,
        media + 0.6,
        f"Media: {media:.0f} bpm",
        ha="right",
        color="#6F6F7B",
        fontsize=11,
    )

    xmax_texto = max(len(fc) - 0.65, 0.3)

    ax.text(
        xmax_texto,
        104.5,
        "RIESGO\n> 100 bpm",
        ha="right",
        va="center",
        fontsize=11,
        color=COLOR_ROJO,
        fontweight="bold",
    )
    ax.text(
        xmax_texto,
        94.5,
        "ALERTA\n90–100 bpm",
        ha="right",
        va="center",
        fontsize=11,
        color="#B57C00",
        fontweight="bold",
    )
    ax.text(
        xmax_texto,
        64,
        "NORMAL\n50–89 bpm",
        ha="right",
        va="center",
        fontsize=11,
        color=COLOR_VERDE,
        fontweight="bold",
    )

    etiquetas = fechas.dt.strftime("%d %b")
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas, fontsize=10)
    ax.set_xlabel("Fecha", fontsize=11)
    ax.text(
        0.01,
        1.02,
        "Frecuencia cardiaca (bpm)",
        transform=ax.transAxes,
        fontsize=12,
        color="black",
    )

    ax.grid(alpha=0.14)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#999999")
    ax.spines["bottom"].set_color("#999999")

    fig.text(
        0.05,
        0.245,
        "Los valores mostrados son medias de cada registro.",
        fontsize=9,
        color="black",
        style="italic",
    )

    panel.axis("off")
    panel.set_xlim(0, 1)
    panel.set_ylim(0, 1)

    contenedor = FancyBboxPatch(
        (0.0, 0.0),
        1.0,
        1.0,
        boxstyle="round,pad=0.012,rounding_size=0.025",
        facecolor="white",
        edgecolor=COLOR_BORDE,
        linewidth=1.0,
    )
    panel.add_patch(contenedor)

    dibujar_tarjeta(panel, 0.97, "Media", f"{media:.0f} bpm")
    dibujar_tarjeta(
        panel,
        0.80,
        "Último valor",
        f"{ultimo:.0f} bpm",
        fechas.iloc[-1].strftime("(%d %b %Y)"),
    )
    dibujar_tarjeta(panel, 0.63, "Variación vs. primera", f"{cambio:+.0f} %")
    dibujar_tarjeta(panel, 0.46, "Registros", str(len(fc)))
    dibujar_tarjeta(panel, 0.29, "Desviación estándar", f"{sd:.1f} bpm")

    panel.text(
        0.31,
        0.12,
        "Estado clínico",
        fontsize=11,
        color=COLOR_AZUL,
    )
    panel.text(
        0.31,
        0.055,
        estado,
        fontsize=20,
        color=color_estado,
        fontweight="bold",
    )

    tabla.axis("off")
    tabla.set_xlim(0, 1)
    tabla.set_ylim(0, 1)

    caja_tabla = FancyBboxPatch(
        (0, 0),
        1,
        1,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        facecolor="white",
        edgecolor=COLOR_BORDE,
    )
    tabla.add_patch(caja_tabla)

    tabla.text(
        0.11,
        0.84,
        "Rangos clínicos (bpm)",
        fontsize=10,
        color=COLOR_AZUL,
        fontweight="bold",
    )
    tabla.text(
        0.43,
        0.84,
        "Interpretación",
        fontsize=10,
        color=COLOR_AZUL,
        fontweight="bold",
    )

    filas = [
        (0.62, COLOR_VERDE, "50 – 89", "Normal: rango esperado en reposo."),
        (0.37, COLOR_AMARILLO, "90 – 100", "Alerta: valores elevados, monitorizar tendencia."),
        (0.12, COLOR_ROJO, "> 100", "Riesgo: valores elevados, valorar intervención."),
    ]

    for y, color, rango, interpretacion in filas:
        tabla.add_patch(Circle((0.05, y), 0.018, color=color))
        tabla.text(0.11, y, rango, fontsize=9, va="center")
        tabla.text(0.43, y, interpretacion, fontsize=8.7, va="center")

    texto.axis("off")
    texto.set_xlim(0, 1)
    texto.set_ylim(0, 1)

    caja_texto = FancyBboxPatch(
        (0, 0),
        1,
        1,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        facecolor="white",
        edgecolor=COLOR_BORDE,
    )
    texto.add_patch(caja_texto)

    texto.add_patch(
        Circle(
            (0.07, 0.5),
            0.035,
            facecolor="white",
            edgecolor="#17609A",
            linewidth=2,
        )
    )
    texto.text(
        0.07,
        0.5,
        "i",
        ha="center",
        va="center",
        fontsize=14,
        color="#17609A",
        fontweight="bold",
    )
    texto.text(
        0.14,
        0.66,
        "La frecuencia cardiaca en reposo refleja el equilibrio del sistema",
        fontsize=9.3,
        color=COLOR_AZUL,
    )
    texto.text(
        0.14,
        0.47,
        "cardiovascular y autonómico. Valores sostenidamente elevados pueden",
        fontsize=9.3,
        color=COLOR_AZUL,
    )
    texto.text(
        0.14,
        0.28,
        "estar asociados a estrés, fatiga, falta de recuperación o evolución clínica.",
        fontsize=9.3,
        color=COLOR_AZUL,
    )

    fig.lines.append(
        plt.Line2D(
            [0.05, 0.97],
            [0.055, 0.055],
            transform=fig.transFigure,
            color=COLOR_BORDE,
            linewidth=0.8,
        )
    )

    fig.text(
        0.07,
        0.022,
        f"SportsLabResearch | {nombre_proyecto}",
        fontsize=9.5,
        color=COLOR_AZUL,
    )
    fig.text(
        0.85,
        0.022,
        pd.Timestamp.today().strftime("Generado el %d/%m/%Y"),
        fontsize=9.5,
        color=COLOR_AZUL,
    )

    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera un gráfico clínico longitudinal de frecuencia cardiaca."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Archivo CSV, XLSX o XLS con columnas Fecha y FC.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/frecuencia_cardiaca_clinica.png"),
        help="Ruta de salida del gráfico PNG.",
    )
    args = parser.parse_args()

    df = cargar_datos(args.input)
    crear_figura_fc(df, args.output)

    print("")
    print("Gráfico generado correctamente:")
    print(args.output.resolve())
    print("")


if __name__ == "__main__":
    main()
