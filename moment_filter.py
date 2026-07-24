# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Gestión del momento de registro.

Este módulo:
- normaliza la variable ``moment``;
- permite seleccionar PRE, POST o TODOS;
- excluye valores ambiguos como ``1, 2``;
- empareja registros PRE y POST por participante y sesión;
- calcula la variación POST - PRE.
"""

from __future__ import annotations

import unicodedata
from typing import Iterable, Sequence

import numpy as np
import pandas as pd


MOMENT_PRE = 1
MOMENT_POST = 2

MOMENT_LABELS = {
    MOMENT_PRE: "PRE",
    MOMENT_POST: "POST",
}


_PRE_VALUES = {
    "1",
    "1.0",
    "pre",
    "antes",
    "before",
}

_POST_VALUES = {
    "2",
    "2.0",
    "post",
    "despues",
    "after",
}


def _plain_text(value: object) -> str:
    """Convierte un valor en texto normalizado sin tildes."""
    if pd.isna(value):
        return ""

    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))

    return " ".join(text.split())


def normalize_moment_value(value: object) -> int | pd.NA:
    """
    Normaliza un valor individual del momento de registro.

    Devuelve:
        1 para PRE.
        2 para POST.
        pd.NA para valores vacíos, desconocidos o ambiguos.

    Los valores combinados como ``1, 2`` no se asignan a ningún momento,
    porque no permiten identificar de forma segura si el registro es PRE o POST.
    """
    text = _plain_text(value)

    if not text:
        return pd.NA

    if text in _PRE_VALUES:
        return MOMENT_PRE

    if text in _POST_VALUES:
        return MOMENT_POST

    return pd.NA


def normalize_moment_column(
    dataframe: pd.DataFrame,
    moment_column: str = "moment",
    label_column: str = "moment_label",
) -> pd.DataFrame:
    """Normaliza la columna de momento y añade su etiqueta PRE/POST."""
    if moment_column not in dataframe.columns:
        raise KeyError(
            f"No existe la columna obligatoria '{moment_column}'."
        )

    output = dataframe.copy()

    output[moment_column] = (
        output[moment_column]
        .map(normalize_moment_value)
        .astype("Int64")
    )

    output[label_column] = output[moment_column].map(MOMENT_LABELS)

    return output


def invalid_moment_records(
    dataframe: pd.DataFrame,
    moment_column: str = "moment",
) -> pd.DataFrame:
    """Devuelve los registros cuyo momento no puede clasificarse."""
    if moment_column not in dataframe.columns:
        raise KeyError(
            f"No existe la columna obligatoria '{moment_column}'."
        )

    normalized = dataframe[moment_column].map(normalize_moment_value)
    return dataframe.loc[normalized.isna()].copy()


def filter_by_moment(
    dataframe: pd.DataFrame,
    moment: int | str,
    moment_column: str = "moment",
) -> pd.DataFrame:
    """
    Selecciona registros PRE, POST o TODOS.

    Valores admitidos:
        PRE: 1, "1", "PRE", "ANTES".
        POST: 2, "2", "POST", "DESPUÉS".
        TODOS: 0, "0", "TODOS", "ALL".
    """
    normalized = normalize_moment_column(
        dataframe,
        moment_column=moment_column,
    )

    requested = _plain_text(moment)

    if requested in {"0", "todos", "todo", "all"}:
        return normalized.loc[
            normalized[moment_column].isin([MOMENT_PRE, MOMENT_POST])
        ].copy()

    selected_moment = normalize_moment_value(moment)

    if pd.isna(selected_moment):
        raise ValueError(
            "Momento no válido. Use 1/PRE, 2/POST o 0/TODOS."
        )

    return normalized.loc[
        normalized[moment_column] == int(selected_moment)
    ].copy()


def split_by_moment(
    dataframe: pd.DataFrame,
    moment_column: str = "moment",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devuelve dos DataFrames independientes: PRE y POST."""
    normalized = normalize_moment_column(
        dataframe,
        moment_column=moment_column,
    )

    pre = normalized.loc[
        normalized[moment_column] == MOMENT_PRE
    ].copy()

    post = normalized.loc[
        normalized[moment_column] == MOMENT_POST
    ].copy()

    return pre, post


def pair_pre_post(
    dataframe: pd.DataFrame,
    variables: str | Sequence[str],
    participant_column: str = "participant",
    date_column: str = "date",
    moment_column: str = "moment",
    site_column: str = "site",
    training_column: str = "training_type",
) -> pd.DataFrame:
    """
    Empareja registros PRE y POST pertenecientes a la misma sesión.

    Las claves de emparejamiento son participante y fecha. También se incluyen
    sede y tipo de entrenamiento cuando existen en el DataFrame.

    Para cada variable crea:
        ``variable_pre``
        ``variable_post``
        ``variable_delta`` = POST - PRE
        ``variable_change_percent``
    """
    variable_list = [variables] if isinstance(variables, str) else list(variables)

    required = {
        participant_column,
        date_column,
        moment_column,
        *variable_list,
    }

    missing = sorted(required.difference(dataframe.columns))

    if missing:
        raise KeyError(
            "Faltan columnas obligatorias para emparejar PRE-POST: "
            + ", ".join(missing)
        )

    normalized = normalize_moment_column(
        dataframe,
        moment_column=moment_column,
    )

    normalized = normalized.loc[
        normalized[moment_column].isin([MOMENT_PRE, MOMENT_POST])
    ].copy()

    keys = [participant_column, date_column]

    if site_column in normalized.columns:
        keys.append(site_column)

    if training_column in normalized.columns:
        keys.append(training_column)

    for variable in variable_list:
        normalized[variable] = pd.to_numeric(
            normalized[variable],
            errors="coerce",
        )

    paired = normalized.pivot_table(
        index=keys,
        columns=moment_column,
        values=variable_list,
        aggfunc="mean",
    )

    if paired.empty:
        return pd.DataFrame()

    paired.columns = [
        f"{variable}_{MOMENT_LABELS.get(int(moment), str(moment)).lower()}"
        for variable, moment in paired.columns
    ]

    paired = paired.reset_index()

    complete_variables: list[str] = []

    for variable in variable_list:
        pre_column = f"{variable}_pre"
        post_column = f"{variable}_post"

        if pre_column not in paired.columns or post_column not in paired.columns:
            continue

        complete_variables.append(variable)

        delta_column = f"{variable}_delta"
        percent_column = f"{variable}_change_percent"

        paired[delta_column] = paired[post_column] - paired[pre_column]

        paired[percent_column] = np.where(
            paired[pre_column].notna() & (paired[pre_column] != 0),
            paired[delta_column] / paired[pre_column].abs() * 100,
            np.nan,
        )

    if not complete_variables:
        return pd.DataFrame()

    required_pair_columns: list[str] = []

    for variable in complete_variables:
        required_pair_columns.extend([
            f"{variable}_pre",
            f"{variable}_post",
        ])

    return paired.dropna(
        subset=required_pair_columns,
        how="all",
    ).reset_index(drop=True)


def moment_counts(
    dataframe: pd.DataFrame,
    moment_column: str = "moment",
) -> dict[str, int]:
    """Resume el número de registros PRE, POST e inválidos."""
    if moment_column not in dataframe.columns:
        raise KeyError(
            f"No existe la columna obligatoria '{moment_column}'."
        )

    normalized = dataframe[moment_column].map(normalize_moment_value)

    return {
        "pre": int((normalized == MOMENT_PRE).sum()),
        "post": int((normalized == MOMENT_POST).sum()),
        "invalid": int(normalized.isna().sum()),
        "total": int(len(dataframe)),
    }


if __name__ == "__main__":
    sample = pd.DataFrame({
        "participant": ["A", "A", "B", "B", "C"],
        "date": pd.to_datetime([
            "2026-07-01",
            "2026-07-01",
            "2026-07-02",
            "2026-07-02",
            "2026-07-03",
        ]),
        "site": ["Murcia"] * 5,
        "training_type": ["Fuerza"] * 5,
        "moment": [1, 2, "Antes", "Después", "1, 2"],
        "fatigue": [4, 6, 7, 5, 3],
    })

    print(moment_counts(sample))
    print(pair_pre_post(sample, "fatigue"))
