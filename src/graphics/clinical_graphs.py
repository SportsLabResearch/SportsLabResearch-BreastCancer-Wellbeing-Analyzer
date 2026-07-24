# -*- coding: utf-8 -*-
"""
Clinical Graphics Engine v3.0

Gráficos clínicos longitudinales de lectura directa:
- sin media móvil;
- registros agregados por fecha;
- media global horizontal;
- bandas clínicas;
- último valor destacado;
- resumen estadístico e interpretación automática.

SportsLabResearch-BreastCancer-Wellbeing-Analyzer
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch

from src.cleaning.clinical_cleaning import clean_clinical_data
from src.config.variable_mapping import prepare_form_dataframe
from src.core.session import get_current_participant


ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results"

# Identidad visual SportsLabResearch
COLOR_PRIMARY = "#0B2C6B"
COLOR_SECONDARY = "#3298FF"
COLOR_TEXT = "#182230"
COLOR_MUTED = "#667085"
COLOR_GRID = "#D0D5DD"
COLOR_BACKGROUND = "#FFFFFF"

COLOR_NORMAL = "#EAF6EC"
COLOR_ALERT = "#FFF4D6"
COLOR_RISK = "#FDE8E7"

COLOR_NORMAL_LINE = "#2E9E44"
COLOR_ALERT_LINE = "#B77900"
COLOR_RISK_LINE = "#D92D20"

DPI_PUBLICATION = 300
FIGSIZE_WORD = (13.2, 7.4)
FONT_FAMILY = "DejaVu Sans"


GRAPH_VARIABLES: dict[str, dict[str, Any]] = {
    "hr": {
        "title": "EVOLUCIÓN DE LA FRECUENCIA CARDÍACA",
        "short_title": "Frecuencia cardíaca",
        "ylabel": "Frecuencia cardíaca (bpm)",
        "unit": "bpm",
        "filename": "frecuencia_cardiaca.png",
        "ylim": (50, 110),
        "bands": [
            (50, 90, COLOR_NORMAL, "NORMAL", "50–89 bpm"),
            (90, 100, COLOR_ALERT, "ALERTA", "90–100 bpm"),
            (100, 110, COLOR_RISK, "RIESGO", "> 100 bpm"),
        ],
        "direction": "neutral",
        "interpretation": (
            "La frecuencia cardíaca en reposo debe interpretarse mediante su "
            "evolución longitudinal. Valores persistentemente elevados pueden "
            "relacionarse con estrés, fatiga, dolor, medicación o menor recuperación."
        ),
    },
    "rmssd": {
        "title": "EVOLUCIÓN DE RMSSD",
        "short_title": "Variabilidad cardíaca: RMSSD",
        "ylabel": "RMSSD (ms)",
        "unit": "ms",
        "filename": "rmssd.png",
        "direction": "higher",
        "interpretation": (
            "El RMSSD refleja principalmente la modulación parasimpática. "
            "Su lectura debe basarse en cambios respecto al patrón individual y "
            "en registros obtenidos bajo condiciones comparables."
        ),
    },
    "ln_rmssd": {
        "title": "EVOLUCIÓN DE LnRMSSD",
        "short_title": "Variabilidad cardíaca: LnRMSSD",
        "ylabel": "LnRMSSD [ln(ms)]",
        "unit": "ln(ms)",
        "filename": "ln_rmssd.png",
        "direction": "higher",
        "interpretation": (
            "LnRMSSD facilita el seguimiento de cambios relativos en la regulación "
            "autonómica. Una disminución mantenida respecto al nivel habitual puede "
            "sugerir menor recuperación."
        ),
    },
    "spo2": {
        "title": "EVOLUCIÓN DE LA SATURACIÓN DE OXÍGENO",
        "short_title": "Saturación periférica de oxígeno",
        "ylabel": "SpO₂ (%)",
        "unit": "%",
        "filename": "spo2.png",
        "ylim": (88, 101),
        "bands": [
            (95, 101, COLOR_NORMAL, "NORMAL", "≥ 95 %"),
            (92, 95, COLOR_ALERT, "ALERTA", "92–94 %"),
            (88, 92, COLOR_RISK, "RIESGO", "< 92 %"),
        ],
        "direction": "higher",
        "interpretation": (
            "La saturación periférica de oxígeno se interpreta mejor mediante "
            "mediciones repetidas y técnicamente válidas. Descensos persistentes "
            "o acompañados de síntomas requieren valoración sanitaria."
        ),
    },
    "sleep": {
        "title": "EVOLUCIÓN DEL SUEÑO",
        "short_title": "Calidad percibida del sueño",
        "ylabel": "Sueño (1–10)",
        "unit": "puntos",
        "filename": "sueno.png",
        "ylim": (0.5, 10.5),
        "bands": [
            (7, 10.5, COLOR_NORMAL, "FAVORABLE", "7–10"),
            (4, 7, COLOR_ALERT, "SEGUIMIENTO", "4–6"),
            (0.5, 4, COLOR_RISK, "DESFAVORABLE", "1–3"),
        ],
        "direction": "higher",
        "interpretation": (
            "Las puntuaciones más altas representan una percepción más favorable "
            "del sueño. Conviene valorar conjuntamente su evolución con fatiga, "
            "dolor y estrés."
        ),
    },
    "mood": {
        "title": "EVOLUCIÓN DEL ESTADO DE ÁNIMO",
        "short_title": "Estado de ánimo percibido",
        "ylabel": "Estado de ánimo (1–5)",
        "unit": "puntos",
        "filename": "estado_animo.png",
        "ylim": (0.5, 5.5),
        "bands": [
            (4, 5.5, COLOR_NORMAL, "FAVORABLE", "4–5"),
            (2.5, 4, COLOR_ALERT, "SEGUIMIENTO", "3"),
            (0.5, 2.5, COLOR_RISK, "DESFAVORABLE", "1–2"),
        ],
        "direction": "higher",
        "interpretation": (
            "Las puntuaciones más altas representan una percepción emocional más "
            "favorable. Una disminución mantenida o con impacto funcional debe "
            "valorarse con el equipo profesional."
        ),
    },
    "stress": {
        "title": "EVOLUCIÓN DEL ESTRÉS",
        "short_title": "Estrés percibido",
        "ylabel": "Estrés (1–10)",
        "unit": "puntos",
        "filename": "estres.png",
        "ylim": (0.5, 10.5),
        "bands": [
            (0.5, 4, COLOR_NORMAL, "FAVORABLE", "1–3"),
            (4, 7, COLOR_ALERT, "SEGUIMIENTO", "4–6"),
            (7, 10.5, COLOR_RISK, "DESFAVORABLE", "7–10"),
        ],
        "direction": "lower",
        "interpretation": (
            "Las puntuaciones más bajas representan una situación más favorable. "
            "Debe observarse la tendencia y su relación con sueño, fatiga, dolor "
            "y acontecimientos clínicos o personales."
        ),
    },
    "fatigue": {
        "title": "EVOLUCIÓN DE LA FATIGA",
        "short_title": "Fatiga percibida",
        "ylabel": "Fatiga (1–10)",
        "unit": "puntos",
        "filename": "fatiga.png",
        "ylim": (0.5, 10.5),
        "bands": [
            (0.5, 4, COLOR_NORMAL, "FAVORABLE", "1–3"),
            (4, 7, COLOR_ALERT, "SEGUIMIENTO", "4–6"),
            (7, 10.5, COLOR_RISK, "DESFAVORABLE", "7–10"),
        ],
        "direction": "lower",
        "interpretation": (
            "Las puntuaciones más bajas representan menor carga sintomática. "
            "Un aumento mantenido debe analizarse junto con sueño, dolor, estrés, "
            "tratamiento y actividad física."
        ),
    },
    "upper_pain": {
        "title": "EVOLUCIÓN DEL DOLOR SUPERIOR",
        "short_title": "Dolor en la región superior",
        "ylabel": "Dolor superior (1–10)",
        "unit": "puntos",
        "filename": "dolor_superior.png",
        "ylim": (0.5, 10.5),
        "bands": [
            (0.5, 4, COLOR_NORMAL, "FAVORABLE", "1–3"),
            (4, 7, COLOR_ALERT, "SEGUIMIENTO", "4–6"),
            (7, 10.5, COLOR_RISK, "DESFAVORABLE", "7–10"),
        ],
        "direction": "lower",
        "interpretation": (
            "Las puntuaciones más bajas representan menor dolor percibido. "
            "El dolor nuevo, intenso, persistente o diferente del patrón habitual "
            "requiere valoración clínica."
        ),
    },
    "lower_pain": {
        "title": "EVOLUCIÓN DEL DOLOR INFERIOR",
        "short_title": "Dolor en la región inferior",
        "ylabel": "Dolor inferior (1–10)",
        "unit": "puntos",
        "filename": "dolor_inferior.png",
        "ylim": (0.5, 10.5),
        "bands": [
            (0.5, 4, COLOR_NORMAL, "FAVORABLE", "1–3"),
            (4, 7, COLOR_ALERT, "SEGUIMIENTO", "4–6"),
            (7, 10.5, COLOR_RISK, "DESFAVORABLE", "7–10"),
        ],
        "direction": "lower",
        "interpretation": (
            "Las puntuaciones más bajas representan menor dolor percibido. "
            "La tendencia debe relacionarse con actividad, tratamiento, movilidad "
            "e impacto funcional."
        ),
    },
}


def configure_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.family": FONT_FAMILY,
            "font.size": 9.5,
            "axes.labelcolor": COLOR_TEXT,
            "axes.edgecolor": COLOR_GRID,
            "xtick.color": COLOR_MUTED,
            "ytick.color": COLOR_MUTED,
            "figure.facecolor": COLOR_BACKGROUND,
            "axes.facecolor": COLOR_BACKGROUND,
            "savefig.facecolor": COLOR_BACKGROUND,
        }
    )


def safe_filename(value: object) -> str:
    text = str(value or "").strip()
    for old, new in {
        " ": "_", "/": "-", "\\": "-", ":": "-", "*": "",
        "?": "", '"': "", "<": "", ">": "", "|": "",
    }.items():
        text = text.replace(old, new)
    return text or "participante"


def prepare_graph_data(records: pd.DataFrame) -> pd.DataFrame:
    clinical_data = prepare_form_dataframe(records.copy())
    clinical_data = clean_clinical_data(clinical_data)

    if "date" not in clinical_data.columns:
        raise KeyError("No existe la columna date para generar gráficos.")

    clinical_data["date"] = pd.to_datetime(
        clinical_data["date"], errors="coerce", dayfirst=True
    )
    clinical_data = clinical_data[clinical_data["date"].notna()].copy()
    clinical_data.sort_values("date", inplace=True)
    return clinical_data


def get_figures_folder(
    participant: dict[str, Any],
    output_dir: Path | str | None = None,
) -> Path:
    if output_dir is not None:
        folder = Path(output_dir)
    else:
        folder = (
            RESULTS_DIR
            / safe_filename(participant.get("site"))
            / (
                safe_filename(participant.get("participant_id"))
                + "_"
                + safe_filename(participant.get("name"))
            )
            / "figures"
        )
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def aggregate_by_date(
    clinical_data: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:
    """Evita líneas verticales cuando existen varios registros el mismo día."""
    available = [column for column in columns if column in clinical_data.columns]
    if not available:
        return pd.DataFrame()

    data = clinical_data[["date"] + available].copy()
    for column in available:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = (
        data.groupby("date", as_index=False)[available]
        .mean(numeric_only=True)
        .sort_values("date")
    )
    return data


def classify_value(
    value: float,
    configuration: dict[str, Any],
) -> tuple[str, str]:
    for lower, upper, _, label, _ in configuration.get("bands", []):
        if lower <= value < upper or (
            value == upper and upper == configuration.get("ylim", (None, None))[1]
        ):
            if label in {"NORMAL", "FAVORABLE"}:
                return label, COLOR_NORMAL_LINE
            if label in {"ALERTA", "SEGUIMIENTO"}:
                return label, COLOR_ALERT_LINE
            return label, COLOR_RISK_LINE
    return "ESTABLE", COLOR_NORMAL_LINE


def trend_text(
    values: pd.Series,
    direction: str,
) -> tuple[str, str]:
    if len(values) < 2:
        return "SIN TENDENCIA", COLOR_MUTED

    first = float(values.iloc[0])
    last = float(values.iloc[-1])
    scale = max(abs(first), abs(float(values.mean())), 1.0)
    relative_change = (last - first) / scale

    if abs(relative_change) < 0.05:
        return "ESTABLE", COLOR_NORMAL_LINE

    improving = (
        (direction == "higher" and relative_change > 0)
        or (direction == "lower" and relative_change < 0)
    )

    if direction == "neutral":
        return ("AUMENTO" if relative_change > 0 else "DESCENSO"), COLOR_ALERT_LINE

    return (
        ("MEJORA", COLOR_NORMAL_LINE)
        if improving
        else ("EMPEORA", COLOR_ALERT_LINE)
    )


def format_date_axis(axis: plt.Axes) -> None:
    locator = mdates.AutoDateLocator(minticks=5, maxticks=9)
    formatter = mdates.ConciseDateFormatter(locator)
    axis.xaxis.set_major_locator(locator)
    axis.xaxis.set_major_formatter(formatter)


def draw_header(figure: plt.Figure, title: str) -> None:
    figure.text(
        0.045, 0.958, "SportsLab", fontsize=20, color=COLOR_PRIMARY,
        fontweight="bold", va="top",
    )
    figure.text(
        0.142, 0.958, "Research", fontsize=20, color=COLOR_SECONDARY,
        fontweight="bold", va="top",
    )
    figure.text(
        0.045, 0.918, "Science. Health. Performance.",
        fontsize=9.5, color=COLOR_PRIMARY,
    )
    figure.text(
        0.965, 0.958, title, fontsize=17, color=COLOR_PRIMARY,
        fontweight="bold", ha="right", va="top",
    )
    figure.text(
        0.965, 0.918, "Seguimiento longitudinal",
        fontsize=10.5, color=COLOR_MUTED, ha="right",
    )
    figure.add_artist(
        plt.Line2D(
            [0.04, 0.97], [0.895, 0.895],
            transform=figure.transFigure,
            color=COLOR_PRIMARY, linewidth=0.8,
        )
    )


def draw_footer(figure: plt.Figure) -> None:
    figure.add_artist(
        plt.Line2D(
            [0.04, 0.97], [0.035, 0.035],
            transform=figure.transFigure,
            color=COLOR_GRID, linewidth=0.8,
        )
    )
    figure.text(
        0.045, 0.012,
        "SportsLabResearch | Breast Cancer Wellbeing Analyzer",
        fontsize=8, color=COLOR_PRIMARY,
    )
    figure.text(
        0.965, 0.012,
        pd.Timestamp.today().strftime("Generado el %d/%m/%Y"),
        fontsize=8, color=COLOR_PRIMARY, ha="right",
    )


def draw_reference_bands(
    axis: plt.Axes,
    configuration: dict[str, Any],
) -> None:
    for lower, upper, color, label, range_text in configuration.get("bands", []):
        axis.axhspan(lower, upper, facecolor=color, alpha=0.82, zorder=0)
        axis.text(
            0.975,
            (lower + upper) / 2,
            f"{label}\n{range_text}",
            transform=axis.get_yaxis_transform(),
            ha="right",
            va="center",
            fontsize=8.5,
            color=(
                COLOR_NORMAL_LINE
                if label in {"NORMAL", "FAVORABLE"}
                else COLOR_ALERT_LINE
                if label in {"ALERTA", "SEGUIMIENTO"}
                else COLOR_RISK_LINE
            ),
            fontweight="bold",
        )


def draw_stats_panel(
    axis: plt.Axes,
    values: pd.Series,
    dates: pd.Series,
    unit: str,
    configuration: dict[str, Any],
) -> None:
    axis.set_axis_off()
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)

    mean = float(values.mean())
    last = float(values.iloc[-1])
    first = float(values.iloc[0])
    change = ((last - first) / first * 100) if first != 0 else 0.0
    sd = float(values.std(ddof=1)) if len(values) > 1 else 0.0
    clinical_status, status_color = classify_value(last, configuration)
    trend_status, trend_color = trend_text(values, configuration.get("direction", "neutral"))

    container = FancyBboxPatch(
        (0.01, 0.01), 0.98, 0.98,
        boxstyle="round,pad=0.012,rounding_size=0.025",
        facecolor="white", edgecolor=COLOR_GRID, linewidth=1.0,
    )
    axis.add_patch(container)

    cards = [
        ("Media global", f"{mean:.1f} {unit}", COLOR_PRIMARY),
        ("Último valor", f"{last:.1f} {unit}", COLOR_PRIMARY),
        ("Variación vs. primera", f"{change:+.1f} %", trend_color),
        ("Registros", str(len(values)), COLOR_PRIMARY),
        ("Desviación estándar", f"{sd:.1f} {unit}", COLOR_PRIMARY),
    ]

    y = 0.94
    for title, value, value_color in cards:
        axis.text(0.12, y, title, fontsize=8.5, color=COLOR_PRIMARY, va="top")
        axis.text(
            0.12, y - 0.052, value, fontsize=13, color=value_color,
            fontweight="bold", va="top",
        )
        axis.plot([0.04, 0.96], [y - 0.105, y - 0.105], color=COLOR_GRID, lw=0.7)
        y -= 0.145

    axis.text(0.12, 0.20, "Estado clínico", fontsize=8.5, color=COLOR_PRIMARY)
    axis.text(
        0.12, 0.145, clinical_status, fontsize=14,
        color=status_color, fontweight="bold",
    )
    axis.text(0.12, 0.085, f"Tendencia: {trend_status}", fontsize=8.5, color=trend_color)
    axis.text(
        0.12, 0.035,
        pd.Timestamp(dates.iloc[-1]).strftime("%d/%m/%Y"),
        fontsize=7.5, color=COLOR_MUTED,
    )


def draw_interpretation_box(
    axis: plt.Axes,
    values: pd.Series,
    configuration: dict[str, Any],
) -> None:
    axis.set_axis_off()
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)

    trend_status, trend_color = trend_text(
        values, configuration.get("direction", "neutral")
    )

    box = FancyBboxPatch(
        (0.005, 0.05), 0.99, 0.90,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        facecolor="#F7FBF7", edgecolor="#A8D5AE", linewidth=0.9,
    )
    axis.add_patch(box)
    axis.text(
        0.03, 0.72, "Interpretación", fontsize=9.5,
        color=COLOR_PRIMARY, fontweight="bold",
    )
    axis.text(
        0.03, 0.46,
        configuration["interpretation"],
        fontsize=8.4, color=COLOR_TEXT, va="center", wrap=True,
    )
    axis.text(
        0.97, 0.72, trend_status, fontsize=9.5,
        color=trend_color, fontweight="bold", ha="right",
    )


def style_main_axis(
    axis: plt.Axes,
    configuration: dict[str, Any],
) -> None:
    axis.set_title(
        configuration["short_title"],
        loc="left", pad=10, color=COLOR_TEXT, fontsize=12,
    )
    axis.set_xlabel("Fecha", labelpad=6)
    axis.set_ylabel(configuration["ylabel"], labelpad=8)
    axis.grid(color=COLOR_GRID, linewidth=0.65, alpha=0.55)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_color(COLOR_GRID)
    axis.spines["bottom"].set_color(COLOR_GRID)
    axis.margins(x=0.03)
    format_date_axis(axis)


def save_publication_formats(
    figure: plt.Figure,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=DPI_PUBLICATION, bbox_inches="tight", pad_inches=0.08)
    figure.savefig(output_path.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.08)
    figure.savefig(output_path.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.08)


def create_single_variable_graph(
    clinical_data: pd.DataFrame,
    column: str,
    configuration: dict[str, Any],
    output_path: Path,
) -> Path | None:
    graph_data = aggregate_by_date(clinical_data, [column])
    if graph_data.empty or column not in graph_data.columns:
        return None

    graph_data.dropna(subset=[column], inplace=True)
    if graph_data.empty:
        return None

    values = graph_data[column]
    dates = graph_data["date"]

    figure = plt.figure(figsize=FIGSIZE_WORD)
    grid = GridSpec(
        2, 2, figure=figure,
        width_ratios=[4.9, 1.25],
        height_ratios=[4.2, 0.85],
        left=0.055, right=0.97, top=0.85, bottom=0.08,
        hspace=0.18, wspace=0.10,
    )
    axis = figure.add_subplot(grid[0, 0])
    stats_axis = figure.add_subplot(grid[0, 1])
    interpretation_axis = figure.add_subplot(grid[1, :])

    draw_header(figure, configuration["title"])
    draw_reference_bands(axis, configuration)

    axis.plot(
        dates, values,
        color="#111111", linewidth=1.7,
        marker="o", markersize=6,
        markerfacecolor="white", markeredgecolor="#111111",
        zorder=4, label="Registro",
    )

    mean = float(values.mean())
    axis.axhline(
        mean, color=COLOR_MUTED, linewidth=1.1,
        linestyle=(0, (6, 4)), zorder=2, label="Media global",
    )
    axis.text(
        0.98, mean,
        f"Media: {mean:.1f} {configuration['unit']}",
        transform=axis.get_yaxis_transform(),
        ha="right", va="bottom", fontsize=8.2, color=COLOR_MUTED,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8},
    )

    last_date = dates.iloc[-1]
    last_value = float(values.iloc[-1])
    axis.scatter(
        [last_date], [last_value], s=210,
        facecolor="none", edgecolor="#111111", linewidth=1.2, zorder=3,
    )

    if "ylim" in configuration:
        axis.set_ylim(configuration["ylim"])

    style_main_axis(axis, configuration)
    axis.legend(loc="lower center", bbox_to_anchor=(0.5, -0.23), ncol=2, frameon=False)

    draw_stats_panel(
        stats_axis, values, dates, configuration["unit"], configuration
    )
    draw_interpretation_box(interpretation_axis, values, configuration)
    draw_footer(figure)

    save_publication_formats(figure, output_path)
    plt.close(figure)
    return output_path


def create_blood_pressure_graph(
    clinical_data: pd.DataFrame,
    output_path: Path,
) -> Path | None:
    graph_data = aggregate_by_date(clinical_data, ["sbp", "dbp"])
    if graph_data.empty:
        return None

    available = [
        column for column in ("sbp", "dbp")
        if column in graph_data.columns and graph_data[column].notna().any()
    ]
    if not available:
        return None

    figure, axis = plt.subplots(figsize=FIGSIZE_WORD)
    draw_header(figure, "EVOLUCIÓN DE LA PRESIÓN ARTERIAL")

    axis.axhspan(90, 120, facecolor=COLOR_NORMAL, alpha=0.82, zorder=0)
    axis.axhspan(120, 140, facecolor=COLOR_ALERT, alpha=0.82, zorder=0)
    axis.axhspan(140, 180, facecolor=COLOR_RISK, alpha=0.82, zorder=0)

    styles = {
        "sbp": ("PAS", COLOR_PRIMARY, "o"),
        "dbp": ("PAD", "#19A7A0", "s"),
    }

    for column in available:
        data = graph_data.dropna(subset=[column])
        label, color, marker = styles[column]

        axis.plot(
            data["date"], data[column],
            color=color, linewidth=1.5, marker=marker,
            markersize=5, markerfacecolor="white",
            markeredgecolor=color, label=label, zorder=4,
        )

        mean = float(data[column].mean())
        axis.axhline(
            mean, color=color, linewidth=1.0,
            linestyle=(0, (5, 4)), alpha=0.75,
            label=f"Media {label}", zorder=2,
        )

    axis.set_title("Presión arterial", loc="left", pad=10, color=COLOR_TEXT, fontsize=12)
    axis.set_xlabel("Fecha")
    axis.set_ylabel("Presión arterial (mmHg)")
    axis.set_ylim(60, 180)
    axis.grid(color=COLOR_GRID, linewidth=0.65, alpha=0.55)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_color(COLOR_GRID)
    axis.spines["bottom"].set_color(COLOR_GRID)
    format_date_axis(axis)
    axis.legend(loc="upper right", frameon=False, ncol=2)

    figure.text(
        0.06, 0.08,
        "Las líneas continuas muestran los registros medios por fecha y las "
        "líneas discontinuas representan la media global de PAS y PAD.",
        fontsize=8.5, color=COLOR_TEXT,
    )
    draw_footer(figure)
    figure.subplots_adjust(left=0.07, right=0.97, top=0.84, bottom=0.17)

    save_publication_formats(figure, output_path)
    plt.close(figure)
    return output_path


def generate_clinical_graphs(
    records: pd.DataFrame,
    output_dir: Path | str | None = None,
) -> list[Path]:
    if records is None or records.empty:
        raise ValueError("No hay registros disponibles para generar gráficos.")

    configure_matplotlib()

    participant = get_current_participant() or {
        "participant_id": "sin_id",
        "name": "Participante",
        "site": "No disponible",
    }

    clinical_data = prepare_graph_data(records)
    if clinical_data.empty:
        raise ValueError("No hay registros con fechas válidas.")

    figures_folder = get_figures_folder(participant, output_dir)
    generated_files: list[Path] = []

    pressure_result = create_blood_pressure_graph(
        clinical_data,
        figures_folder / "presion_arterial.png",
    )
    if pressure_result is not None:
        generated_files.append(pressure_result)

    for column, configuration in GRAPH_VARIABLES.items():
        result = create_single_variable_graph(
            clinical_data,
            column,
            configuration,
            figures_folder / configuration["filename"],
        )
        if result is not None:
            generated_files.append(result)

    return generated_files
