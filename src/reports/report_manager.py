# -*- coding: utf-8 -*-

"""
Gestor automático de informes por participante.

Genera:
- Informe_PRE_ID_Nombre.docx
- Informe_PRE_ID_Nombre.xlsx
- Informe_POST_ID_Nombre.docx
- Informe_POST_ID_Nombre.xlsx
- Informe_PRE_POST_ID_Nombre.docx
- Informe_PRE_POST_ID_Nombre.xlsx
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.core.session import get_current_participant
from src.reports.excel_exporter import export_participant_excel
from src.reports.report_generator import (
    REPORT_MODE_POST,
    REPORT_MODE_PRE,
    REPORT_MODE_PRE_POST,
    filter_records_for_report,
    generate_participant_report,
    safe_filename,
)


def _participant_filename() -> str:
    """Devuelve ID_Nombre para utilizarlo en los archivos."""

    participant: dict[str, Any] = get_current_participant() or {
        "participant_id": "sin_id",
        "name": "Participante",
    }

    participant_id = safe_filename(
        participant.get("participant_id", "sin_id")
    )

    participant_name = safe_filename(
        participant.get("name", "Participante")
    )

    return f"{participant_id}_{participant_name}"


def _rename_excel(
    generated_path: Path,
    report_mode: str,
) -> Path:
    """Renombra el Excel generado con el mismo nombre base que el Word."""

    final_name = (
        f"Informe_{report_mode}_{_participant_filename()}.xlsx"
    )

    final_path = generated_path.parent / final_name

    if final_path.exists():
        final_path.unlink()

    generated_path.replace(final_path)

    return final_path


def _generate_excel(
    records: pd.DataFrame,
    output_dir: Path,
    report_mode: str,
) -> Path:
    """Genera y renombra el Excel correspondiente."""

    generated_path = export_participant_excel(
        records=records,
        output_dir=output_dir,
        include_graphs=False,
    )

    return _rename_excel(
        generated_path=generated_path,
        report_mode=report_mode,
    )


def generate_all_participant_reports(
    records: pd.DataFrame,
    output_dir: Path | str | None = None,
) -> dict[str, Path]:
    """
    Genera automáticamente los seis archivos de una participante.
    """

    if records is None or records.empty:
        raise ValueError(
            "No hay registros disponibles para generar los informes."
        )

    generated: dict[str, Path] = {}

    pre_records = filter_records_for_report(
        records=records,
        report_mode=REPORT_MODE_PRE,
    )

    post_records = filter_records_for_report(
        records=records,
        report_mode=REPORT_MODE_POST,
    )

    pre_word = generate_participant_report(
        records=records,
        output_dir=output_dir,
        report_mode=REPORT_MODE_PRE,
    )

    participant_folder = pre_word.parent

    pre_excel = _generate_excel(
        records=pre_records,
        output_dir=participant_folder,
        report_mode=REPORT_MODE_PRE,
    )

    generated["pre_word"] = pre_word
    generated["pre_excel"] = pre_excel

    post_word = generate_participant_report(
        records=records,
        output_dir=participant_folder,
        report_mode=REPORT_MODE_POST,
    )

    post_excel = _generate_excel(
        records=post_records,
        output_dir=participant_folder,
        report_mode=REPORT_MODE_POST,
    )

    generated["post_word"] = post_word
    generated["post_excel"] = post_excel

    pre_post_word = generate_participant_report(
        records=records,
        output_dir=participant_folder,
        report_mode=REPORT_MODE_PRE_POST,
    )

    pre_post_excel = _generate_excel(
        records=records,
        output_dir=participant_folder,
        report_mode=REPORT_MODE_PRE_POST,
    )

    generated["pre_post_word"] = pre_post_word
    generated["pre_post_excel"] = pre_post_excel

    return generated


def print_generated_reports(
    generated: dict[str, Path],
) -> None:
    """Muestra los archivos generados."""

    print()
    print("=" * 80)
    print("INFORMES GENERADOS CORRECTAMENTE")
    print("=" * 80)

    order = (
        "pre_word",
        "pre_excel",
        "post_word",
        "post_excel",
        "pre_post_word",
        "pre_post_excel",
    )

    for key in order:
        path = generated.get(key)

        if path is not None:
            print(f"  {path}")

    print("=" * 80)
