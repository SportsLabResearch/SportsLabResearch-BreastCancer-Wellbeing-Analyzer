# -*- coding: utf-8 -*-

"""
Connector manager.

Detecta y lista archivos compatibles disponibles en data/input.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from src.config.project_config import INPUT, SUPPORTED_FORMATS


def find_input_files() -> List[Path]:
    """Devuelve los archivos compatibles disponibles en data/input."""
    INPUT.mkdir(parents=True, exist_ok=True)

    files = [
        path
        for path in INPUT.iterdir()
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_FORMATS
        and not path.name.startswith("~$")
    ]

    return sorted(files, key=lambda path: path.name.lower())


def group_files_by_format(files: List[Path]) -> Dict[str, List[Path]]:
    """Agrupa los archivos detectados por extensión."""
    grouped: Dict[str, List[Path]] = {}

    for path in files:
        grouped.setdefault(path.suffix.lower(), []).append(path)

    return grouped


def print_detected_files() -> List[Path]:
    """Muestra los archivos detectados y devuelve la lista."""
    files = find_input_files()

    print("\nARCHIVOS DE ENTRADA DETECTADOS")
    print("=" * 90)

    if not files:
        print(f"No hay archivos compatibles en: {INPUT.resolve()}")
        print(f"Formatos admitidos: {', '.join(SUPPORTED_FORMATS)}")
        print("=" * 90)
        return []

    for index, path in enumerate(files, start=1):
        size_kb = path.stat().st_size / 1024
        print(
            f"{index:>3}. {path.name} | "
            f"{path.suffix.upper().replace('.', '')} | "
            f"{size_kb:.1f} KB"
        )

    print("=" * 90)
    print(f"Total de archivos: {len(files)}")

    return files


def select_input_file() -> Path | None:
    """Permite seleccionar un archivo detectado."""
    files = print_detected_files()

    if not files:
        return None

    print("\n0. Cancelar")

    while True:
        raw = input("Seleccione un archivo: ").strip()

        if raw == "0":
            return None

        try:
            index = int(raw)

            if 1 <= index <= len(files):
                selected = files[index - 1]
                print(f"\nArchivo seleccionado: {selected.name}")
                return selected
        except ValueError:
            pass

        print("Selección no válida.")


if __name__ == "__main__":
    select_input_file()
