# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Coordinador del análisis por momento de registro.

Modos:
    PRE
    POST
    PRE_POST

Este módulo:
    - prepara las variables clínicas;
    - ejecuta el análisis correspondiente;
    - presenta los resultados;
    - mantiene la estadística dentro de pre_post.py.
"""

from __future__ import annotations

import pandas as pd

from src.analysis.pre_post import (
    MODE_POST,
    MODE_PRE,
    MODE_PRE_POST,
    analyse_by_mode,
)


MOMENT_VARIABLES = {
    "sleep": {
        "label": "Sueño",
        "direction": 1,
        "mcid": 1.0,
    },
    "mood": {
        "label": "Estado de ánimo",
        "direction": 1,
        "mcid": 1.0,
    },
    "energy": {
        "label": "Energía",
        "direction": 1,
        "mcid": 1.0,
    },
    "stress": {
        "label": "Estrés",
        "direction": -1,
        "mcid": 1.0,
    },
    "fatigue": {
        "label": "Fatiga",
        "direction": -1,
        "mcid": 1.0,
    },
    "upper_pain": {
        "label": "Dolor superior",
        "direction": -1,
        "mcid": 1.0,
    },
    "lower_pain": {
        "label": "Dolor inferior",
        "direction": -1,
        "mcid": 1.0,
    },
    "hr": {
        "label": "Frecuencia cardiaca",
        "direction": -1,
        "mcid": 5.0,
    },
    "rmssd": {
        "label": "RMSSD",
        "direction": 1,
        "mcid": 5.0,
    },
    "ln_rmssd": {
        "label": "LnRMSSD",
        "direction": 1,
        "mcid": 0.20,
    },
    "sbp": {
        "label": "Presión arterial sistólica",
        "direction": -1,
        "mcid": 5.0,
    },
    "dbp": {
        "label": "Presión arterial diastólica",
        "direction": -1,
        "mcid": 5.0,
    },
    "spo2": {
        "label": "Saturación de oxígeno",
        "direction": 1,
        "mcid": 1.0,
    },
}


def available_variables(
    dataframe: pd.DataFrame,
) -> dict:
    """
    Devuelve únicamente las variables disponibles en los datos.
    """

    result = {}

    for variable, config in MOMENT_VARIABLES.items():

        if variable not in dataframe.columns:
            continue

        values = pd.to_numeric(
            dataframe[variable],
            errors="coerce",
        )

        if values.notna().sum() == 0:
            continue

        result[variable] = {
            "direction": config["direction"],
            "mcid": config["mcid"],
        }

    return result


def add_variable_labels(
    results: pd.DataFrame,
) -> pd.DataFrame:
    """
    Añade el nombre clínico de cada variable.
    """

    if results.empty or "variable" not in results.columns:
        return results

    output = results.copy()

    labels = {
        variable: config["label"]
        for variable, config in MOMENT_VARIABLES.items()
    }

    output.insert(
        1,
        "variable_label",
        output["variable"].map(labels).fillna(
            output["variable"]
        ),
    )

    return output


def run_moment_analysis(
    dataframe: pd.DataFrame,
    mode: str,
) -> pd.DataFrame:
    """
    Ejecuta el análisis solicitado.

    Parameters
    ----------
    dataframe:
        Datos clínicos preparados.

    mode:
        PRE, POST o PRE_POST.
    """

    if dataframe is None or dataframe.empty:
        return pd.DataFrame()

    variables = available_variables(dataframe)

    if not variables:
        return pd.DataFrame()

    results = analyse_by_mode(
        dataframe=dataframe,
        variables=variables,
        mode=mode,
        moment_column="moment",
    )

    return add_variable_labels(results)


def format_number(
    value: object,
    decimals: int = 2,
) -> str:
    """
    Formatea valores numéricos de forma segura.
    """

    try:
        if pd.isna(value):
            return "-"
    except TypeError:
        pass

    try:
        return f"{float(value):.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)


def print_single_moment_results(
    results: pd.DataFrame,
    title: str,
) -> None:
    """
    Imprime resultados descriptivos PRE o POST.
    """

    print()
    print("=" * 92)
    print(title)
    print("=" * 92)

    if results.empty:
        print("No hay datos disponibles para este momento.")
        return

    columns = [
        "variable_label",
        "n",
        "mean",
        "median",
        "sd",
        "minimum",
        "maximum",
    ]

    available = [
        column
        for column in columns
        if column in results.columns
    ]

    output = results[available].copy()

    rename = {
        "variable_label": "Variable",
        "n": "n",
        "mean": "Media",
        "median": "Mediana",
        "sd": "DE",
        "minimum": "Mínimo",
        "maximum": "Máximo",
    }

    output = output.rename(columns=rename)

    for column in [
        "Media",
        "Mediana",
        "DE",
        "Mínimo",
        "Máximo",
    ]:
        if column in output.columns:
            output[column] = output[column].apply(
                format_number
            )

    print(output.to_string(index=False))


def print_pre_post_results(
    results: pd.DataFrame,
) -> None:
    """
    Imprime el análisis de variación PRE–POST.
    """

    print()
    print("=" * 92)
    print("EFECTO PRE–POST")
    print("=" * 92)

    if results.empty:
        print(
            "No existen pares PRE–POST válidos "
            "para las variables disponibles."
        )
        return

    columns = [
        "variable_label",
        "n",
        "before_mean",
        "after_mean",
        "delta",
        "delta_percent",
        "p",
        "cohen_dz",
        "effect_magnitude",
        "change_interpretation",
    ]

    available = [
        column
        for column in columns
        if column in results.columns
    ]

    output = results[available].copy()

    rename = {
        "variable_label": "Variable",
        "n": "n",
        "before_mean": "PRE",
        "after_mean": "POST",
        "delta": "Variación",
        "delta_percent": "Variación %",
        "p": "p",
        "cohen_dz": "dz",
        "effect_magnitude": "Magnitud",
        "change_interpretation": "Interpretación",
    }

    output = output.rename(columns=rename)

    for column in [
        "PRE",
        "POST",
        "Variación",
        "Variación %",
        "p",
        "dz",
    ]:
        if column in output.columns:
            output[column] = output[column].apply(
                format_number
            )

    print(output.to_string(index=False))


def print_moment_analysis(
    dataframe: pd.DataFrame,
    mode: str,
) -> pd.DataFrame:
    """
    Ejecuta e imprime el análisis seleccionado.
    """

    selected_mode = (
        str(mode)
        .strip()
        .upper()
        .replace("-", "_")
    )

    results = run_moment_analysis(
        dataframe=dataframe,
        mode=selected_mode,
    )

    if selected_mode == MODE_PRE:
        print_single_moment_results(
            results,
            "ANÁLISIS DE REGISTROS PRE",
        )

    elif selected_mode == MODE_POST:
        print_single_moment_results(
            results,
            "ANÁLISIS DE REGISTROS POST",
        )

    elif selected_mode in {
        MODE_PRE_POST,
        "PREPOST",
        "EFECTO",
        "EFFECT",
    }:
        print_pre_post_results(results)

    else:
        raise ValueError(
            "Modo no válido. Utilice PRE, POST o PRE_POST."
        )

    return results


if __name__ == "__main__":

    sample = pd.DataFrame({
        "participant": [
            "A", "A",
            "B", "B",
            "C", "C",
        ],
        "date": pd.to_datetime([
            "2026-07-01",
            "2026-07-01",
            "2026-07-02",
            "2026-07-02",
            "2026-07-03",
            "2026-07-03",
        ]),
        "moment": [
            1, 2,
            1, 2,
            1, 2,
        ],
        "fatigue": [
            6, 4,
            5, 4,
            7, 5,
        ],
        "energy": [
            4, 6,
            5, 6,
            3, 5,
        ],
        "stress": [
            7, 5,
            6, 4,
            5, 3,
        ],
    })

    print_moment_analysis(
        sample,
        MODE_PRE,
    )

    print_moment_analysis(
        sample,
        MODE_POST,
    )

    print_moment_analysis(
        sample,
        MODE_PRE_POST,
    )
