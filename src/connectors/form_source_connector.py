# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Conector validado para localizar y leer exportaciones de Google Forms,
Excel, CSV y TXT sincronizadas localmente o mediante Google Drive.
"""

from __future__ import annotations

import unicodedata
from io import StringIO
from pathlib import Path
from typing import Iterable

import pandas as pd

from src.config.project_config import INPUT, OUTPUT, RESULTS, ROOT


DRIVE_FOLDERS = [
    Path("G:/Mi unidad"),
]

KEYWORDS = [
    "FORMULARIO",
    "FORMS",
    "GOOGLE",
    "PRESION",
    "PRESIÓN",
    "ARTERIAL",
    "CUESTIONARIO",
    "SATURACION",
    "SATURACIÓN",
    "BIENESTAR",
    "MOOD",
    "ICBR",
    "CANCER",
    "CÁNCER",
]

VALID_EXTENSIONS = {".xlsx", ".xls", ".csv", ".txt"}

EXCLUDED_NAMES = {
    "MASTER_DATABASE.XLSX",
    "UNIFIED_DATABASE.XLSX",
    "BASE_MAESTRA_ICBR_M.XLSX",
    "BASE_UNIFICADA_ICBR_M.XLSX",
}

EXCLUDED_TERMS = {
    "BACKUP",
    "RESULTADO",
    "INFORME",
    "DICCIONARIO",
    "DEBUG",
    "ERROR",
    "LOGIN",
    "RESPUESTA_HTML",
}

PRIORITY_SHEETS = [
    "Respuestas de formulario 1",
    "Form Responses 1",
    "Datos",
    "Base_maestra",
    "Base_unificada",
    "Sheet1",
    "Hoja1",
    "Hoja 1",
]


def normalize_text(value: object) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )
    return text.upper().strip()


def clean_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    output = dataframe.copy()
    output.columns = [str(column).strip() for column in output.columns]
    return output.dropna(how="all").reset_index(drop=True)


def is_html_login(text: str) -> bool:
    sample = text[:5000].lower()

    return any(
        marker in sample
        for marker in (
            "<html",
            "<!doctype html",
            "accounts.google.com",
            "signin",
        )
    )


def is_candidate_file(path: Path) -> bool:
    if not path.is_file():
        return False

    if path.suffix.lower() not in VALID_EXTENSIONS:
        return False

    name = path.name.upper()

    if name.startswith("~$"):
        return False

    if name in EXCLUDED_NAMES:
        return False

    if any(term in name for term in EXCLUDED_TERMS):
        return False

    try:
        resolved = path.resolve()

        if OUTPUT.resolve() in resolved.parents:
            return False

        if RESULTS.resolve() in resolved.parents:
            return False
    except OSError:
        pass

    normalized_name = normalize_text(name)

    return any(
        normalize_text(keyword) in normalized_name
        for keyword in KEYWORDS
    )


def _search_folder(folder: Path) -> list[Path]:
    candidates: list[Path] = []

    if not folder.exists():
        return candidates

    for extension in VALID_EXTENSIONS:
        try:
            for path in folder.rglob(f"*{extension}"):
                if is_candidate_file(path):
                    candidates.append(path)
        except (OSError, PermissionError):
            continue

    return candidates


def remove_duplicates(paths: Iterable[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[str] = set()

    for path in paths:
        try:
            key = str(path.resolve()).lower()
        except OSError:
            key = str(path).lower()

        if key not in seen:
            seen.add(key)
            unique.append(path)

    return unique


def find_source_files(
    include_drive: bool = True,
) -> list[Path]:
    candidates: list[Path] = []

    search_folders = [
        ROOT,
        INPUT,
    ]

    if include_drive:
        search_folders.extend(DRIVE_FOLDERS)

    for folder in search_folders:
        candidates.extend(_search_folder(folder))

    return remove_duplicates(candidates)


def source_priority(path: Path) -> tuple[int, float]:
    score = 0
    extension = path.suffix.lower()

    if extension in {".xlsx", ".xls", ".csv"}:
        score += 4
    elif extension == ".txt":
        score += 1

    try:
        resolved = path.resolve()

        if INPUT.resolve() in resolved.parents:
            score += 8
    except OSError:
        pass

    if any(part.name.lower() in {"datos", "data", "input"} for part in path.parents):
        score += 3

    if path.name.upper() in EXCLUDED_NAMES:
        score -= 100

    try:
        modification_time = path.stat().st_mtime
    except OSError:
        modification_time = 0.0

    return score, modification_time


def select_latest_source(files: Iterable[Path]) -> Path:
    candidates = list(files)

    if not candidates:
        raise FileNotFoundError(
            "No se encontró ningún archivo válido del formulario. "
            "Copia el Excel o CSV en data/input o sincroniza Google Drive."
        )

    return max(candidates, key=source_priority)


def detect_excel_sheet(path: Path) -> str:
    workbook = pd.ExcelFile(path)

    if not workbook.sheet_names:
        raise ValueError(f"El archivo Excel no contiene hojas: {path}")

    normalized_sheets = {
        normalize_text(sheet): sheet
        for sheet in workbook.sheet_names
    }

    for priority in PRIORITY_SHEETS:
        normalized_priority = normalize_text(priority)

        if normalized_priority in normalized_sheets:
            return normalized_sheets[normalized_priority]

    return workbook.sheet_names[0]


def read_source_file(path: Path) -> pd.DataFrame:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(path)

    extension = path.suffix.lower()

    if extension in {".xlsx", ".xls"}:
        sheet = detect_excel_sheet(path)

        dataframe = pd.read_excel(
            path,
            sheet_name=sheet,
        )

        return clean_columns(dataframe)

    if extension == ".csv":
        dataframe = pd.read_csv(
            path,
            sep=None,
            engine="python",
            encoding="utf-8-sig",
            on_bad_lines="skip",
        )

        return clean_columns(dataframe)

    if extension == ".txt":
        text = (
            path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
            .replace("\ufeff", "")
            .strip()
        )

        if is_html_login(text):
            raise ValueError(
                "El TXT contiene una página HTML o un inicio de sesión "
                "de Google, no datos del formulario."
            )

        if text.startswith("OK_CSV_FORMULARIO"):
            text = text.split("\n", 1)[1] if "\n" in text else ""

        dataframe = pd.read_csv(
            StringIO(text),
            sep=None,
            engine="python",
            on_bad_lines="skip",
        )

        return clean_columns(dataframe)

    raise ValueError(f"Extensión no soportada: {extension}")


def load_latest_source(
    include_drive: bool = True,
) -> tuple[Path, pd.DataFrame]:
    files = find_source_files(include_drive=include_drive)
    selected = select_latest_source(files)
    dataframe = read_source_file(selected)

    return selected, dataframe


def print_detected_sources(
    include_drive: bool = True,
) -> list[Path]:
    files = sorted(
        find_source_files(include_drive=include_drive),
        key=source_priority,
        reverse=True,
    )

    print()
    print("=" * 90)
    print("ARCHIVOS DE FORMULARIO DETECTADOS")
    print("=" * 90)

    if not files:
        print("No se encontraron archivos válidos.")
        return []

    for index, path in enumerate(files, start=1):
        priority, _ = source_priority(path)
        print(f"{index:>3}. {path} | prioridad={priority}")

    print("=" * 90)
    print(f"Total: {len(files)}")

    return files


if __name__ == "__main__":
    detected = print_detected_sources(include_drive=True)

    if detected:
        selected, dataframe = load_latest_source(include_drive=True)

        print()
        print(f"Archivo seleccionado: {selected}")
        print(f"Registros: {len(dataframe)}")
        print(f"Columnas: {len(dataframe.columns)}")


