# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer
=================================================

Main operativo inicial del proyecto.

Versión: 0.2.0-alpha
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, Dict, List


PROJECT_NAME = "SportsLabResearch-BreastCancer-Wellbeing-Analyzer"
VERSION = "0.2.0-alpha"
AUTHOR = "José Pino-Ortega"
ORGANIZATION = "SportsLabResearch"
PRIMARY_POPULATION = "Women with breast cancer"

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
RESULTS_DIR = ROOT / "results"
DOCS_DIR = ROOT / "docs"
DOCUMENTS_DIR = ROOT / "documents"
ASSETS_DIR = ROOT / "assets"

SUPPORTED_FORMATS = {".xlsx", ".xls", ".csv"}

MODULES = {
    "Importación de datos": "Preparado",
    "Base maestra": "Pendiente de integración",
    "Depuración y control de calidad": "Pendiente de integración",
    "Selección de participantes": "Pendiente de integración",
    "Análisis clínico": "Pendiente de integración",
    "Dashboard": "Pendiente de integración",
    "Informes": "Pendiente de integración",
    "Configuración": "Activo",
    "Auditoría": "Activo",
}


def create_project_folders() -> None:
    for folder in (
        DATA_DIR,
        INPUT_DIR,
        OUTPUT_DIR,
        RESULTS_DIR,
        DOCS_DIR,
        DOCUMENTS_DIR,
        ASSETS_DIR,
    ):
        folder.mkdir(parents=True, exist_ok=True)


def clear_screen() -> None:
    print("\n" * 2)


def pause() -> None:
    input("\nPulse Enter para continuar...")


def print_header() -> None:
    print("=" * 92)
    print(PROJECT_NAME)
    print("=" * 92)
    print(f"Versión      : {VERSION}")
    print(f"Organización : {ORGANIZATION}")
    print(f"Autor        : {AUTHOR}")
    print(f"Población    : {PRIMARY_POPULATION}")
    print("-" * 92)
    print("Plataforma científica para monitorización multidimensional del bienestar y la salud")
    print("=" * 92)


def find_input_files() -> List[Path]:
    if not INPUT_DIR.exists():
        return []

    return sorted(
        [
            path
            for path in INPUT_DIR.iterdir()
            if path.is_file()
            and path.suffix.lower() in SUPPORTED_FORMATS
            and not path.name.startswith("~$")
        ],
        key=lambda p: p.name.lower(),
    )


def show_input_files() -> None:
    print_header()
    print("\nARCHIVOS DE ENTRADA")
    print("-" * 92)

    files = find_input_files()

    if not files:
        print(f"No hay archivos compatibles en: {INPUT_DIR}")
        print("Formatos admitidos: .xlsx, .xls y .csv")
        return

    for index, file in enumerate(files, start=1):
        size_kb = file.stat().st_size / 1024
        print(f"{index:>3}. {file.name} ({size_kb:.1f} KB)")


def import_data_menu() -> None:
    while True:
        print_header()
        print(
            "\nIMPORTAR DATOS\n"
            "1. Ver archivos Excel/CSV disponibles\n"
            "2. Importar desde Excel\n"
            "3. Importar desde CSV\n"
            "4. Importar desde Google Forms\n"
            "0. Volver\n"
        )
        option = input("Seleccione una opción: ").strip()

        if option == "1":
            show_input_files()
            pause()
        elif option in {"2", "3", "4"}:
            print("\nMódulo preparado para integración en la siguiente fase.")
            pause()
        elif option == "0":
            return
        else:
            print("\nOpción no válida.")
            pause()


def base_maestra_menu() -> None:
    print_header()
    print("\nBASE MAESTRA")
    print("-" * 92)
    print("1. Actualizar base maestra")
    print("2. Crear base unificada")
    print("3. Ver estado de la base")
    print("\nMódulo pendiente de integrar con la lógica validada de los scripts originales.")
    pause()


def quality_control_menu() -> None:
    print_header()
    print("\nDEPURACIÓN Y CONTROL DE CALIDAD")
    print("-" * 92)
    print("1. Fechas")
    print("2. Nombres y fuzzy matching")
    print("3. Sedes")
    print("4. PRE / POST")
    print("5. Duplicados")
    print("6. Valores fuera de rango")
    print("\nMódulo pendiente de integración.")
    pause()


def participants_menu() -> None:
    print_header()
    print("\nSELECCIÓN DE PARTICIPANTES")
    print("-" * 92)
    print("1. Seleccionar sede")
    print("2. Seleccionar una participante")
    print("3. Seleccionar varias participantes")
    print("4. Seleccionar todas")
    print("\nMódulo pendiente de integración.")
    pause()


def analysis_menu() -> None:
    print_header()
    print("\nANÁLISIS CLÍNICO")
    print("-" * 92)
    print("1. Bienestar")
    print("2. Presión arterial")
    print("3. SpO2")
    print("4. ICBR-M")
    print("5. PRE / POST")
    print("6. Longitudinal")
    print("\nMódulo pendiente de integración.")
    pause()


def dashboards_menu() -> None:
    print_header()
    print("\nDASHBOARDS")
    print("-" * 92)
    print("1. Dashboard clínico")
    print("2. Dashboard participante")
    print("3. Dashboard profesional")
    print("4. Dashboard grupal")
    print("5. Dashboard longitudinal")
    print("\nMódulo pendiente de integración.")
    pause()


def reports_menu() -> None:
    print_header()
    print("\nINFORMES")
    print("-" * 92)
    print("1. Word participante")
    print("2. Word profesional")
    print("3. Word grupal")
    print("4. Excel individual")
    print("5. Excel global")
    print("\nMódulo pendiente de integración.")
    pause()


def configuration_menu() -> None:
    print_header()
    print("\nCONFIGURACIÓN")
    print("-" * 92)
    print(f"Raíz del proyecto : {ROOT}")
    print(f"Entrada            : {INPUT_DIR}")
    print(f"Salida             : {OUTPUT_DIR}")
    print(f"Resultados         : {RESULTS_DIR}")
    print(f"Documentación      : {DOCS_DIR}")
    print(f"Formatos admitidos : {', '.join(sorted(SUPPORTED_FORMATS))}")
    pause()


def audit_project() -> None:
    print_header()
    print("\nAUDITORÍA DEL PROYECTO")
    print("-" * 92)

    checks: Dict[str, bool] = {
        "Carpeta data/input": INPUT_DIR.exists(),
        "Carpeta data/output": OUTPUT_DIR.exists(),
        "Carpeta results": RESULTS_DIR.exists(),
        "Carpeta docs": DOCS_DIR.exists(),
        "Archivo README.md": (ROOT / "README.md").exists(),
        "Archivo project.yml": (ROOT / "project.yml").exists(),
        "Archivo mkdocs.yml": (ROOT / "mkdocs.yml").exists(),
        "Archivo CITATION.cff": (ROOT / "CITATION.cff").exists(),
        "Archivo requirements.txt": (ROOT / "requirements.txt").exists(),
    }

    for item, ok in checks.items():
        print(f"{item:<34} {'OK' if ok else 'FALTA'}")

    print("-" * 92)
    print(f"Archivos de entrada detectados: {len(find_input_files())}")

    print("\nESTADO DE MÓDULOS")
    for name, status in MODULES.items():
        print(f"{name:<38} {status}")

    pause()


def main_menu() -> None:
    actions: Dict[str, Callable[[], None]] = {
        "1": import_data_menu,
        "2": base_maestra_menu,
        "3": quality_control_menu,
        "4": participants_menu,
        "5": analysis_menu,
        "6": dashboards_menu,
        "7": reports_menu,
        "8": configuration_menu,
        "9": audit_project,
    }

    while True:
        clear_screen()
        print_header()
        print(
            "\n"
            "1. Importar datos\n"
            "2. Base maestra\n"
            "3. Depuración y control de calidad\n"
            "4. Selección de participantes\n"
            "5. Análisis clínico\n"
            "6. Dashboard\n"
            "7. Informes\n"
            "8. Configuración\n"
            "9. Auditoría del proyecto\n"
            "0. Salir\n"
        )

        option = input("Seleccione una opción: ").strip()

        if option == "0":
            print("\nPrograma finalizado.")
            return

        action = actions.get(option)
        if action is None:
            print("\nOpción no válida.")
            pause()
            continue

        action()


def main() -> int:
    try:
        create_project_folders()
        main_menu()
        return 0
    except KeyboardInterrupt:
        print("\n\nProceso cancelado por el usuario.")
        return 130
    except Exception as exc:
        print("\n[ERROR]")
        print(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
