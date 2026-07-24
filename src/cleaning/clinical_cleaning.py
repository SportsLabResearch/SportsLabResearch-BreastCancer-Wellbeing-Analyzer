# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Clinical Data Cleaning Module
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def clean_blood_pressure(
    values: pd.Series,
    minimum_decimal: float,
    maximum_decimal: float,
) -> pd.Series:
    output = pd.to_numeric(
        values,
        errors="coerce",
    ).astype(float)

    output = output.mask(output <= 0)

    decimal_mask = output.between(
        minimum_decimal,
        maximum_decimal,
        inclusive="both",
    )

    output.loc[decimal_mask] = (
        output.loc[decimal_mask] * 10
    )

    return output


def clean_spo2(values: pd.Series) -> pd.Series:
    output = pd.to_numeric(
        values,
        errors="coerce",
    ).astype(float)

    output = output.mask(output <= 0)

    proportion_mask = output.between(
        0.70,
        1.00,
        inclusive="both",
    )

    output.loc[proportion_mask] = (
        output.loc[proportion_mask] * 100
    )

    decimal_mask = output.between(
        7.0,
        10.0,
        inclusive="left",
    )

    output.loc[decimal_mask] = (
        output.loc[decimal_mask] * 10
    )

    output = output.mask(
        (output < 70) | (output > 100)
    )

    return output


def clean_clinical_data(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    output = dataframe.copy()

    if "sbp" in output.columns:
        output["sbp_raw"] = output["sbp"]

        output["sbp"] = clean_blood_pressure(
            output["sbp"],
            minimum_decimal=7.0,
            maximum_decimal=25.0,
        )

        output["sbp"] = output["sbp"].mask(
            (output["sbp"] < 70)
            | (output["sbp"] > 250)
        )

    if "dbp" in output.columns:
        output["dbp_raw"] = output["dbp"]

        output["dbp"] = clean_blood_pressure(
            output["dbp"],
            minimum_decimal=4.0,
            maximum_decimal=15.0,
        )

        output["dbp"] = output["dbp"].mask(
            (output["dbp"] < 40)
            | (output["dbp"] > 150)
        )

    if "spo2" in output.columns:
        output["spo2_raw"] = output["spo2"]

        output["spo2"] = clean_spo2(
            output["spo2"]
        )

    return output


if __name__ == "__main__":
    from src.connectors.form_source_connector import (
        load_latest_source,
    )

    _, dataframe = load_latest_source(
        include_drive=False
    )

    cleaned = clean_clinical_data(
        dataframe
    )

    print()
    print("=" * 92)
    print("COMPROBACIÓN DE LIMPIEZA CLÍNICA")
    print("=" * 92)

    for variable, minimum, maximum in (
        ("sbp", 70, 250),
        ("dbp", 40, 150),
        ("spo2", 70, 100),
    ):
        values = pd.to_numeric(
            cleaned[variable],
            errors="coerce",
        )

        print(
            f"{variable.upper():<8}"
            f"datos={values.notna().sum():>6}  "
            f"mín={values.min():>7.2f}  "
            f"máx={values.max():>7.2f}  "
            f"fuera_rango="
            f"{((values < minimum) | (values > maximum)).sum()}"
        )
