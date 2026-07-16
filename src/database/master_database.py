# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Master Database Manager
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import datetime as dt

import pandas as pd

from src.config.project_config import DATA


MASTER_DATABASE = DATA / "MASTER_DATABASE.xlsx"


class MasterDatabase:

    def __init__(self):

        DATA.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def row_hash(row) -> str:

        txt = "||".join("" if pd.isna(v) else str(v).strip() for v in row.values)

        return hashlib.sha256(
            txt.encode("utf-8")
        ).hexdigest()

    def exists(self) -> bool:

        return MASTER_DATABASE.exists()

    def load(self) -> pd.DataFrame:

        if not self.exists():

            return pd.DataFrame()

        return pd.read_excel(MASTER_DATABASE)

    def save(self, dataframe: pd.DataFrame):

        dataframe.to_excel(
            MASTER_DATABASE,
            index=False,
        )

    def update(self, dataframe: pd.DataFrame):

        dataframe = dataframe.copy()

        dataframe["__hash__"] = dataframe.apply(
            self.row_hash,
            axis=1,
        )

        dataframe["__import_date__"] = dt.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        if not self.exists():

            self.save(dataframe)

            return {

                "new_records": len(dataframe),

                "total_records": len(dataframe),

            }

        master = self.load()

        if "__hash__" not in master.columns:

            master["__hash__"] = master.apply(
                self.row_hash,
                axis=1,
            )

        hashes = set(master["__hash__"].astype(str))

        new_rows = dataframe[
            ~dataframe["__hash__"].astype(str).isin(hashes)
        ].copy()

        if len(new_rows):

            master = pd.concat(
                [master, new_rows],
                ignore_index=True,
            )

            self.save(master)

        return {

            "new_records": len(new_rows),

            "total_records": len(master),

        }


if __name__ == "__main__":

    db = MasterDatabase()

    print()

    print("MASTER DATABASE")

    print("=" * 80)

    print(MASTER_DATABASE)

    print()

    print("Exists :", db.exists())

    if db.exists():

        print("Rows   :", len(db.load()))

    else:

        print("Rows   : 0")
