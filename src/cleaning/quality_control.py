# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Quality Control Module
"""

from __future__ import annotations

import pandas as pd


class QualityControl:

    def __init__(self):

        self.report = []

    def duplicated_rows(self, dataframe):

        duplicated = dataframe.duplicated()

        self.report.append({

            "Control": "Duplicated rows",

            "Detected": int(duplicated.sum())

        })

        return dataframe.loc[~duplicated].reset_index(drop=True)

    def remove_empty_rows(self, dataframe):

        before = len(dataframe)

        dataframe = dataframe.dropna(how="all").reset_index(drop=True)

        removed = before - len(dataframe)

        self.report.append({

            "Control": "Empty rows",

            "Detected": removed,

        })

        return dataframe

    def missing_columns(self, dataframe, required):

        missing = [

            column

            for column in required

            if column not in dataframe.columns

        ]

        self.report.append({

            "Control": "Required columns",

            "Detected": len(missing),

            "Details": ", ".join(missing),

        })

        return missing

    def out_of_range(

        self,

        dataframe,

        column,

        minimum,

        maximum,

    ):

        if column not in dataframe.columns:

            return dataframe

        values = pd.to_numeric(

            dataframe[column],

            errors="coerce",

        )

        invalid = (

            values.notna()

            & (

                (values < minimum)

                | (values > maximum)

            )

        )

        self.report.append({

            "Control": f"{column} range",

            "Detected": int(invalid.sum()),

        })

        dataframe.loc[invalid, column] = pd.NA

        return dataframe

    def summary(self):

        return pd.DataFrame(self.report)


if __name__ == "__main__":

    df = pd.DataFrame({

        "A": [1, 1, None],

        "B": [2, 2, None],

    })

    qc = QualityControl()

    df = qc.remove_empty_rows(df)

    df = qc.duplicated_rows(df)

    print()

    print("=" * 80)

    print("QUALITY CONTROL")

    print("=" * 80)

    print(qc.summary())

