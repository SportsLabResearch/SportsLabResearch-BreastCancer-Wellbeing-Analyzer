# -*- coding: utf-8 -*-

from __future__ import annotations

import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Callable, Dict, List

import pandas as pd

from src.cleaning.names import clean_name
from src.cleaning.clinical_validator import print_report
from src.cleaning.clinical_incidents import print_incidents
from src.analysis.clinical_summary import print_clinical_summary
from src.analysis.blood_pressure import analyse as analyse_blood_pressure
from src.analysis.wellbeing import analyse as analyse_wellbeing
from src.analysis.moment_menu import moment_analysis_menu
from src.core.session import set_current_participant
from src.core.session import has_active_participant, get_current_dataframe, get_current_participant
from src.config.variable_mapping import prepare_form_dataframe
from src.cleaning.clinical_cleaning import clean_clinical_data
from src.config.path_manager import PathManager
from src.connectors.form_source_connector import load_latest_source
from src.database.master_database import MasterDatabase
from src.reports.report_manager import (
    generate_all_participant_reports,
    print_generated_reports,
)


PROJECT_NAME = "SportsLabResearch-BreastCancer-Wellbeing-Analyzer"
VERSION = "1.0.0"
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

SITE_COLUMN = "site"
NAME_COLUMN = "participant"
ID_COLUMN = "participant_id"


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
    manager = PathManager()
    files: List[Path] = []

    for configured_path in manager.input_paths:
        folder = (
            configured_path
            if configured_path.is_absolute()
            else ROOT / configured_path
        )

        if not folder.exists() or not folder.is_dir():
            continue

        files.extend(
            path
            for path in folder.iterdir()
            if path.is_file()
            and path.suffix.lower() in SUPPORTED_FORMATS
            and not path.name.startswith("~$")
        )

    return sorted(
        set(files),
        key=lambda path: (path.name.lower(), str(path)),
    )


def load_input_dataframe() -> pd.DataFrame:
    database = MasterDatabase()

    if database.exists():
        dataframe = database.load()

        if not dataframe.empty:
            return dataframe

    source_file, dataframe = load_latest_source(
        include_drive=True
    )

    if dataframe.empty:
        raise ValueError(
            f"El archivo no contiene registros: {source_file}"
        )

    return dataframe


def normalize_site_name(value: object) -> str:
    if pd.isna(value):
        return ""

    site = str(value).strip()

    replacements = {
        "Espinardo, Carpa, Universidad de Murcia":
            "Espinardo. Carpa. Universidad de Murcia",
    }

    return replacements.get(site, site)


def normalize_identifier(value: object) -> str:
    if pd.isna(value):
        return ""

    text = str(value).strip()

    if text.endswith(".0"):
        text = text[:-2]

    return text


def prepare_dataframe() -> pd.DataFrame:
    dataframe = load_input_dataframe().copy()

    required = {
        SITE_COLUMN,
        NAME_COLUMN,
        ID_COLUMN,
    }

    missing = required.difference(dataframe.columns)

    if missing:
        raise KeyError(
            "Faltan columnas obligatorias: "
            + ", ".join(sorted(missing))
        )

    dataframe[SITE_COLUMN] = dataframe[SITE_COLUMN].apply(
        normalize_site_name
    )

    dataframe[NAME_COLUMN] = (
        dataframe[NAME_COLUMN]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    dataframe[ID_COLUMN] = dataframe[ID_COLUMN].apply(
        normalize_identifier
    )

    return dataframe


def get_sites() -> pd.Series:
    dataframe = prepare_dataframe()

    sites = dataframe[SITE_COLUMN]
    sites = sites[sites != ""]

    return sites.value_counts()


def select_site() -> str | None:
    while True:
        print_header()
        print("\nSELECCIONE LA SEDE")
        print("-" * 92)

        try:
            sites = get_sites()
        except Exception as exc:
            print(f"\n[ERROR] {exc}")
            pause()
            return None

        if sites.empty:
            print("\nNo se han encontrado sedes.")
            pause()
            return None

        site_names = list(sites.index)

        for index, site in enumerate(site_names, start=1):
            print(
                f"{index}. {site} "
                f"({int(sites[site])} registros)"
            )

        print("0. Volver")

        option = input("\nSeleccione una opción: ").strip()

        if option == "0":
            return None

        if not option.isdigit():
            print("\nOpción no válida.")
            pause()
            continue

        selected_index = int(option) - 1

        if selected_index < 0 or selected_index >= len(site_names):
            print("\nOpción no válida.")
            pause()
            continue

        return site_names[selected_index]


def most_frequent_name(series: pd.Series) -> str:
    names = (
        series
        .dropna()
        .astype(str)
        .str.strip()
    )

    names = names[names != ""]

    if names.empty:
        return "Sin nombre"

    return names.value_counts().index[0]


def build_participant_dictionary(
    dataframe: pd.DataFrame,
) -> Dict[str, str]:

    valid = dataframe[
        dataframe[ID_COLUMN].str.fullmatch(r"\d+")
    ].copy()

    participants: Dict[str, str] = (
        valid
        .groupby(ID_COLUMN)[NAME_COLUMN]
        .agg(most_frequent_name)
        .to_dict()
    )

    invalid = dataframe[
        ~dataframe[ID_COLUMN].str.fullmatch(r"\d+")
    ].copy()

    if not participants:
        return {}

    for _, row in invalid.iterrows():
        name = str(row[NAME_COLUMN]).strip()

        if not name:
            continue

        best_identifier, best_name = max(
            participants.items(),
            key=lambda item: SequenceMatcher(
                None,
                clean_name(name),
                clean_name(item[1]),
            ).ratio(),
        )

        similarity = SequenceMatcher(
            None,
            clean_name(name),
            clean_name(best_name),
        ).ratio()

        if similarity >= 0.70:
            dataframe.loc[
                dataframe.index == row.name,
                ID_COLUMN,
            ] = best_identifier

    return participants


def get_participants_by_site(
    site: str,
) -> tuple[Dict[str, str], pd.DataFrame]:

    dataframe = prepare_dataframe()

    participant_sites = (
        dataframe.dropna(
            subset=[NAME_COLUMN, SITE_COLUMN]
        )
        .groupby(NAME_COLUMN)[SITE_COLUMN]
        .agg(
            lambda values: values.value_counts().index[0]
        )
        .to_dict()
    )

    dataframe["_primary_site"] = dataframe[
        NAME_COLUMN
    ].map(participant_sites)

    site_dataframe = dataframe[
        dataframe["_primary_site"] == site
    ].copy()

    site_dataframe.drop(
        columns=["_primary_site"],
        inplace=True,
    )

    participants = build_participant_dictionary(
        site_dataframe
    )

    return participants, site_dataframe


def select_one_participant(site: str | None = None) -> pd.DataFrame | None:
    if site is None:
        site = select_site()

    if site is None:
        return

    participants, site_dataframe = get_participants_by_site(
        site
    )

    if not participants:
        print("\nNo se encontraron participantes válidas.")
        pause()
        return

    participant_items = sorted(
        participants.items(),
        key=lambda item: int(item[0]),
    )

    while True:
        print_header()
        print(f"\nSEDE: {site}")
        print("-" * 92)
        print(
            f"PARTICIPANTES DISPONIBLES "
            f"({len(participant_items)})"
        )
        print("-" * 92)

        for index, (identifier, name) in enumerate(
            participant_items,
            start=1,
        ):
            records = int(
                (
                    site_dataframe[ID_COLUMN]
                    == identifier
                ).sum()
            )

            print(
                f"{index:>3}. "
                f"{identifier:<6} "
                f"{name} "
                f"({records} registros)"
            )

        print("  0. Volver")

        option = input(
            "\nSeleccione una participante: "
        ).strip()

        if option == "0":
            return

        if not option.isdigit():
            print("\nOpción no válida.")
            pause()
            continue

        selected_index = int(option) - 1

        if (
            selected_index < 0
            or selected_index >= len(participant_items)
        ):
            print("\nOpción no válida.")
            pause()
            continue

        identifier, name = participant_items[selected_index]

        records = site_dataframe[
            site_dataframe[ID_COLUMN] == identifier
        ].copy()

        dates = pd.to_datetime(
            records.get("date"),
            errors="coerce",
            dayfirst=True,
        )

        first_date = (
            dates.min().strftime("%d/%m/%Y")
            if dates.notna().any()
            else "No disponible"
        )

        last_date = (
            dates.max().strftime("%d/%m/%Y")
            if dates.notna().any()
            else "No disponible"
        )

        availability = {
            "Frecuencia cardiaca":
                "hr",
            "HRV - RMSSD":
                "rmssd",
            "Presión arterial sistólica":
                "Presión sistólica",
            "Presión arterial diastólica":
                "Presión distólica",
            "Saturación de oxígeno":
                "Saturación de oxígeno",
            "Sueño":
                "Sueño",
            "Estrés":
                "Estrés",
            "fatigue":
                "fatigue",
            "upper_pain":
                "upper_pain",
            "lower_pain":
                "lower_pain",
        }

        print("\nFICHA DE LA PARTICIPANTE")
        print("=" * 92)
        print(f"Identificador   : {identifier}")
        print(f"Nombre          : {name}")
        print(f"Sede            : {site}")
        print(f"Registros       : {len(records)}")
        print(f"Primer registro : {first_date}")
        print(f"Último registro : {last_date}")

        print("\nDISPONIBILIDAD DE DATOS")
        print("-" * 92)

        for label, column in availability.items():
            count = (
                int(records[column].notna().sum())
                if column in records.columns
                else 0
            )

            status = "Disponible" if count > 0 else "No disponible"

            print(
                f"{label:<34} "
                f"{status:<15} "
                f"({count} registros)"
            )

        clinical_data = prepare_form_dataframe(records)
        clinical_data = clean_clinical_data(clinical_data)

        summary_variables = {
            "FC media": "hr",
            "RMSSD media": "rmssd",
            "LnRMSSD media": "ln_rmssd",
            "PAS media": "sbp",
            "PAD media": "dbp",
            "SpO2 media": "spo2",
            "Sueño medio": "sleep",
            "Mood medio": "mood",
            "Estrés medio": "stress",
            "Fatiga media": "fatigue",
            "Dolor superior medio": "upper_pain",
            "Dolor inferior medio": "lower_pain",
        }

        print("\nRESUMEN CLÃNICO RÃPIDO")
        print("-" * 92)

        for label, column in summary_variables.items():
            if column not in clinical_data.columns:
                print(f"{label:<30} No disponible")
                continue

            values = pd.to_numeric(
                clinical_data[column],
                errors="coerce",
            ).dropna()

            if values.empty:
                print(f"{label:<30} No disponible")
            else:
                print(
                    f"{label:<30} "
                    f"{values.mean():.2f} "
                    f"(n={len(values)})"
                )

        evolution_columns = [
            "date",
            "hr",
            "rmssd",
            "ln_rmssd",
            "sbp",
            "dbp",
            "sleep",
            "stress",
            "fatigue",
        ]

        available_columns = [
            column
            for column in evolution_columns
            if column in clinical_data.columns
        ]

        if "date" in available_columns:
            evolution = clinical_data[
                available_columns
            ].copy()

            evolution["date"] = pd.to_datetime(
                evolution["date"],
                errors="coerce",
                dayfirst=True,
            )

            evolution = evolution[
                evolution["date"].notna()
            ].sort_values("date")

            if not evolution.empty:
                evolution["date"] = evolution[
                    "date"
                ].dt.strftime("%d/%m/%Y")

                evolution = evolution.rename(
                    columns={
                        "date": "Fecha",
                        "hr": "FC",
                        "rmssd": "rmssd",
                        "ln_rmssd": "LnRMSSD",
                        "sbp": "PAS",
                        "dbp": "PAD",
                        "sleep": "Sueño",
                        "stress": "Estrés",
                        "fatigue": "fatigue",
                    }
                )

                print("\nEVOLUCIÓN TEMPORAL")
                print("-" * 92)
                print(
                    evolution.tail(20).to_string(
                        index=False,
                        na_rep="-",
                    )
                )
            else:
                print("\nEVOLUCIÓN TEMPORAL")
                print("-" * 92)
                print("No hay fechas válidas disponibles.")

        set_current_participant(
            participant_id=identifier,
            name=name,
            site=site,
            dataframe=records,
        )

        return records


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
        print(
            f"{index:>3}. {file.name} "
            f"({size_kb:.1f} KB)"
        )


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

        option = input(
            "Seleccione una opcion: "
        ).strip()

        if option == "1":
            show_input_files()
            pause()

        elif option == "4":
            try:
                source_file, dataframe = load_latest_source(
                    include_drive=True
                )

                print()
                print("=" * 92)
                print("DATOS DE GOOGLE FORMS CARGADOS")
                print("=" * 92)
                print(f"Archivo   : {source_file}")
                print(f"Registros : {len(dataframe)}")
                print(f"Columnas  : {len(dataframe.columns)}")

            except Exception as exc:
                print()
                print("[ERROR AL CARGAR GOOGLE FORMS]")
                print(str(exc))

            pause()

        elif option in {"2", "3"}:
            print(
                "\nM?dulo preparado para integraci?n "
                "en la siguiente fase."
            )
            pause()

        elif option == "0":
            return

        else:
            print("\nOpci?n no v?lida.")
            pause()

def base_maestra_menu() -> None:
    while True:
        print_header()
        print("\nBASE MAESTRA")
        print("-" * 92)
        print("1. Actualizar base maestra")
        print("2. Ver estado de la base")
        print("0. Volver")

        option = input(
            "\nSeleccione una opcion: "
        ).strip()

        if option == "1":
            try:
                source_file, dataframe = load_latest_source(
                    include_drive=True
                )

                database = MasterDatabase()
                result = database.update(dataframe)

                print()
                print("=" * 92)
                print("BASE MAESTRA ACTUALIZADA")
                print("=" * 92)
                print(f"Archivo origen      : {source_file}")
                print(f"Registros leidos    : {len(dataframe)}")
                print(f"Registros nuevos    : {result['new_records']}")
                print(f"Total base maestra  : {result['total_records']}")

            except Exception as exc:
                print()
                print("[ERROR AL ACTUALIZAR LA BASE MAESTRA]")
                print(str(exc))

            pause()

        elif option == "2":
            database = MasterDatabase()

            print()
            print("=" * 92)
            print("ESTADO DE LA BASE MAESTRA")
            print("=" * 92)

            if database.exists():
                dataframe = database.load()
                print(f"Registros : {len(dataframe)}")
                print(f"Columnas  : {len(dataframe.columns)}")
            else:
                print("La base maestra todav?a no existe.")

            pause()

        elif option == "0":
            return

        else:
            print("\nOpcion no valida.")
            pause()

def quality_control_menu() -> None:
    while True:
        print_header()
        print("\nDEPURACIÓN Y CONTROL DE CALIDAD")
        print("-" * 92)
        print("1. Validación clínica")
        print("2. Incidencias clínicas")
        print("0. Volver")

        option = input("\nSeleccione una opción: ").strip()

        if option == "1":
            dataframe = prepare_dataframe()
            print_report(dataframe)
            pause()

        elif option == "2":
            dataframe = prepare_dataframe()
            dataframe = prepare_form_dataframe(dataframe)
            dataframe = clean_clinical_data(dataframe)
            print_incidents(dataframe)
            pause()

        elif option == "0":
            return

        else:
            print("\nOpción no válida.")
            pause()


def participants_menu() -> None:
    while True:
        print_header()
        print("\nSELECCIÓN DE PARTICIPANTES")
        print("-" * 92)
        print("1. Seleccionar sede y participante")
        print("2. Seleccionar una participante")
        print("0. Volver")

        option = input(
            "\nSeleccione una opción: "
        ).strip()

        if option == "1":
            site = select_site()

            if site:
                select_one_participant(site)

        elif option == "2":
            select_one_participant()

        elif option == "0":
            return

        else:
            print("\nOpción no válida.")
            pause()


def get_active_or_select_participant() -> pd.DataFrame | None:
    if has_active_participant():
        participant = get_current_participant()
        dataframe = get_current_dataframe()

        print()
        print("PARTICIPANTE ACTIVA")
        print("-" * 92)
        print(
            f"{participant['participant_id']} - "
            f"{participant['name']}"
        )
        print(participant["site"])

        return dataframe

    return select_one_participant()

def analysis_menu() -> None:
    while True:
        print_header()
        print("\nANÃLISIS CLÃNICO")
        print("-" * 92)
        print("1. Resumen clínico de una participante")
        print("2. Bienestar")
        print("3. Presión arterial")
        print("4. Momento de registro: PRE, POST y efecto")
        print("0. Volver")

        option = input("\nSeleccione una opción: ").strip()

        if option == "1":
            records = get_active_or_select_participant()

            if records is None or records.empty:
                continue

            clinical_data = prepare_form_dataframe(records)
            clinical_data = clean_clinical_data(clinical_data)
            print_clinical_summary(clinical_data)
            pause()

        elif option == "2":
            records = get_active_or_select_participant()

            if records is None or records.empty:
                continue

            clinical_data = prepare_form_dataframe(records)
            clinical_data = clean_clinical_data(clinical_data)
            results = analyse_wellbeing(clinical_data)

            print()
            print("=" * 92)
            print("ANÃLISIS DE BIENESTAR")
            print("=" * 92)

            if results.empty:
                print("No hay datos de bienestar disponibles.")
            else:
                print(results.to_string(index=False))

            pause()

        elif option == "3":
            records = get_active_or_select_participant()

            if records is None or records.empty:
                continue

            clinical_data = prepare_form_dataframe(records)
            clinical_data = clean_clinical_data(clinical_data)
            results = analyse_blood_pressure(clinical_data)

            summary = results["summary"]
            descriptive = results["descriptive"]
            alerts = results["alerts"]

            print()
            print("=" * 92)
            print("ANÃLISIS DE PRESIÃ“N ARTERIAL")
            print("=" * 92)
            print(f"Registros totales : {summary['records']}")
            print(f"PAS válidas       : {summary['valid_sbp']}")
            print(f"PAD válidas       : {summary['valid_dbp']}")
            print(f"PAS media         : {summary['sbp_mean']:.2f} mmHg")
            print(f"PAD media         : {summary['dbp_mean']:.2f} mmHg")
            print(f"Clasificación     : {summary['classification']}")
            print(f"Interpretación    : {summary['interpretation']}")

            print()
            print("-" * 92)
            print(descriptive.to_string(index=False))

            print()
            print(f"Alertas detectadas: {len(alerts)}")
            pause()

        elif option == "4":
            records = get_active_or_select_participant()

            if records is None or records.empty:
                continue

            moment_analysis_menu(records)

        elif option == "0":
            return

        else:
            print("\nOpción no válida.")
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



def select_report_date_range(
    records: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Timestamp | None, pd.Timestamp | None]:
    """
    Permite seleccionar una fecha, un intervalo o todas las fechas.
    """

    if "date" not in records.columns:
        print()
        print("No existe una columna de fecha.")
        print("Se utilizar?n todos los registros.")
        return records.copy(), None, None

    dates = pd.to_datetime(
        records["date"],
        errors="coerce",
        dayfirst=True,
    ).dt.normalize()

    valid_dates = sorted(
        dates.dropna().unique()
    )

    if not valid_dates:
        print()
        print("No hay fechas v?lidas disponibles.")
        print("Se utilizar?n todos los registros.")
        return records.copy(), None, None

    while True:
        print()
        print("SELECCI?N DE FECHAS")
        print("-" * 92)
        print("1. Seleccionar una fecha")
        print("2. Seleccionar un intervalo")
        print("3. Utilizar todas las fechas")
        print("0. Volver")

        option = input(
            "\nSeleccione una opci?n: "
        ).strip()

        if option == "0":
            return pd.DataFrame(), None, None

        if option == "3":
            return records.copy(), None, None

        if option not in {"1", "2"}:
            print()
            print("Opci?n no v?lida.")
            continue

        print()
        print("FECHAS DISPONIBLES")
        print("-" * 92)

        for index, date_value in enumerate(
            valid_dates,
            start=1,
        ):
            date_timestamp = pd.Timestamp(date_value)

            count = int(
                (dates == date_timestamp).sum()
            )

            print(
                f"{index:>3}. "
                f"{date_timestamp.strftime('%d/%m/%Y')} "
                f"({count} registros)"
            )

        if option == "1":
            while True:
                selected = input(
                    "\nSeleccione el n?mero de fecha: "
                ).strip()

                if not selected.isdigit():
                    print("Opci?n no v?lida.")
                    continue

                selected_index = int(selected) - 1

                if (
                    selected_index < 0
                    or selected_index >= len(valid_dates)
                ):
                    print("Opci?n no v?lida.")
                    continue

                selected_date = pd.Timestamp(
                    valid_dates[selected_index]
                )

                mask = (
                    dates.notna()
                    & (dates == selected_date)
                )

                filtered_records = records.loc[mask].copy()

                print()
                print("FECHA SELECCIONADA")
                print("-" * 92)
                print(
                    selected_date.strftime("%d/%m/%Y")
                )
                print(
                    f"Registros: {len(filtered_records)}"
                )

                return (
                    filtered_records,
                    selected_date,
                    selected_date,
                )

        if option == "2":
            while True:
                start_option = input(
                    "\nN?mero de fecha inicial: "
                ).strip()

                if not start_option.isdigit():
                    print("Opci?n no v?lida.")
                    continue

                start_index = int(start_option) - 1

                if (
                    start_index < 0
                    or start_index >= len(valid_dates)
                ):
                    print("Opci?n no v?lida.")
                    continue

                start_date = pd.Timestamp(
                    valid_dates[start_index]
                )

                break

            while True:
                end_option = input(
                    "N?mero de fecha final: "
                ).strip()

                if not end_option.isdigit():
                    print("Opci?n no v?lida.")
                    continue

                end_index = int(end_option) - 1

                if (
                    end_index < 0
                    or end_index >= len(valid_dates)
                ):
                    print("Opci?n no v?lida.")
                    continue

                end_date = pd.Timestamp(
                    valid_dates[end_index]
                )

                if end_date < start_date:
                    print(
                        "La fecha final no puede ser anterior "
                        "a la fecha inicial."
                    )
                    continue

                break

            mask = (
                dates.notna()
                & (dates >= start_date)
                & (dates <= end_date)
            )

            filtered_records = records.loc[mask].copy()

            print()
            print("INTERVALO SELECCIONADO")
            print("-" * 92)
            print(
                "Fecha inicial : "
                f"{start_date.strftime('%d/%m/%Y')}"
            )
            print(
                "Fecha final   : "
                f"{end_date.strftime('%d/%m/%Y')}"
            )
            print(
                f"Registros     : {len(filtered_records)}"
            )

            return (
                filtered_records,
                start_date,
                end_date,
            )


def select_report_mode() -> str | None:
    """Pregunta qué tipo de informe desea generar."""

    while True:
        print_header()
        print("\nTIPO DE INFORME CLÍNICO")
        print("-" * 92)
        print("1. Estado PRE")
        print("   Analiza únicamente los registros anteriores a la sesión.")
        print()
        print("2. Estado POST")
        print("   Analiza únicamente los registros posteriores a la sesión.")
        print()
        print("3. Efecto PRE–POST")
        print("   Analiza la variación pareada entre PRE y POST.")
        print()
        print("0. Volver")

        option = input("\nSeleccione una opción: ").strip()

        modes = {
            "1": "PRE",
            "2": "POST",
            "3": "PRE_POST",
        }

        if option == "0":
            return None

        if option in modes:
            return modes[option]

        print("\nOpción no válida.")
        pause()


def reports_menu() -> None:
    while True:
        print_header()
        print()
        print("INFORMES")
        print("-" * 92)
        print("1. Generar informes completos de la participante")
        print("   Word y Excel: PRE, POST y PRE-POST")
        print("0. Volver")

        option = input(
            "\nSeleccione una opci?n: "
        ).strip()

        if option == "1":
            records = get_active_or_select_participant()

            if records is None or records.empty:
                continue

            report_records, start_date, end_date = (
                select_report_date_range(records)
            )

            if report_records is None or report_records.empty:
                print()
                print("No hay registros seleccionados.")
                pause()
                continue

            try:
                print()
                print("GENERANDO INFORMES")
                print("-" * 92)

                generated = generate_all_participant_reports(
                    records=report_records
                )

                print_generated_reports(generated)

                if start_date is None and end_date is None:
                    print("Periodo: todas las fechas")
                elif start_date == end_date:
                    print(
                        "Fecha seleccionada: "
                        f"{start_date.strftime('%d/%m/%Y')}"
                    )
                else:
                    print(
                        "Periodo seleccionado: "
                        f"{start_date.strftime('%d/%m/%Y')} - "
                        f"{end_date.strftime('%d/%m/%Y')}"
                    )

            except Exception as exc:
                print()
                print("[ERROR AL GENERAR LOS INFORMES]")
                print(str(exc))

            pause()

        elif option == "0":
            return

        else:
            print()
            print("Opci?n no v?lida.")
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
    print(
        "Formatos admitidos : "
        + ", ".join(sorted(SUPPORTED_FORMATS))
    )
    pause()


def audit_project() -> None:
    print_header()
    print("\nAUDITORÃA DEL PROYECTO")
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
        "Archivo requirements.txt":
            (ROOT / "requirements.txt").exists(),
    }

    for item, ok in checks.items():
        print(
            f"{item:<34} "
            f"{'OK' if ok else 'FALTA'}"
        )

    print("-" * 92)
    print(
        "Archivos de entrada detectados: "
        f"{len(find_input_files())}"
    )

    pause()


def update_database_on_startup() -> None:
    print_header()
    print()
    print("ACTUALIZANDO DATOS AUTOMATICAMENTE")
    print("-" * 92)

    try:
        source_file, dataframe = load_latest_source(
            include_drive=True
        )

        database = MasterDatabase()
        result = database.update(dataframe)

        print(f"Archivo origen     : {source_file}")
        print(f"Registros leidos   : {len(dataframe)}")
        print(f"Registros nuevos   : {result['new_records']}")
        print(f"Total registros    : {result['total_records']}")
        print()
        print("Base de datos actualizada correctamente.")

    except Exception as exc:
        print()
        print("[ERROR AL ACTUALIZAR LOS DATOS]")
        print(str(exc))
        print()
        print(
            "El programa intentara continuar con la "
            "base maestra existente."
        )

        database = MasterDatabase()

        if not database.exists():
            raise


def main_menu() -> None:
    actions: Dict[str, Callable[[], None]] = {
        "1": quality_control_menu,
        "2": participants_menu,
        "3": analysis_menu,
        "4": reports_menu,
        "5": configuration_menu,
        "6": audit_project,
    }

    while True:
        clear_screen()
        print_header()

        print(
            "\n"
            "1. Depuración y control de calidad\n"
            "2. Selección de participantes\n"
            "3. Análisis clínico\n"
            "4. Informes\n"
            "5. Configuración\n"
            "6. Auditoría del proyecto\n"
            "0. Salir\n"
        )

        option = input(
            "Seleccione una opción: "
        ).strip()

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
        print(
            "\n\nProceso cancelado por el usuario."
        )
        return 130

    except Exception as exc:
        print("\n[ERROR]")
        print(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
