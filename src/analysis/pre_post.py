# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Generic PRE/POST Analysis Engine

This module performs paired analyses for any variable
defined in the project.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.analysis.statistics import (
    paired_comparison,
    smallest_worthwhile_change,
    responder_analysis,
)


def paired_dataset(
    dataframe: pd.DataFrame,
    variable: str,
    participant_column: str = "participant",
    date_column: str = "date",
    moment_column: str = "moment",
    site_column: str = "site",
    before_label: str = "Antes",
    after_label: str = "Después",
):

    required = {
        participant_column,
        date_column,
        moment_column,
        variable,
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
        values=variable,
        aggfunc="mean",
    ).reset_index()

    if before_label not in table.columns:
        return pd.DataFrame()

    if after_label not in table.columns:
        return pd.DataFrame()

    return table.dropna(
        subset=[before_label, after_label]
    )


def analyse_variable(
    dataframe: pd.DataFrame,
    variable: str,
    favourable_direction: int,
    mcid: float,
):

    table = paired_dataset(
        dataframe,
        variable,
    )

    if table.empty:
        return {}

    before = table["Antes"]

    after = table["Después"]

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
        favourable_direction=favourable_direction,
        swc=swc,
        mcid=mcid,
    )

    return {

        "variable": variable,

        "n": comparison["n"],

        "before_mean": comparison["before_mean"],

        "after_mean": comparison["after_mean"],

        "delta": comparison["delta"],

        "ci95_low": comparison["ci95_low"],

        "ci95_high": comparison["ci95_high"],

        "test": comparison["test"],

        "statistic": comparison["statistic"],

        "p": comparison["p"],

        "cohen_dz": comparison["cohen_dz"],

        "swc": swc,

        "mcid": mcid,

        "swc_responders_n": responders["swc_responders_n"],

        "swc_responders_percent": responders["swc_responders_percent"],

        "mcid_responders_n": responders["mcid_responders_n"],

        "mcid_responders_percent": responders["mcid_responders_percent"],

    }


def analyse_multiple(
    dataframe: pd.DataFrame,
    variables: dict,
):

    rows = []

    for variable, config in variables.items():

        result = analyse_variable(

            dataframe,

            variable,

            favourable_direction=config["direction"],

            mcid=config["mcid"],

        )

        if result:
            rows.append(result)

    return pd.DataFrame(rows)


if __name__ == "__main__":

    sample = pd.DataFrame({

        "participant":[
            "A","A",
            "B","B",
            "C","C",
        ],

        "date":pd.to_datetime([
            "2026-07-01",
            "2026-07-01",
            "2026-07-02",
            "2026-07-02",
            "2026-07-03",
            "2026-07-03",
        ]),

        "moment":[
            "Antes","Después",
            "Antes","Después",
            "Antes","Después",
        ],

        "sbp":[138,130,142,136,128,124],

        "spo2":[96,97,94,95,92,94],

    })

    VARIABLES = {

        "sbp":{

            "direction":-1,

            "mcid":5,

        },

        "spo2":{

            "direction":1,

            "mcid":2,

        },

    }

    print()

    print("="*80)

    print("GENERIC PRE/POST ENGINE")

    print("="*80)

    print(

        analyse_multiple(

            sample,

            VARIABLES,

        )

    )

