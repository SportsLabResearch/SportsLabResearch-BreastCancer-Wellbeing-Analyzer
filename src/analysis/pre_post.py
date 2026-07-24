# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Motor de análisis por momento de registro.

Momento:
    1 = PRE
    2 = POST

Modos disponibles:
    PRE
    POST
    PRE_POST
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.analysis.moment_filter import normalize_moment
from src.analysis.statistics import (
    descriptive_statistics,
    paired_comparison,
    responder_analysis,
    smallest_worthwhile_change,
)


PRE = 1
POST = 2

MODE_PRE = "PRE"
MODE_POST = "POST"
MODE_PRE_POST = "PRE_POST"


def prepare_moment_column(
    dataframe: pd.DataFrame,
    moment_column: str = "moment",
) -> pd.DataFrame:
    """
    Normaliza la variable de momento.

    Acepta:
        1, PRE, Antes
        2, POST, Después
    """

    if moment_column not in dataframe.columns:
        raise KeyError(
            f"No existe la columna de momento: {moment_column}"
        )

    result = dataframe.copy()

    result["_moment"] = result[moment_column].apply(
        normalize_moment
    )

    return result


def filter_by_moment(
    dataframe: pd.DataFrame,
    moment: int | str,
    moment_column: str = "moment",
) -> pd.DataFrame:
    """
    Filtra los registros PRE o POST.
    """

    normalized = normalize_moment(moment)

    if normalized not in (PRE, POST):
        raise ValueError(
            "El momento debe ser 1/PRE/Antes o 2/POST/Después."
        )

    prepared = prepare_moment_column(
        dataframe,
        moment_column=moment_column,
    )

    return prepared[
        prepared["_moment"] == normalized
    ].copy()


def analyse_single_moment(
    dataframe: pd.DataFrame,
    variables: dict,
    moment: int | str,
    moment_column: str = "moment",
) -> pd.DataFrame:
    """
    Realiza el análisis descriptivo de PRE o POST.
    """

    selected = filter_by_moment(
        dataframe,
        moment=moment,
        moment_column=moment_column,
    )

    moment_value = normalize_moment(moment)
    moment_label = MODE_PRE if moment_value == PRE else MODE_POST

    rows = []

    for variable in variables:

        if variable not in selected.columns:
            continue

        stats = descriptive_statistics(
            selected[variable]
        )

        rows.append({
            "mode": moment_label,
            "moment": moment_value,
            "variable": variable,
            "n": stats["n"],
            "mean": stats["mean"],
            "median": stats["median"],
            "sd": stats["sd"],
            "minimum": stats["minimum"],
            "maximum": stats["maximum"],
            "p25": stats["p25"],
            "p75": stats["p75"],
            "iqr": stats["iqr"],
            "cv_percent": stats["cv_percent"],
        })

    return pd.DataFrame(rows)


def paired_dataset(
    dataframe: pd.DataFrame,
    variable: str,
    participant_column: str = "participant",
    date_column: str = "date",
    moment_column: str = "moment",
    site_column: str = "site",
    training_column: str = "training_type",
) -> pd.DataFrame:
    """
    Genera una tabla pareada PRE-POST.

    El emparejamiento se realiza por:
        participante;
        fecha;
        sede, cuando existe;
        tipo de entrenamiento, cuando existe.
    """

    required = {
        participant_column,
        date_column,
        moment_column,
        variable,
    }

    if not required.issubset(dataframe.columns):
        return pd.DataFrame()

    prepared = prepare_moment_column(
        dataframe,
        moment_column=moment_column,
    )

    prepared[variable] = pd.to_numeric(
        prepared[variable],
        errors="coerce",
    )

    prepared = prepared[
        prepared["_moment"].isin([PRE, POST])
    ].copy()

    keys = [
        participant_column,
        date_column,
    ]

    if site_column in prepared.columns:
        keys.append(site_column)

    if training_column in prepared.columns:
        keys.append(training_column)

    table = prepared.pivot_table(
        index=keys,
        columns="_moment",
        values=variable,
        aggfunc="mean",
    ).reset_index()

    if PRE not in table.columns:
        return pd.DataFrame()

    if POST not in table.columns:
        return pd.DataFrame()

    table = table.rename(
        columns={
            PRE: "PRE",
            POST: "POST",
        }
    )

    table = table.dropna(
        subset=["PRE", "POST"]
    ).copy()

    table["CHANGE"] = (
        table["POST"] - table["PRE"]
    )

    table["CHANGE_PERCENT"] = np.where(
        table["PRE"] != 0,
        table["CHANGE"] / table["PRE"] * 100,
        np.nan,
    )

    return table


def interpret_change(
    delta: float,
    favourable_direction: int,
    threshold: float = 0.0,
) -> str:
    """
    Interpreta la dirección del cambio.

    favourable_direction:
         1 = mejorar al aumentar
        -1 = mejorar al disminuir
    """

    if pd.isna(delta):
        return "No evaluable"

    adjusted_change = delta * favourable_direction

    if abs(adjusted_change) <= threshold:
        return "Sin cambio relevante"

    if adjusted_change > 0:
        return "Cambio favorable"

    return "Cambio desfavorable"


def effect_magnitude(cohen_dz: float) -> str:
    """
    Clasifica la magnitud del tamaño del efecto.
    """

    if pd.isna(cohen_dz):
        return "No evaluable"

    value = abs(cohen_dz)

    if value < 0.20:
        return "Trivial"

    if value < 0.50:
        return "Pequeño"

    if value < 0.80:
        return "Moderado"

    return "Grande"


def analyse_variable(
    dataframe: pd.DataFrame,
    variable: str,
    favourable_direction: int,
    mcid: float,
    participant_column: str = "participant",
    date_column: str = "date",
    moment_column: str = "moment",
    site_column: str = "site",
    training_column: str = "training_type",
) -> dict:
    """
    Analiza el efecto PRE-POST de una variable.
    """

    table = paired_dataset(
        dataframe=dataframe,
        variable=variable,
        participant_column=participant_column,
        date_column=date_column,
        moment_column=moment_column,
        site_column=site_column,
        training_column=training_column,
    )

    if table.empty:
        return {}

    pre = table["PRE"]
    post = table["POST"]

    comparison = paired_comparison(
        pre,
        post,
    )

    swc = smallest_worthwhile_change(
        pre
    )

    responders = responder_analysis(
        pre,
        post,
        favourable_direction=favourable_direction,
        swc=swc,
        mcid=mcid,
    )

    delta = comparison["delta"]

    return {
        "mode": MODE_PRE_POST,
        "variable": variable,
        "n": comparison["n"],
        "before_mean": comparison["before_mean"],
        "after_mean": comparison["after_mean"],
        "delta": delta,
        "delta_percent": (
            float(table["CHANGE_PERCENT"].mean())
            if not table["CHANGE_PERCENT"].dropna().empty
            else np.nan
        ),
        "ci95_low": comparison["ci95_low"],
        "ci95_high": comparison["ci95_high"],
        "test": comparison["test"],
        "statistic": comparison["statistic"],
        "p": comparison["p"],
        "cohen_dz": comparison["cohen_dz"],
        "effect_magnitude": effect_magnitude(
            comparison["cohen_dz"]
        ),
        "favourable_direction": favourable_direction,
        "change_interpretation": interpret_change(
            delta=delta,
            favourable_direction=favourable_direction,
            threshold=swc if pd.notna(swc) else 0.0,
        ),
        "swc": swc,
        "mcid": mcid,
        "swc_responders_n": responders[
            "swc_responders_n"
        ],
        "swc_responders_percent": responders[
            "swc_responders_percent"
        ],
        "mcid_responders_n": responders[
            "mcid_responders_n"
        ],
        "mcid_responders_percent": responders[
            "mcid_responders_percent"
        ],
    }


def analyse_multiple(
    dataframe: pd.DataFrame,
    variables: dict,
    participant_column: str = "participant",
    date_column: str = "date",
    moment_column: str = "moment",
    site_column: str = "site",
    training_column: str = "training_type",
) -> pd.DataFrame:
    """
    Analiza múltiples variables PRE-POST.

    Formato esperado:

    VARIABLES = {
        "fatigue": {
            "direction": -1,
            "mcid": 1,
        },
        "energy": {
            "direction": 1,
            "mcid": 1,
        },
    }
    """

    rows = []

    for variable, config in variables.items():

        if variable not in dataframe.columns:
            continue

        result = analyse_variable(
            dataframe=dataframe,
            variable=variable,
            favourable_direction=config.get(
                "direction",
                1,
            ),
            mcid=config.get(
                "mcid",
                np.nan,
            ),
            participant_column=participant_column,
            date_column=date_column,
            moment_column=moment_column,
            site_column=site_column,
            training_column=training_column,
        )

        if result:
            rows.append(result)

    return pd.DataFrame(rows)


def analyse_by_mode(
    dataframe: pd.DataFrame,
    variables: dict,
    mode: str,
    moment_column: str = "moment",
) -> pd.DataFrame:
    """
    Ejecuta el modo solicitado.

    PRE:
        análisis descriptivo de los registros previos.

    POST:
        análisis descriptivo de los registros posteriores.

    PRE_POST:
        análisis pareado y efecto de la variación.
    """

    selected_mode = str(mode).strip().upper().replace("-", "_")

    if selected_mode == MODE_PRE:
        return analyse_single_moment(
            dataframe=dataframe,
            variables=variables,
            moment=PRE,
            moment_column=moment_column,
        )

    if selected_mode == MODE_POST:
        return analyse_single_moment(
            dataframe=dataframe,
            variables=variables,
            moment=POST,
            moment_column=moment_column,
        )

    if selected_mode in {
        MODE_PRE_POST,
        "PREPOST",
        "EFFECT",
        "EFECTO",
    }:
        return analyse_multiple(
            dataframe=dataframe,
            variables=variables,
            moment_column=moment_column,
        )

    raise ValueError(
        "Modo no válido. Utilice PRE, POST o PRE_POST."
    )


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
    })

    variables = {
        "fatigue": {
            "direction": -1,
            "mcid": 1,
        },
        "energy": {
            "direction": 1,
            "mcid": 1,
        },
    }

    print("=" * 80)
    print("ANÁLISIS PRE")
    print("=" * 80)
    print(analyse_by_mode(sample, variables, MODE_PRE))

    print()
    print("=" * 80)
    print("ANÁLISIS POST")
    print("=" * 80)
    print(analyse_by_mode(sample, variables, MODE_POST))

    print()
    print("=" * 80)
    print("EFECTO PRE-POST")
    print("=" * 80)
    print(analyse_by_mode(sample, variables, MODE_PRE_POST))
