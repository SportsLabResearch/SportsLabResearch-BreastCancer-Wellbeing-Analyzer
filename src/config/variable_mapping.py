# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Mapeo único entre las columnas reales del formulario y las variables internas.
"""

from __future__ import annotations

from typing import Dict

import pandas as pd


FORM_TO_INTERNAL: Dict[str, str] = {
    "Marca temporal": "timestamp",
    "Curso Académico": "academic_year",
    "Nombre y apellidos": "participant",
    "Número de Identificación Cátedra": "participant_id",
    "Fecha": "date",
    "Sede Entrenamiento": "site",
    "Momento de registro": "moment",
    "Tipo entrenamiento": "training_type",

    "Readiness (introducir sólo el número, separación decimales, utilizar coma)":
        "readiness",
    "Heart Rate latidos/minuto": "hr",
    "RMSSD": "rmssd",
    "Ln RMSSD": "ln_rmssd",
    "PNS index": "pns_index",
    "SNS index": "sns_index",
    "Mean RR": "mean_rr",
    "SDNN": "sdnn",
    "Poincaré SD1": "sd1",
    "Poincaré SD2": "sd2",
    "Stress index": "stress_index",
    "Respiratory rate": "respiratory_rate",
    "LF power": "lf_power",
    "HF power": "hf_power",
    "LF power (n.u.)": "lf_power_nu",
    "HF power (n.u.)": "hf_power_nu",
    "LF/HF rate": "lf_hf",
    "Measurement quality": "measurement_quality",

    "Percepción subjetiva del esfuerzo": "rpe",
    "¿Cuántas energía mental tienes esta mañana?": "mental_energy",
    "¿Cuánto te duelen los músculos esta mañana?": "general_muscle_pain",
    "Sueño": "sleep",
    "Mood": "mood",
    "Estrés": "stress",
    "Fatiga": "fatigue",
    "Dolor muscular superior": "upper_pain",
    "Dolor muscular inferior": "lower_pain",

    "Saturación de oxígeno": "spo2",
    "Presión sistólica": "sbp",
    "Presión distólica": "dbp",

    "¿Cómo definirías tu estilo de vida actual), 1 inestable, estrés 10 normal puedo concentrarme":
        "lifestyle",
    "¿Estás lesionado? especifica tipo lesión": "injury",
    "¿Bebiste alcohol ayer por la noche?": "alcohol",
    "¿Estas malo/a hoy?": "illness",
    "¿Quieres anotar algo más?": "observations",
}


VARIABLE_METADATA = {
    "sleep": {
        "label": "Sueño",
        "minimum": 1,
        "maximum": 10,
        "better": "higher",
        "group": "wellbeing",
    },
    "mood": {
        "label": "Estado de ánimo",
        "minimum": 1,
        "maximum": 5,
        "better": "higher",
        "group": "wellbeing",
    },
    "stress": {
        "label": "Estrés",
        "minimum": 1,
        "maximum": 10,
        "better": "lower",
        "group": "wellbeing",
    },
    "fatigue": {
        "label": "Fatiga",
        "minimum": 1,
        "maximum": 10,
        "better": "lower",
        "group": "wellbeing",
    },
    "upper_pain": {
        "label": "Dolor muscular superior",
        "minimum": 1,
        "maximum": 10,
        "better": "lower",
        "group": "wellbeing",
    },
    "lower_pain": {
        "label": "Dolor muscular inferior",
        "minimum": 1,
        "maximum": 10,
        "better": "lower",
        "group": "wellbeing",
    },
    "sbp": {
        "label": "Presión arterial sistólica",
        "unit": "mmHg",
        "group": "health",
    },
    "dbp": {
        "label": "Presión arterial diastólica",
        "unit": "mmHg",
        "group": "health",
    },
    "spo2": {
        "label": "Saturación de oxígeno",
        "unit": "%",
        "group": "health",
    },
    "hr": {
        "label": "Frecuencia cardiaca",
        "unit": "latidos/minuto",
        "group": "hrv",
    },
    "rmssd": {
        "label": "RMSSD",
        "unit": "ms",
        "group": "hrv",
    },
    "ln_rmssd": {
        "label": "Ln RMSSD",
        "group": "hrv",
    },
}


NUMERIC_VARIABLES = {
    "readiness",
    "hr",
    "rmssd",
    "ln_rmssd",
    "pns_index",
    "sns_index",
    "mean_rr",
    "sdnn",
    "sd1",
    "sd2",
    "stress_index",
    "respiratory_rate",
    "lf_power",
    "hf_power",
    "lf_power_nu",
    "hf_power_nu",
    "lf_hf",
    "measurement_quality",
    "rpe",
    "mental_energy",
    "general_muscle_pain",
    "sleep",
    "mood",
    "stress",
    "fatigue",
    "upper_pain",
    "lower_pain",
    "spo2",
    "sbp",
    "dbp",
    "lifestyle",
}


def rename_form_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    output = dataframe.copy()

    output.columns = [
        str(column).strip()
        for column in output.columns
    ]

    available_mapping = {
        source: target
        for source, target in FORM_TO_INTERNAL.items()
        if source in output.columns
    }

    output = output.rename(columns=available_mapping)

    return output


def convert_numeric_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    output = dataframe.copy()

    for column in NUMERIC_VARIABLES:
        if column not in output.columns:
            continue

        output[column] = (
            output[column]
            .astype(str)
            .str.strip()
            .str.replace(",", ".", regex=False)
        )

        output[column] = pd.to_numeric(
            output[column],
            errors="coerce",
        )

    return output


def prepare_form_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    output = rename_form_columns(dataframe)
    output = convert_numeric_columns(output)

    if "date" in output.columns:
        output["date"] = pd.to_datetime(
            output["date"],
            errors="coerce",
            dayfirst=True,
        )

    return output


if __name__ == "__main__":
    print("VARIABLE MAPPING")
    print("=" * 80)
    print(f"Columnas mapeadas : {len(FORM_TO_INTERNAL)}")
    print(f"Variables numéricas: {len(NUMERIC_VARIABLES)}")
