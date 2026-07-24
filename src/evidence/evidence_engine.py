# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Scientific Evidence Engine
Version 1.0.0
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Any


class ScientificEvidenceEngine:
    """Gestiona la base científica utilizada en los informes."""

    def __init__(self, database_path: str | Path | None = None) -> None:

        if database_path is None:
            database_path = Path(__file__).parent / "variables.json"

        self.database_path = Path(database_path)

        if not self.database_path.exists():
            raise FileNotFoundError(
                f"No se encontró la base científica: {self.database_path}"
            )

        with self.database_path.open("r", encoding="utf-8-sig") as file:
            self.database = json.load(file)

        self.variables = self.database.get("variables", {})

    @staticmethod
    def _normalize(text: str) -> str:

        text = str(text).strip().lower()

        text = unicodedata.normalize("NFD", text)

        text = "".join(
            character
            for character in text
            if unicodedata.category(character) != "Mn"
        )

        return (
            text.replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_")
        )

    def search(self, variable: str) -> dict[str, Any] | None:

        searched = self._normalize(variable)

        for key, information in self.variables.items():

            if searched == self._normalize(key):
                return information

            label = information.get("label", "")

            if searched == self._normalize(label):
                return information

            aliases = information.get("aliases", [])

            for alias in aliases:

                if searched == self._normalize(alias):
                    return information

        return None

    def exists(self, variable: str) -> bool:

        return self.search(variable) is not None

    def get(self, variable: str) -> dict[str, Any] | None:

        return self.search(variable)

    def description(self, variable: str) -> str:

        information = self.search(variable)

        if information is None:
            return ""

        return information.get("description", "")

    def recommendation(self, variable: str) -> str:

        information = self.search(variable)

        if information is None:
            return ""

        return information.get("recommendation", "")

    def references(self, variable: str) -> list[str]:

        information = self.search(variable)

        if information is None:
            return []

        return information.get("references", [])

    def available_variables(self) -> list[str]:

        return [
            information.get("label", key)
            for key, information in self.variables.items()
        ]

    def build_report(self, variable: str) -> str | None:

        information = self.search(variable)

        if information is None:
            return None

        sections = [
            information.get("label", variable),
            "",
            information.get("description", ""),
            "",
            "Significado clínico",
            information.get("clinical_meaning", ""),
            "",
            "Interpretación de valores bajos",
            information.get("low_values", ""),
            "",
            "Interpretación de valores altos",
            information.get("high_values", ""),
            "",
            "Recomendación",
            information.get("recommendation", ""),
            "",
            "Advertencia",
            information.get("alert", ""),
        ]

        references = information.get("references", [])

        if references:

            sections.extend(["", "Referencias científicas"])

            sections.extend(
                f"• {reference}"
                for reference in references
            )

        return "\n".join(
            section
            for section in sections
            if section is not None
        )


if __name__ == "__main__":

    engine = ScientificEvidenceEngine()

    print(engine.build_report("fatiga"))


