# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Unified Database Manager
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config.project_config import DATA
from src.database.master_database import MasterDatabase


UNIFIED_DATABASE = DATA / "UNIFIED_DATABASE.xlsx"


class UnifiedDatabase:

    def __init__(self):

        self.master = MasterDatabase()

    def build(self):

        master = self.master.load()

        if master.empty:

            return pd.DataFrame()

        unified = master.copy()

        unified.columns = [

            str(column).strip()

            for column in unified.columns

        ]

        unified = unified.loc[
            :,
            ~unified.columns.duplicated()
        ]

        unified = unified.sort_index(
            axis=1
        )

        unified = unified.sort_values(

            by=[
                column

                for column in [

                    "Fecha",
                    "Nombre",
                    "__import_date__",

                ]

                if column in unified.columns

            ],

            ignore_index=True,

        )

        return unified

    def save(self):

        dataframe = self.build()

        if dataframe.empty:

            return dataframe

        dataframe.to_excel(

            UNIFIED_DATABASE,

            index=False,

        )

        return dataframe

    def summary(self):

        dataframe = self.build()

        if dataframe.empty:

            return {

                "rows": 0,

                "columns": 0,

                "database": str(UNIFIED_DATABASE),

            }

        return {

            "rows": len(dataframe),

            "columns": len(dataframe.columns),

            "database": str(UNIFIED_DATABASE),

        }


if __name__ == "__main__":

    db = UnifiedDatabase()

    dataframe = db.save()

    print()

    print("=" * 80)

    print("UNIFIED DATABASE")

    print("=" * 80)

    print(db.summary())

    if not dataframe.empty:

        print()

        print(dataframe.head())
