# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Clinical Summary Module
"""

from __future__ import annotations

from typing import Dict

import pandas as pd

from src.analysis.statistics import descriptive_statistics


VARIABLES = {
    "hr": {
        "label": "Frecuencia cardiaca",
        "unit": "latidos/minuto",
    },
    "rmssd": {
        "label": "RMSSD",
        "unit": "ms",
    },
    "ln_rmssd": {
        "label": "Ln RMSSD",
        "unit": "",
    },
    "sbp": {
        "label": "Presión arterial sistólica",
        "unit": "mmHg",
    },
    "dbp": {
        "label": "Presión arterial diastólica",
        "unit": "mmHg",
    },
    "spo2": {
        "label": "Saturación de oxígeno",
        "unit": "%",
    },
    "sleep": {
        "label": "Sueño",
        "unit": "1-10",
    },
    "mood": {
        "label": "Estado de ánimo",
        "unit": "1-5",
    },
    "stress": {
        "label": "Estrés",
        "unit": "1-10",
    },
    "fatigue": {
        "label": "Fatiga",
        "unit": "1-10",
    },
    "upper_pain": {
        "label": "Dolor muscular superior",
        "unit": "1-10",
    },
    "lower_pain": {
        "label": "Dolor muscular inferior",
        "unit": "1-10",
    },
}


def most_frequent_text(
    dataframe: pd.DataFrame,
    column: str,
) -> str:
    if column not in dataframe.columns:
        return "No disponible"

    values = (
        dataframe[column]
        .dropna()
        .astype(str)
        .str.strip()
    )

    values = values[values != ""]

    if values.empty:
        return "No disponible"

    return str(values.value_counts().index[0])


def format_date(value) -> str:
    if pd.isna(value):
        return "No disponible"

    return pd.Timestamp(value).strftime("%d/%m/%Y")


def participant_information(
    dataframe: pd.DataFrame,
) -> Dict[str, object]:
    dates = pd.Series(dtype="datetime64[ns]")

    if "date" in dataframe.columns:
        dates = pd.to_datetime(
            dataframe["date"],
            errors="coerce",
            dayfirst=True,
        ).dropna()

    return {
        "participant_id": most_frequent_text(
            dataframe,
            "participant_id",
        ),
        "participant": most_frequent_text(
            dataframe,
            "participant",
        ),
        "site": most_frequent_text(
            dataframe,
            "site",
        ),
        "records": int(len(dataframe)),
        "first_date": (
            format_date(dates.min())
            if not dates.empty
            else "No disponible"
        ),
        "last_date": (
            format_date(dates.max())
            if not dates.empty
            else "No disponible"
        ),
    }


def variable_summary(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    total_records = len(dataframe)

    for variable, metadata in VARIABLES.items():
        if variable not in dataframe.columns:
            continue

        statistics = descriptive_statistics(
            dataframe[variable]
        )

        available = int(statistics["n"])

        availability = (
            available / total_records * 100
            if total_records > 0
            else 0.0
        )

        rows.append({
            "variable": variable,
            "label": metadata["label"],
            "unit": metadata["unit"],
            "n": available,
            "availability_percent": availability,
            "mean": statistics["mean"],
            "median": statistics["median"],
            "sd": statistics["sd"],
            "minimum": statistics["minimum"],
            "maximum": statistics["maximum"],
            "p25": statistics["p25"],
            "p75": statistics["p75"],
            "iqr": statistics["iqr"],
            "cv_percent": statistics["cv_percent"],
        })

    return pd.DataFrame(rows)


def build_clinical_summary(
    dataframe: pd.DataFrame,
) -> Dict[str, object]:
    if dataframe.empty:
        return {
            "participant": {},
            "variables": pd.DataFrame(),
        }

    return {
        "participant": participant_information(
            dataframe
        ),
        "variables": variable_summary(
            dataframe
        ),
    }


def print_clinical_summary(
    dataframe: pd.DataFrame,
) -> None:
    summary = build_clinical_summary(
        dataframe
    )

    participant = summary["participant"]
    variables = summary["variables"]

    print()
    print("=" * 92)
    print("RESUMEN CLÍNICO")
    print("=" * 92)

    if not participant:
        print("No hay datos disponibles.")
        return

    print(
        f"Identificador   : "
        f"{participant['participant_id']}"
    )
    print(
        f"Participante    : "
        f"{participant['participant']}"
    )
    print(
        f"Sede            : "
        f"{participant['site']}"
    )
    print(
        f"Registros       : "
        f"{participant['records']}"
    )
    print(
        f"Primer registro : "
        f"{participant['first_date']}"
    )
    print(
        f"Último registro : "
        f"{participant['last_date']}"
    )

    print()
    print("-" * 92)
    print(
        f"{'VARIABLE':<32}"
        f"{'N':>6}"
        f"{'DISP.%':>10}"
        f"{'MEDIA':>10}"
        f"{'MEDIANA':>10}"
        f"{'MÍN':>9}"
        f"{'MÁX':>9}"
    )
    print("-" * 92)

    if variables.empty:
        print("No hay variables clínicas disponibles.")
        return

    for _, row in variables.iterrows():
        print(
            f"{row['label']:<32}"
            f"{int(row['n']):>6}"
            f"{row['availability_percent']:>9.1f}%"
            f"{row['mean']:>10.2f}"
            f"{row['median']:>10.2f}"
            f"{row['minimum']:>9.2f}"
            f"{row['maximum']:>9.2f}"
        )


if __name__ == "__main__":
    from src.connectors.form_source_connector import (
        load_latest_source,
    )

    _, dataframe = load_latest_source(
        include_drive=False
    )

    identifier = "129"

    if "participant_id" in dataframe.columns:
        participant_ids = (
            dataframe["participant_id"]
            .astype(str)
            .str.strip()
            .str.replace(
                r"\.0$",
                "",
                regex=True,
            )
        )

        participant_dataframe = dataframe[
            participant_ids == identifier
        ].copy()
    else:
        participant_dataframe = pd.DataFrame()

    print_clinical_summary(
        participant_dataframe
    )
