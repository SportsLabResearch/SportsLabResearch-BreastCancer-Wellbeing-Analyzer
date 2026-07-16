# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Wellbeing Analysis Engine
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.analysis.scoring import calculate_scores


DOMAINS = {

    "ICBR-R": "Recovery",

    "ICBR-CP": "Perceived Load",

    "ICBR-D": "Pain",

    "ICBR-G": "Global Wellbeing",

}


def classify(value):

    if pd.isna(value):

        return "Not evaluable"

    if value >= 75:

        return "Excellent"

    if value >= 60:

        return "Good"

    if value >= 45:

        return "Moderate"

    return "Poor"


def traffic_light(value):

    if pd.isna(value):

        return "⚪"

    if value >= 75:

        return "🟢"

    if value >= 60:

        return "🟡"

    return "🔴"


def interpretation(value):

    if pd.isna(value):

        return "No interpretation available."

    if value >= 75:

        return "Very favourable status."

    if value >= 60:

        return "Adequate status."

    if value >= 45:

        return "Moderate status. Follow-up recommended."

    return "Unfavourable status. Clinical review recommended."


def analyse(dataframe):

    dataframe = calculate_scores(dataframe)

    summary = []

    for variable in [

        "ICBR-R",

        "ICBR-CP",

        "ICBR-D",

        "ICBR-G",

    ]:

        values = pd.to_numeric(

            dataframe[variable],

            errors="coerce",

        )

        mean = values.mean()

        summary.append({

            "Domain": DOMAINS[variable],

            "Score": mean,

            "Classification": classify(mean),

            "Traffic Light": traffic_light(mean),

            "Interpretation": interpretation(mean),

            "Participants": values.count(),

        })

    return pd.DataFrame(summary)


def participant_scores(dataframe):

    dataframe = calculate_scores(dataframe)

    dataframe["Classification"] = dataframe["ICBR-G"].apply(

        classify

    )

    dataframe["Traffic Light"] = dataframe["ICBR-G"].apply(

        traffic_light

    )

    dataframe["Interpretation"] = dataframe["ICBR-G"].apply(

        interpretation

    )

    return dataframe


if __name__ == "__main__":

    sample = pd.DataFrame({

        "sleep":[8,7,9],

        "mood":[8,7,6],

        "stress":[2,4,5],

        "fatigue":[3,5,6],

        "upper_pain":[2,2,4],

        "lower_pain":[3,4,5],

    })

    print()

    print("=" * 80)

    print("WELLBEING ENGINE")

    print("=" * 80)

    print(analyse(sample))

