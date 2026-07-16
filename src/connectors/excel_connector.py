# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Excel Connector
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


SUPPORTED_EXTENSIONS = [".xlsx", ".xls"]


class ExcelConnector:

    PRIORITY_SHEETS = [
        "Respuestas de formulario 1",
        "Form Responses 1",
        "Datos",
        "Base_maestra",
        "Sheet1",
        "Hoja1",
        "Hoja 1",
    ]

    def __init__(self, file_path: Path):

        self.file_path = Path(file_path)

    def is_valid(self) -> bool:

        return (
            self.file_path.exists()
            and self.file_path.is_file()
            and self.file_path.suffix.lower() in SUPPORTED_EXTENSIONS
        )

    def available_sheets(self):

        xls = pd.ExcelFile(self.file_path)

        return xls.sheet_names

    def detect_sheet(self) -> str:

        xls = pd.ExcelFile(self.file_path)

        for sheet in self.PRIORITY_SHEETS:

            if sheet in xls.sheet_names:

                return sheet

        return xls.sheet_names[0]

    def read(self) -> pd.DataFrame:

        sheet = self.detect_sheet()

        df = pd.read_excel(
            self.file_path,
            sheet_name=sheet,
        )

        return self.clean(df)

    @staticmethod
    def clean(df: pd.DataFrame) -> pd.DataFrame:

        df = df.copy()

        df.columns = [
            str(column).strip()
            for column in df.columns
        ]

        df = df.dropna(
            how="all"
        ).reset_index(
            drop=True
        )

        return df

    def summary(self):

        df = self.read()

        return {

            "file": self.file_path.name,

            "sheet": self.detect_sheet(),

            "rows": len(df),

            "columns": len(df.columns),

            "variables": list(df.columns),

        }


def open_excel(path) -> pd.DataFrame:

    connector = ExcelConnector(path)

    if not connector.is_valid():

        raise FileNotFoundError(path)

    return connector.read()


if __name__ == "__main__":

    from src.config.project_config import INPUT

    files = sorted(INPUT.glob("*.xlsx")) + sorted(INPUT.glob("*.xls"))

    if not files:

        print("No Excel files detected.")

    else:

        connector = ExcelConnector(files[0])

        print(connector.summary())
