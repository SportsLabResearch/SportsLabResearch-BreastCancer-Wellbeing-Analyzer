# -*- coding: utf-8 -*-

"""
Genera automáticamente tres informes Word:

1. PRE
2. POST
3. PRE-POST
"""

from __future__ import annotations

import sys

from main import (
    ID_COLUMN,
    NAME_COLUMN,
    SITE_COLUMN,
    prepare_dataframe,
)
from src.core.session import set_current_participant
from src.reports.report_generator import (
    REPORT_MODE_POST,
    REPORT_MODE_PRE,
    REPORT_MODE_PRE_POST,
    generate_participant_report,
)


def most_frequent_value(dataframe, column: str, default: str) -> str:

    if column not in dataframe.columns:
        return default

    values = (
        dataframe[column]
        .dropna()
        .astype(str)
        .str.strip()
    )

    values = values[values != ""]

    if values.empty:
        return default

    return str(values.value_counts().index[0])


def main() -> int:

    print("=" * 92)
    print("GENERACIÓN DE INFORMES PRE, POST Y PRE-POST")
    print("=" * 92)

    participant_id = input(
        "\nIntroduzca el identificador de la participante: "
    ).strip()

    if not participant_id:
        print("\nNo se ha introducido ningún identificador.")
        return 1

    try:
        dataframe = prepare_dataframe()
    except Exception as exc:
        print("\n[ERROR AL CARGAR LOS DATOS]")
        print(str(exc))
        return 1

    records = dataframe[
        dataframe[ID_COLUMN].astype(str).str.strip()
        == participant_id
    ].copy()

    if records.empty:
        print(
            f"\nNo se encontraron registros para "
            f"el identificador {participant_id}."
        )
        return 1

    participant_name = most_frequent_value(
        records,
        NAME_COLUMN,
        "Participante",
    )

    participant_site = most_frequent_value(
        records,
        SITE_COLUMN,
        "No disponible",
    )

    set_current_participant(
        participant_id=participant_id,
        name=participant_name,
        site=participant_site,
        dataframe=records,
    )

    print()
    print("PARTICIPANTE")
    print("-" * 92)
    print(f"Identificador : {participant_id}")
    print(f"Nombre        : {participant_name}")
    print(f"Sede          : {participant_site}")
    print(f"Registros     : {len(records)}")

    modes = (
        ("PRE", REPORT_MODE_PRE),
        ("POST", REPORT_MODE_POST),
        ("PRE-POST", REPORT_MODE_PRE_POST),
    )

    generated = []
    errors = []

    for label, mode in modes:

        print()
        print(f"Generando informe {label}...")

        try:
            output_path = generate_participant_report(
                records=records,
                report_mode=mode,
            )

            generated.append(
                (label, output_path)
            )

            print(f"Correcto: {output_path}")

        except Exception as exc:

            errors.append(
                (label, str(exc))
            )

            print(f"[ERROR {label}]")
            print(str(exc))

    print()
    print("=" * 92)
    print("RESULTADO FINAL")
    print("=" * 92)

    if generated:

        print("\nINFORMES GENERADOS")

        for label, output_path in generated:
            print(f"{label:<10}: {output_path}")

    if errors:

        print("\nINFORMES NO GENERADOS")

        for label, error in errors:
            print(f"{label:<10}: {error}")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
