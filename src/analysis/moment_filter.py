# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Moment Filter
-------------

Gestiona la variable:

    Momento de registro

        1 = PRE
        2 = POST

Permite:

- Filtrar PRE
- Filtrar POST
- Emparejar PRE-POST
- Calcular cambios
"""

from __future__ import annotations

import pandas as pd


PRE = 1
POST = 2


def normalize_moment(value):
    """
    Convierte cualquier representación del momento
    en PRE (1) o POST (2).

    Devuelve None si el valor no es válido.
    """

    if pd.isna(value):
        return None

    value = str(value).strip().lower()

    mapping = {
        "1": PRE,
        "pre": PRE,
        "antes": PRE,

        "2": POST,
        "post": POST,
        "después": POST,
        "despues": POST,
    }

    return mapping.get(value)


def prepare_dataframe(df, moment_column="Momento de registro"):
    """
    Normaliza la columna de momento.
    """

    dataframe = df.copy()

    dataframe["_moment"] = dataframe[moment_column].apply(
        normalize_moment
    )

    return dataframe


def get_pre(df):

    return df[df["_moment"] == PRE].copy()


def get_post(df):

    return df[df["_moment"] == POST].copy()


def get_valid(df):

    return df[df["_moment"].isin([PRE, POST])].copy()


def get_invalid(df):

    return df[~df["_moment"].isin([PRE, POST])].copy()


def pair_pre_post(
    df,
    id_columns,
    value_columns,
):
    """
    Empareja registros PRE y POST.

    Parameters
    ----------
    id_columns :
        Columnas que identifican la sesión.

    value_columns :
        Variables a comparar.

    Returns
    -------
    DataFrame
    """

    dataframe = get_valid(
        prepare_dataframe(df)
    )

    pre = (
        dataframe[dataframe["_moment"] == PRE]
        .copy()
        .rename(
            columns={
                c: f"{c}_PRE"
                for c in value_columns
            }
        )
    )

    post = (
        dataframe[dataframe["_moment"] == POST]
        .copy()
        .rename(
            columns={
                c: f"{c}_POST"
                for c in value_columns
            }
        )
    )

    merged = pre.merge(
        post,
        on=id_columns,
        how="inner",
    )

    for variable in value_columns:

        merged[f"{variable}_CHANGE"] = (
            merged[f"{variable}_POST"]
            - merged[f"{variable}_PRE"]
        )

        merged[f"{variable}_CHANGE_%"] = (
            (
                merged[f"{variable}_CHANGE"]
                / merged[f"{variable}_PRE"]
            )
            * 100
        )

    return merged


if __name__ == "__main__":

    print("--------------------------------------")
    print(" Moment Filter")
    print("--------------------------------------")
    print("PRE :", PRE)
    print("POST:", POST)
