# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Menú interactivo para el análisis por momento de registro:

    1 = PRE
    2 = POST
    3 = Efecto PRE-POST
"""

from __future__ import annotations

import pandas as pd

from src.analysis.moment_analysis import print_moment_analysis
from src.analysis.pre_post import (
    MODE_POST,
    MODE_PRE,
    MODE_PRE_POST,
)
from src.cleaning.clinical_cleaning import clean_clinical_data
from src.config.variable_mapping import prepare_form_dataframe


def prepare_moment_data(
    records: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepara los registros seleccionados para el análisis.
    """

    if records is None or records.empty:
        return pd.DataFrame()

    dataframe = prepare_form_dataframe(
        records.copy()
    )

    dataframe = clean_clinical_data(
        dataframe
    )

    return dataframe


def print_moment_availability(
    dataframe: pd.DataFrame,
) -> None:
    """
    Muestra el número de registros PRE, POST y no válidos.
    """

    print()
    print("DISPONIBILIDAD POR MOMENTO")
    print("-" * 92)

    if "moment" not in dataframe.columns:
        print("No existe la variable 'moment'.")
        return

    moment = (
        dataframe["moment"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    pre_values = {
        "1",
        "1.0",
        "pre",
        "antes",
    }

    post_values = {
        "2",
        "2.0",
        "post",
        "después",
        "despues",
    }

    pre_count = int(
        moment.isin(pre_values).sum()
    )

    post_count = int(
        moment.isin(post_values).sum()
    )

    invalid_count = int(
        len(dataframe) - pre_count - post_count
    )

    print(f"Registros PRE       : {pre_count}")
    print(f"Registros POST      : {post_count}")
    print(f"Registros no válidos: {invalid_count}")


def moment_analysis_menu(
    records: pd.DataFrame,
) -> None:
    """
    Menú de análisis PRE, POST y PRE-POST.
    """

    dataframe = prepare_moment_data(records)

    if dataframe.empty:
        print(
            "\nNo hay datos clínicos disponibles "
            "para analizar."
        )
        return

    while True:
        print()
        print("=" * 92)
        print("ANÁLISIS POR MOMENTO DE REGISTRO")
        print("=" * 92)

        print_moment_availability(
            dataframe
        )

        print()
        print("1. Analizar registros PRE")
        print("2. Analizar registros POST")
        print("3. Analizar efecto PRE-POST")
        print("0. Volver")

        option = input(
            "\nSeleccione una opción: "
        ).strip()

        if option == "1":
            print_moment_analysis(
                dataframe,
                MODE_PRE,
            )

            input(
                "\nPulse Enter para continuar..."
            )

        elif option == "2":
            print_moment_analysis(
                dataframe,
                MODE_POST,
            )

            input(
                "\nPulse Enter para continuar..."
            )

        elif option == "3":
            print_moment_analysis(
                dataframe,
                MODE_PRE_POST,
            )

            input(
                "\nPulse Enter para continuar..."
            )

        elif option == "0":
            return

        else:
            print(
                "\nOpción no válida."
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
        "stress": [
            7, 5,
            6, 4,
            5, 3,
        ],
    })

    moment_analysis_menu(sample)
