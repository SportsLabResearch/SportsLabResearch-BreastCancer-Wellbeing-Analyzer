# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Fuzzy Name Matching Engine
"""

from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path

from src.cleaning.names import clean_name

DATA = Path("data")

DECISIONS_FILE = DATA / "fuzzy_decisions.json"


TOKEN_CORRECTIONS = {

    "MANGELES": "MARIANGELES",
    "ESTER": "ESTHER",
    "LLA": "LLANOS",
    "LLANS": "LLANOS",
    "LLENOS": "LLANOS",
    "JULA": "JULIA",
    "HERNANZEZ": "HERNANDEZ",
    "SALNERON": "SALMERON",
    "SANMERON": "SALMERON",
    "ISABE": "ISABEL",
    "PELEGIN": "PELEGRIN",
    "PELGRIN": "PELEGRIN",
    "CARRNO": "CARRENO",
    "CARMEEN": "CARMEN",
    "COBESA": "CONESA",

}


STOPWORDS = {

    "DE",
    "DEL",
    "LA",
    "LAS",
    "LOS",
    "Y",
    "MARIA",
    "MA",
    "M",
    "Mª",

}


def normalize_tokens(name):

    cleaned = clean_name(name)

    tokens = []

    for token in cleaned.split():

        token = TOKEN_CORRECTIONS.get(

            token,

            token,

        )

        if token in STOPWORDS:

            continue

        tokens.append(token)

    return tokens


def similarity(a, b):

    return SequenceMatcher(

        None,

        " ".join(normalize_tokens(a)),

        " ".join(normalize_tokens(b)),

    ).ratio()


def are_similar(

    a,

    b,

    threshold=0.85,

):

    return similarity(

        a,

        b,

    ) >= threshold


def build_dictionary(names):

    mapping = {}

    canonical = []

    for name in sorted(set(names)):

        assigned = False

        for ref in canonical:

            if are_similar(

                name,

                ref,

            ):

                mapping[name] = ref

                assigned = True

                break

        if not assigned:

            canonical.append(name)

            mapping[name] = name

    return mapping


def load_decisions():

    if not DECISIONS_FILE.exists():

        return {}

    with open(

        DECISIONS_FILE,

        encoding="utf-8",

    ) as f:

        return json.load(f)


def save_decisions(mapping):

    DATA.mkdir(

        exist_ok=True,

    )

    with open(

        DECISIONS_FILE,

        "w",

        encoding="utf-8",

    ) as f:

        json.dump(

            mapping,

            f,

            indent=4,

            ensure_ascii=False,

        )


if __name__ == "__main__":

    sample = [

        "M Ángeles",

        "Mariangeles",

        "María Ángeles",

        "Josefa Salneron",

        "Josefa Salmerón",

        "Julia Hernanzez",

        "Julia Hernández",

    ]

    dictionary = build_dictionary(sample)

    print()

    print("=" * 80)

    print("FUZZY ENGINE")

    print("=" * 80)

    for k, v in dictionary.items():

        print(f"{k:30} -> {v}")

