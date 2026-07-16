# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Scoring Engine
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.analysis.variables import (
    VARIABLES,
    ICBR_RECOVERY,
    ICBR_LOAD,
    ICBR_PAIN,
)

WEIGHTS = {
    "sleep": 0.4335,
    "mood": 0.7983,
    "stress": 0.6744,
    "fatigue": 0.9853,
    "upper_pain": 0.7484,
    "lower_pain": 0.9244,
}

NEGATIVE = {
    "stress",
    "fatigue",
    "upper_pain",
    "lower_pain",
}


def normalize(variable, value):

    if pd.isna(value):
        return np.nan

    info = VARIABLES[variable]

    minimum = info["minimum"]
    maximum = info["maximum"]

    score = (value - minimum) / (maximum - minimum) * 100

    if variable in NEGATIVE:
        score = 100 - score

    return score


def weighted_score(row, variables):

    values = []
    weights = []

    for variable in variables:

        if variable not in row.index:
            continue

        value = normalize(variable, row[variable])

        if pd.isna(value):
            continue

        w = WEIGHTS[variable]

        values.append(value * w)
        weights.append(w)

    if not weights:
        return np.nan

    return float(np.sum(values) / np.sum(weights))


def calculate_scores(dataframe):

    dataframe = dataframe.copy()

    dataframe["ICBR-R"] = dataframe.apply(
        lambda row: weighted_score(row, ICBR_RECOVERY),
        axis=1,
    )

    dataframe["ICBR-CP"] = dataframe.apply(
        lambda row: weighted_score(row, ICBR_LOAD),
        axis=1,
    )

    dataframe["ICBR-D"] = dataframe.apply(
        lambda row: weighted_score(row, ICBR_PAIN),
        axis=1,
    )

    dataframe["ICBR-G"] = dataframe[
        ["ICBR-R", "ICBR-CP", "ICBR-D"]
    ].mean(axis=1)

    return dataframe


if __name__ == "__main__":

    sample = pd.DataFrame({
        "sleep":[8],
        "mood":[7],
        "stress":[3],
        "fatigue":[4],
        "upper_pain":[2],
        "lower_pain":[5],
    })

    print(calculate_scores(sample))
