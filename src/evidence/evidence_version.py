# -*- coding: utf-8 -*-

"""
Gestión de versiones de la evidencia científica.

SportsLabResearch-BreastCancer-Wellbeing-Analyzer
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "evidence"
CURRENT_DIR = EVIDENCE_DIR / "current"
VERSIONS_DIR = EVIDENCE_DIR / "versions"
UPDATES_DIR = EVIDENCE_DIR / "updates"

MANIFEST_PATH = CURRENT_DIR / "manifest.json"


def load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"No existe el manifiesto científico: {MANIFEST_PATH}"
        )

    with MANIFEST_PATH.open(
        "r",
        encoding="utf-8-sig",
    ) as file:
        return json.load(file)


def save_manifest(
    manifest: dict[str, Any],
) -> None:
    CURRENT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with MANIFEST_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            manifest,
            file,
            ensure_ascii=False,
            indent=2,
        )


def get_evidence_version() -> str:
    manifest = load_manifest()

    return str(
        manifest.get(
            "evidence_version",
            "No disponible",
        )
    )


def get_evidence_summary() -> dict[str, Any]:
    manifest = load_manifest()

    return {
        "engine_name": manifest.get("engine_name"),
        "version": manifest.get("evidence_version"),
        "last_search": manifest.get("last_search"),
        "approval_date": manifest.get("approval_date"),
        "approved": manifest.get("approved", False),
        "status": manifest.get("status"),
        "publications_included": manifest.get(
            "publications_included",
            0,
        ),
        "update_interval_days": manifest.get(
            "update_interval_days",
            30,
        ),
    }


def update_is_due(
    today: date | None = None,
) -> bool:
    manifest = load_manifest()

    last_search_text = manifest.get("last_search")

    if not last_search_text:
        return True

    last_search = datetime.strptime(
        last_search_text,
        "%Y-%m-%d",
    ).date()

    interval_days = int(
        manifest.get(
            "update_interval_days",
            30,
        )
    )

    current_date = today or date.today()

    return (
        current_date - last_search
    ).days >= interval_days


def print_evidence_status() -> None:
    summary = get_evidence_summary()

    print()
    print("EVIDENCIA CIENTÍFICA")
    print("-" * 92)
    print(
        f"Motor               : {summary['engine_name']}"
    )
    print(
        f"Versión activa      : {summary['version']}"
    )
    print(
        f"Última búsqueda     : {summary['last_search']}"
    )
    print(
        f"Fecha de aprobación : {summary['approval_date']}"
    )
    print(
        f"Estado              : {summary['status']}"
    )
    print(
        "Aprobada            : "
        f"{'Sí' if summary['approved'] else 'No'}"
    )
    print(
        "Publicaciones       : "
        f"{summary['publications_included']}"
    )
    print(
        "Actualización       : "
        f"{'Pendiente' if update_is_due() else 'No necesaria'}"
    )
