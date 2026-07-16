# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

SpO2 Analysis Module
"""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd

from src.analysis.statistics import (
    descriptive_statistics,
    linear_regression,
    paired_comparison,
    responder_analysis,
    smallest_worthwhile_change,
)


SPO2_VALID_MIN = 70
SPO2_VALID_MAX = 100

SPO2_WARNING_THRESHOLD = 94
SPO2_CRITICAL_THRESHOLD = 90

SPO2_MCID = 2.0


def clean_spo2(
    dataframe: pd.DataFrame,
    spo2_column: str = "spo2",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    output = dataframe.copy()
    issues = []

    if spo2_column not in output.columns:
        output[spo2_column] = np.nan

    output[spo2_column] = pd.to_numeric(
        output[spo2_column],
        errors="coerce",
    )

    invalid = output[spo2_column].notna() & (
        (output[spo2_column] < SPO2_VALID_MIN)
        | (output[spo2_column] > SPO2_VALID_MAX)
    )

    for index in output.index[invalid]:
        issues.append({
            "row": int(index),
            "variable": spo2_column,
            "value": output.at[index, spo2_column],
            "issue": "SpO2 fuera de rango",
        })

    output.loc[invalid, spo2_column] = np.nan

    return output, pd.DataFrame(issues)


def classify_spo2(value: float) -> str:
    if pd.isna(value):
        return "No evaluable"

    if value < SPO2_CRITICAL_THRESHOLD:
        return "Crítica"

    if value < SPO2_WARNING_THRESHOLD:
        return "Baja"

    return "Adecuada"


def traffic_light(value: float) -> str:
    if pd.isna(value):
        return "⚪"

    if value < SPO2_CRITICAL_THRESHOLD:
        return "🔴"

    if value < SPO2_WARNING_THRESHOLD:
        return "🟡"

    return "🟢"


def interpretation(value: float) -> str:
    classification = classify_spo2(value)

    if classification == "No evaluable":
        return "No hay datos suficientes para interpretar la SpO2."

    if classification == "Crítica":
        return (
            "La saturación media es muy baja. Debe revisarse la calidad "
            "de la medición y valorarse con el equipo sanitario."
        )

    if classification == "Baja":
        return (
            "La saturación media está por debajo del umbral operativo. "
            "Conviene revisar la medición y realizar seguimiento."
        )

    return "La saturación media se encuentra dentro del rango operativo adecuado."


def generate_alerts(
    dataframe: pd.DataFrame,
    spo2_column: str = "spo2",
) -> pd.DataFrame:
    rows = []

    if spo2_column not in dataframe.columns:
        return pd.DataFrame()

    values = pd.to_numeric(
        dataframe[spo2_column],
        errors="coerce",
    )

    for index, value in values.items():
        if pd.isna(value):
            continue

        if value < SPO2_CRITICAL_THRESHOLD:
            rows.append({
                "row": int(index),
                "variable": "Saturación de oxígeno",
                "value": float(value),
                "alert": "SpO2 crítica",
            })

        elif value < SPO2_WARNING_THRESHOLD:
            rows.append({
                "row": int(index),
                "variable": "Saturación de oxígeno",
                "value": float(value),
                "alert": "SpO2 baja",
            })

    return pd.DataFrame(rows)


def descriptive_summary(
    dataframe: pd.DataFrame,
    spo2_column: str = "spo2",
) -> pd.DataFrame:
    stats = descriptive_statistics(
        dataframe.get(
            spo2_column,
            pd.Series(dtype=float),
        )
    )

    return pd.DataFrame([{
        "Variable": "Saturación de oxígeno",
        "n": stats["n"],
        "Media": stats["mean"],
        "Mediana": stats["median"],
        "DT": stats["sd"],
        "Varianza": stats["variance"],
        "Mínimo": stats["minimum"],
        "Máximo": stats["maximum"],
        "P25": stats["p25"],
        "P75": stats["p75"],
        "IQR": stats["iqr"],
        "CV (%)": stats["cv_percent"],
    }])


def global_summary(
    dataframe: pd.DataFrame,
    spo2_column: str = "spo2",
) -> Dict[str, object]:
    values = pd.to_numeric(
        dataframe.get(
            spo2_column,
            pd.Series(dtype=float),
        ),
        errors="coerce",
    )

    mean_value = (
        float(values.mean())
        if values.notna().any()
        else np.nan
    )

    return {
        "records": int(len(dataframe)),
        "valid_spo2": int(values.notna().sum()),
        "spo2_mean": mean_value,
        "classification": classify_spo2(mean_value),
        "traffic_light": traffic_light(mean_value),
        "interpretation": interpretation(mean_value),
    }


def paired_analysis(
    dataframe: pd.DataFrame,
    moment_column: str = "moment",
    before_value: str = "Antes",
    after_value: str = "Después",
    participant_column: str = "participant",
    date_column: str = "date",
    site_column: str = "site",
    spo2_column: str = "spo2",
) -> pd.DataFrame:
    required = {
        moment_column,
        participant_column,
        date_column,
        spo2_column,
    }

    if not required.issubset(dataframe.columns):
        return pd.DataFrame()

    keys = [
        participant_column,
        date_column,
    ]

    if site_column in dataframe.columns:
        keys.append(site_column)

    table = dataframe.pivot_table(
        index=keys,
        columns=moment_column,
        values=spo2_column,
        aggfunc="mean",
    ).reset_index()

    if (
        before_value not in table.columns
        or after_value not in table.columns
    ):
        return pd.DataFrame()

    table = table.dropna(
        subset=[before_value, after_value]
    )

    if table.empty:
        return pd.DataFrame()

    before = table[before_value]
    after = table[after_value]

    comparison = paired_comparison(
        before,
        after,
    )

    swc = smallest_worthwhile_change(
        before
    )

    responders = responder_analysis(
        before,
        after,
        favourable_direction=1,
        swc=swc,
        mcid=SPO2_MCID,
    )

    return pd.DataFrame([{
        "Variable": "Saturación de oxígeno",
        "n emparejado": comparison["n"],
        "Media antes": comparison["before_mean"],
        "Media después": comparison["after_mean"],
        "Delta": comparison["delta"],
        "IC95% inferior": comparison["ci95_low"],
        "IC95% superior": comparison["ci95_high"],
        "Prueba": comparison["test"],
        "Estadístico": comparison["statistic"],
        "p": comparison["p"],
        "Cohen dz": comparison["cohen_dz"],
        "SWC": swc,
        "MCID": SPO2_MCID,
        "Respondedores SWC n": responders["swc_responders_n"],
        "Respondedores SWC %": responders[
            "swc_responders_percent"
        ],
        "Respondedores MCID n": responders["mcid_responders_n"],
        "Respondedores MCID %": responders[
            "mcid_responders_percent"
        ],
    }])


def longitudinal_analysis(
    dataframe: pd.DataFrame,
    date_column: str = "date",
    spo2_column: str = "spo2",
) -> pd.DataFrame:
    if (
        date_column not in dataframe.columns
        or spo2_column not in dataframe.columns
    ):
        return pd.DataFrame()

    working = dataframe.copy()

    working[date_column] = pd.to_datetime(
        working[date_column],
        errors="coerce",
    )

    working[spo2_column] = pd.to_numeric(
        working[spo2_column],
        errors="coerce",
    )

    working = working.dropna(
        subset=[date_column, spo2_column]
    )

    if working.empty:
        return pd.DataFrame()

    first_date = working[date_column].min()

    working["_days"] = (
        working[date_column] - first_date
    ).dt.days

    daily = (
        working[[date_column, "_days", spo2_column]]
        .groupby(
            [date_column, "_days"],
            as_index=False,
        )[spo2_column]
        .mean()
    )

    regression = linear_regression(
        daily["_days"],
        daily[spo2_column],
    )

    weekly_slope = (
        regression["slope"] * 7
        if pd.notna(regression["slope"])
        else np.nan
    )

    return pd.DataFrame([{
        "Variable": "Saturación de oxígeno",
        "n sesiones": regression["n"],
        "Pendiente diaria": regression["slope"],
        "Pendiente semanal": weekly_slope,
        "Intercepto": regression["intercept"],
        "R²": regression["r_squared"],
        "p": regression["p"],
        "Ecuación": regression["equation"],
    }])


def analyse(
    dataframe: pd.DataFrame,
    spo2_column: str = "spo2",
) -> Dict[str, object]:
    cleaned, quality_issues = clean_spo2(
        dataframe,
        spo2_column=spo2_column,
    )

    return {
        "data": cleaned,
        "quality_control": quality_issues,
        "descriptive": descriptive_summary(
            cleaned,
            spo2_column=spo2_column,
        ),
        "summary": global_summary(
            cleaned,
            spo2_column=spo2_column,
        ),
        "alerts": generate_alerts(
            cleaned,
            spo2_column=spo2_column,
        ),
    }


if __name__ == "__main__":
    sample = pd.DataFrame({
        "participant": [
            "A",
            "A",
            "B",
            "B",
            "C",
            "C",
        ],
        "date": pd.to_datetime([
            "2026-07-01",
            "2026-07-01",
            "2026-07-02",
            "2026-07-02",
            "2026-07-03",
            "2026-07-03",
        ]),
        "site": ["Murcia"] * 6,
        "moment": [
            "Antes",
            "Después",
            "Antes",
            "Después",
            "Antes",
            "Después",
        ],
        "spo2": [96, 97, 94, 95, 92, 94],
    })

    results = analyse(sample)

    print("=" * 80)
    print("SpO2 ANALYSIS")
    print("=" * 80)
    print(results["descriptive"])
    print()
    print(results["summary"])
    print()
    print(paired_analysis(sample))
    print()
    print(longitudinal_analysis(sample))
