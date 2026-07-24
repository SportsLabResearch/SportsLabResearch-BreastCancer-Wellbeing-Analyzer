# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Blood Pressure Analysis Module
"""

from __future__ import annotations

from typing import Dict, Iterable

import numpy as np
import pandas as pd

from src.cleaning.clinical_cleaning import clean_clinical_data

from src.analysis.statistics import (
    descriptive_statistics,
    linear_regression,
    paired_comparison,
    responder_analysis,
    smallest_worthwhile_change,
)


SBP_VALID_MIN = 70
SBP_VALID_MAX = 250
DBP_VALID_MIN = 40
DBP_VALID_MAX = 150

SBP_ALERT_THRESHOLD = 135
DBP_ALERT_THRESHOLD = 85

SBP_MCID = 5.0
DBP_MCID = 3.0


def clean_blood_pressure(
    dataframe: pd.DataFrame,
    sbp_column: str = "sbp",
    dbp_column: str = "dbp",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Convierte PAS/PAD a formato numérico e invalida valores imposibles.

    Devuelve:
    - DataFrame limpio.
    - Tabla de incidencias de control de calidad.
    """
    output = dataframe.copy()
    issues = []

    for column in (sbp_column, dbp_column):
        if column not in output.columns:
            output[column] = np.nan

        output[column] = pd.to_numeric(
            output[column],
            errors="coerce",
        )

    invalid_sbp = output[sbp_column].notna() & (
        (output[sbp_column] < SBP_VALID_MIN)
        | (output[sbp_column] > SBP_VALID_MAX)
    )

    invalid_dbp = output[dbp_column].notna() & (
        (output[dbp_column] < DBP_VALID_MIN)
        | (output[dbp_column] > DBP_VALID_MAX)
    )

    invalid_relation = (
        output[sbp_column].notna()
        & output[dbp_column].notna()
        & (output[sbp_column] <= output[dbp_column])
    )

    for index in output.index[invalid_sbp]:
        issues.append({
            "row": int(index),
            "variable": sbp_column,
            "value": output.at[index, sbp_column],
            "issue": "PAS fuera de rango",
        })

    for index in output.index[invalid_dbp]:
        issues.append({
            "row": int(index),
            "variable": dbp_column,
            "value": output.at[index, dbp_column],
            "issue": "PAD fuera de rango",
        })

    for index in output.index[invalid_relation]:
        issues.append({
            "row": int(index),
            "variable": f"{sbp_column}/{dbp_column}",
            "value": (
                f"{output.at[index, sbp_column]}/"
                f"{output.at[index, dbp_column]}"
            ),
            "issue": "PAS menor o igual que PAD",
        })

    output.loc[invalid_sbp, sbp_column] = np.nan
    output.loc[invalid_dbp, dbp_column] = np.nan

    output.loc[
        invalid_relation,
        [sbp_column, dbp_column],
    ] = np.nan

    return output, pd.DataFrame(issues)


def classify_blood_pressure(
    sbp: float,
    dbp: float,
) -> str:
    """
    Clasificación operativa basada en el umbral domiciliario 135/85 mmHg.
    """
    if pd.isna(sbp) or pd.isna(dbp):
        return "No evaluable"

    if sbp >= SBP_ALERT_THRESHOLD or dbp >= DBP_ALERT_THRESHOLD:
        return "Elevada"

    return "Dentro del umbral"


def traffic_light(
    sbp: float,
    dbp: float,
) -> str:
    if pd.isna(sbp) or pd.isna(dbp):
        return "⚪"

    if sbp >= 160 or dbp >= 100:
        return "🔴"

    if sbp >= SBP_ALERT_THRESHOLD or dbp >= DBP_ALERT_THRESHOLD:
        return "🟡"

    return "🟢"


def interpretation(
    sbp: float,
    dbp: float,
) -> str:
    classification = classify_blood_pressure(sbp, dbp)

    if classification == "No evaluable":
        return "No hay datos suficientes para interpretar la presión arterial."

    if sbp >= 160 or dbp >= 100:
        return (
            "Valores claramente elevados. Conviene repetir la medición "
            "y revisar el resultado con el equipo sanitario."
        )

    if classification == "Elevada":
        return (
            "La media supera al menos uno de los umbrales operativos "
            "de presión arterial domiciliaria."
        )

    return (
        "La presión arterial media se encuentra dentro de los "
        "umbrales operativos configurados."
    )


def generate_alerts(
    dataframe: pd.DataFrame,
    sbp_column: str = "sbp",
    dbp_column: str = "dbp",
) -> pd.DataFrame:
    rows = []

    for index, row in dataframe.iterrows():
        sbp = pd.to_numeric(
            pd.Series([row.get(sbp_column)]),
            errors="coerce",
        ).iloc[0]

        dbp = pd.to_numeric(
            pd.Series([row.get(dbp_column)]),
            errors="coerce",
        ).iloc[0]

        if pd.notna(sbp) and sbp >= SBP_ALERT_THRESHOLD:
            rows.append({
                "row": int(index),
                "variable": "Presión arterial sistólica",
                "value": float(sbp),
                "alert": "PAS elevada",
            })

        if pd.notna(dbp) and dbp >= DBP_ALERT_THRESHOLD:
            rows.append({
                "row": int(index),
                "variable": "Presión arterial diastólica",
                "value": float(dbp),
                "alert": "PAD elevada",
            })

    return pd.DataFrame(rows)


def descriptive_summary(
    dataframe: pd.DataFrame,
    sbp_column: str = "sbp",
    dbp_column: str = "dbp",
) -> pd.DataFrame:
    rows = []

    for column, label in (
        (sbp_column, "Presión arterial sistólica"),
        (dbp_column, "Presión arterial diastólica"),
    ):
        stats = descriptive_statistics(
            dataframe.get(column, pd.Series(dtype=float))
        )

        rows.append({
            "Variable": label,
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
        })

    return pd.DataFrame(rows)


def global_summary(
    dataframe: pd.DataFrame,
    sbp_column: str = "sbp",
    dbp_column: str = "dbp",
) -> Dict[str, object]:
    sbp = pd.to_numeric(
        dataframe.get(sbp_column, pd.Series(dtype=float)),
        errors="coerce",
    )

    dbp = pd.to_numeric(
        dataframe.get(dbp_column, pd.Series(dtype=float)),
        errors="coerce",
    )

    sbp_mean = float(sbp.mean()) if sbp.notna().any() else np.nan
    dbp_mean = float(dbp.mean()) if dbp.notna().any() else np.nan

    return {
        "records": int(len(dataframe)),
        "valid_sbp": int(sbp.notna().sum()),
        "valid_dbp": int(dbp.notna().sum()),
        "sbp_mean": sbp_mean,
        "dbp_mean": dbp_mean,
        "classification": classify_blood_pressure(
            sbp_mean,
            dbp_mean,
        ),
        "traffic_light": traffic_light(
            sbp_mean,
            dbp_mean,
        ),
        "interpretation": interpretation(
            sbp_mean,
            dbp_mean,
        ),
    }


def paired_analysis(
    dataframe: pd.DataFrame,
    moment_column: str = "moment",
    before_value: str = "Antes",
    after_value: str = "Después",
    participant_column: str = "participant",
    date_column: str = "date",
    site_column: str = "site",
    sbp_column: str = "sbp",
    dbp_column: str = "dbp",
) -> pd.DataFrame:
    """
    Analiza el cambio PRE/POST mediante emparejamiento por participante,
    fecha y sede.
    """
    required = {
        moment_column,
        participant_column,
        date_column,
        sbp_column,
        dbp_column,
    }

    if not required.issubset(dataframe.columns):
        return pd.DataFrame()

    keys = [
        participant_column,
        date_column,
    ]

    if site_column in dataframe.columns:
        keys.append(site_column)

    rows = []

    for column, label, mcid in (
        (sbp_column, "Presión arterial sistólica", SBP_MCID),
        (dbp_column, "Presión arterial diastólica", DBP_MCID),
    ):
        table = dataframe.pivot_table(
            index=keys,
            columns=moment_column,
            values=column,
            aggfunc="mean",
        ).reset_index()

        if (
            before_value not in table.columns
            or after_value not in table.columns
        ):
            continue

        table = table.dropna(
            subset=[before_value, after_value]
        )

        if table.empty:
            continue

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
            favourable_direction=-1,
            swc=swc,
            mcid=mcid,
        )

        rows.append({
            "Variable": label,
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
            "MCID": mcid,
            "Respondedores SWC n": responders["swc_responders_n"],
            "Respondedores SWC %": responders[
                "swc_responders_percent"
            ],
            "Respondedores MCID n": responders["mcid_responders_n"],
            "Respondedores MCID %": responders[
                "mcid_responders_percent"
            ],
        })

    return pd.DataFrame(rows)


def longitudinal_analysis(
    dataframe: pd.DataFrame,
    date_column: str = "date",
    sbp_column: str = "sbp",
    dbp_column: str = "dbp",
) -> pd.DataFrame:
    if date_column not in dataframe.columns:
        return pd.DataFrame()

    working = dataframe.copy()
    working[date_column] = pd.to_datetime(
        working[date_column],
        errors="coerce",
    )

    working = working.dropna(
        subset=[date_column]
    )

    if working.empty:
        return pd.DataFrame()

    first_date = working[date_column].min()
    working["_days"] = (
        working[date_column] - first_date
    ).dt.days

    rows = []

    for column, label in (
        (sbp_column, "Presión arterial sistólica"),
        (dbp_column, "Presión arterial diastólica"),
    ):
        if column not in working.columns:
            continue

        daily = (
            working[[date_column, "_days", column]]
            .dropna()
            .groupby(
                [date_column, "_days"],
                as_index=False,
            )[column]
            .mean()
        )

        regression = linear_regression(
            daily["_days"],
            daily[column],
        )

        slope_week = (
            regression["slope"] * 7
            if pd.notna(regression["slope"])
            else np.nan
        )

        rows.append({
            "Variable": label,
            "n sesiones": regression["n"],
            "Pendiente diaria": regression["slope"],
            "Pendiente semanal": slope_week,
            "Intercepto": regression["intercept"],
            "R²": regression["r_squared"],
            "p": regression["p"],
            "Ecuación": regression["equation"],
        })

    return pd.DataFrame(rows)


def analyse(
    dataframe: pd.DataFrame,
    sbp_column: str = "sbp",
    dbp_column: str = "dbp",
) -> Dict[str, object]:
    cleaned = clean_clinical_data(
        dataframe
    )

    cleaned, quality_issues = clean_blood_pressure(
        cleaned,
        sbp_column=sbp_column,
        dbp_column=dbp_column,
    )

    return {
        "data": cleaned,
        "quality_control": quality_issues,
        "descriptive": descriptive_summary(
            cleaned,
            sbp_column=sbp_column,
            dbp_column=dbp_column,
        ),
        "summary": global_summary(
            cleaned,
            sbp_column=sbp_column,
            dbp_column=dbp_column,
        ),
        "alerts": generate_alerts(
            cleaned,
            sbp_column=sbp_column,
            dbp_column=dbp_column,
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
        "sbp": [138, 130, 142, 136, 128, 124],
        "dbp": [88, 82, 91, 86, 80, 78],
    })

    results = analyse(sample)

    print("=" * 80)
    print("BLOOD PRESSURE ANALYSIS")
    print("=" * 80)
    print(results["descriptive"])
    print()
    print(results["summary"])
    print()
    print(paired_analysis(sample))
    print()
    print(longitudinal_analysis(sample))

