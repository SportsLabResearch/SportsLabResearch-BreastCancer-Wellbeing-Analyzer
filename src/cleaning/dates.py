# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Date Cleaning Module
"""

from __future__ import annotations

import datetime as dt
import re

import pandas as pd


MIN_YEAR = 2020


def parse_date(value):

    if pd.isna(value):
        return pd.NaT

    if isinstance(value, pd.Timestamp):
        date = value

    elif isinstance(value, dt.datetime):
        date = pd.Timestamp(value)

    elif isinstance(value, dt.date):
        date = pd.Timestamp(value)

    else:

        text = str(value).strip()

        if re.fullmatch(r"\d+(\.\d+)?", text):

            try:

                serial = float(text)

                if 30000 <= serial <= 60000:

                    date = pd.to_datetime(
                        serial,
                        unit="D",
                        origin="1899-12-30",
                        errors="coerce",
                    )

                else:

                    date = pd.to_datetime(
                        text,
                        dayfirst=True,
                        errors="coerce",
                    )

            except Exception:

                date = pd.NaT

        else:

            date = pd.to_datetime(
                text,
                dayfirst=True,
                errors="coerce",
            )

    if pd.isna(date):

        return pd.NaT

    today = pd.Timestamp.today().normalize()

    if date.year < MIN_YEAR:

        return pd.NaT

    if date > today + pd.Timedelta(days=30):

        return pd.NaT

    return date.normalize()


def clean_dates(dataframe, column):

    dataframe = dataframe.copy()

    dataframe[column] = dataframe[column].apply(
        parse_date
    )

    return dataframe


def remove_invalid_dates(dataframe, column):

    dataframe = dataframe.copy()

    return dataframe[
        dataframe[column].notna()
    ].reset_index(drop=True)


def summary(dataframe, column):

    valid = dataframe[column].notna().sum()

    invalid = dataframe[column].isna().sum()

    return {

        "valid_dates": int(valid),

        "invalid_dates": int(invalid),

        "first_date": dataframe[column].min(),

        "last_date": dataframe[column].max(),

    }


if __name__ == "__main__":

    print()

    print("=" * 80)

    print("DATE CLEANING MODULE")

    print("=" * 80)

    print("Module loaded correctly.")

