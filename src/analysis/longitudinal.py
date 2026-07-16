# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Longitudinal Analysis Engine

Scientific longitudinal monitoring module.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.analysis.statistics import (
    descriptive_statistics,
    linear_regression,
    smallest_worthwhile_change,
)


def prepare_longitudinal_dataset(
    dataframe,
    variable,
    participant_column="participant",
    date_column="date",
):

    required = {
        participant_column,
        date_column,
        variable,
    }

    if not required.issubset(dataframe.columns):

        return pd.DataFrame()

    df = dataframe.copy()

    df[date_column] = pd.to_datetime(
        df[date_column],
        errors="coerce",
    )

    df[variable] = pd.to_numeric(
        df[variable],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            date_column,
            variable,
        ]
    )

    return df.sort_values(
        [
            participant_column,
            date_column,
        ]
    )


def participant_trend(
    dataframe,
    variable,
    participant_column="participant",
    date_column="date",
):

    rows = []

    for participant, group in dataframe.groupby(
        participant_column
    ):

        first_date = group[date_column].min()

        group = group.copy()

        group["days"] = (
            group[date_column] - first_date
        ).dt.days

        regression = linear_regression(
            group["days"],
            group[variable],
        )

        descriptive = descriptive_statistics(
            group[variable]
        )

        swc = smallest_worthwhile_change(
            group[variable]
        )

        first = group[variable].iloc[0]

        last = group[variable].iloc[-1]

        delta = last - first

        percent = (
            delta / first * 100
            if first != 0
            else np.nan
        )

        rows.append({

            "Participant": participant,

            "Sessions": len(group),

            "First value": first,

            "Last value": last,

            "Absolute change": delta,

            "Relative change (%)": percent,

            "Mean": descriptive["mean"],

            "Median": descriptive["median"],

            "SD": descriptive["sd"],

            "CV (%)": descriptive["cv_percent"],

            "IQR": descriptive["iqr"],

            "SWC": swc,

            "Slope/day": regression["slope"],

            "Slope/week": (
                regression["slope"] * 7
                if pd.notna(regression["slope"])
                else np.nan
            ),

            "R²": regression["r_squared"],

            "Equation": regression["equation"],

        })

    return pd.DataFrame(rows)


def classify_change(
    value,
    swc,
    direction,
):

    if pd.isna(value):

        return "Not evaluable"

    if pd.isna(swc):

        return "Stable"

    score = value * direction

    if score >= swc:

        return "Improved"

    if score <= -swc:

        return "Worsened"

    return "Stable"


def longitudinal_summary(
    dataframe,
    direction=1,
):

    dataframe = dataframe.copy()

    dataframe["Status"] = dataframe.apply(

        lambda row:

        classify_change(

            row["Absolute change"],

            row["SWC"],

            direction,

        ),

        axis=1,

    )

    return dataframe


def analyse(
    dataframe,
    variable,
    direction=1,
):

    prepared = prepare_longitudinal_dataset(

        dataframe,

        variable,

    )

    if prepared.empty:

        return pd.DataFrame()

    trends = participant_trend(

        prepared,

        variable,

    )

    return longitudinal_summary(

        trends,

        direction,

    )


if __name__ == "__main__":

    sample = pd.DataFrame({

        "participant":[

            "A","A","A",

            "B","B","B",

        ],

        "date":pd.to_datetime([

            "2026-07-01",

            "2026-07-08",

            "2026-07-15",

            "2026-07-01",

            "2026-07-08",

            "2026-07-15",

        ]),

        "sbp":[

            138,

            134,

            130,

            145,

            141,

            136,

        ],

    })

    print()

    print("="*80)

    print("LONGITUDINAL ENGINE")

    print("="*80)

    print(

        analyse(

            sample,

            "sbp",

            direction=-1,

        )

    )

