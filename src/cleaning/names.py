# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Name Cleaning Module
"""

from __future__ import annotations

import re
import unicodedata

import pandas as pd


STOPWORDS = {
    "DE",
    "DEL",
    "LA",
    "LAS",
    "LOS",
    "Y",
}


def remove_accents(text: str) -> str:

    return (
        unicodedata
        .normalize("NFKD", str(text))
        .encode("ascii", "ignore")
        .decode("ascii")
    )


def normalize_text(value) -> str:

    if pd.isna(value):

        return ""

    text = remove_accents(str(value))

    text = text.upper().strip()

    text = re.sub(r"[^A-Z ]+", " ", text)

    text = re.sub(r"\s+", " ", text).strip()

    return text


def clean_name(value) -> str:

    text = normalize_text(value)

    if not text:

        return ""

    words = []

    for word in text.split():

        if word in STOPWORDS:

            continue

        words.append(word)

    return " ".join(words)


def split_name(value):

    cleaned = clean_name(value)

    if not cleaned:

        return []

    return cleaned.split()


def initials(value):

    tokens = split_name(value)

    return "".join(token[0] for token in tokens if token)


def clean_column(dataframe, column):

    dataframe = dataframe.copy()

    dataframe[column] = dataframe[column].apply(

        clean_name

    )

    return dataframe


def summary(dataframe, column):

    names = dataframe[column].dropna().astype(str)

    return {

        "participants": names.nunique(),

        "records": len(names),

        "empty": int((names == "").sum()),

    }


if __name__ == "__main__":

    print()

    print("=" * 80)

    print("NAME CLEANING MODULE")

    print("=" * 80)

    print(clean_name("José Pino-Ortega"))

    print(clean_name("María del Carmen López"))

    print(clean_name("Ana de la Torre"))

