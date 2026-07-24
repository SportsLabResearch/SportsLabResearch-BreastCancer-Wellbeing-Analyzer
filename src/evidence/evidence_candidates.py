# -*- coding: utf-8 -*-

"""
Registro y gestión de publicaciones científicas candidatas.

SportsLabResearch-BreastCancer-Wellbeing-Analyzer
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "evidence"
UPDATES_DIR = EVIDENCE_DIR / "updates"

VALID_STATUSES = {
    "candidate",
    "reviewed",
    "approved",
    "rejected",
}


def ensure_updates_folder() -> None:
    UPDATES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def get_candidates_path(
    search_date: str | None = None,
) -> Path:
    date_text = search_date or datetime.now().strftime(
        "%Y-%m-%d"
    )

    return (
        UPDATES_DIR
        / f"candidates_{date_text}.json"
    )


def load_candidates(
    search_date: str | None = None,
) -> list[dict[str, Any]]:
    path = get_candidates_path(search_date)

    if not path.exists():
        return []

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "El archivo de candidatas debe contener una lista."
        )

    return data


def save_candidates(
    candidates: list[dict[str, Any]],
    search_date: str | None = None,
) -> Path:
    ensure_updates_folder()

    path = get_candidates_path(search_date)

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            candidates,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return path


def normalize_doi(value: object) -> str:
    text = str(value or "").strip().lower()

    prefixes = (
        "https://doi.org/",
        "http://doi.org/",
        "doi:",
    )

    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):]

    return text.strip()


def candidate_exists(
    candidates: list[dict[str, Any]],
    doi: str,
) -> bool:
    normalized_doi = normalize_doi(doi)

    if not normalized_doi:
        return False

    return any(
        normalize_doi(
            candidate.get("doi")
        ) == normalized_doi
        for candidate in candidates
    )


def create_candidate(
    *,
    title: str,
    doi: str = "",
    authors: str = "",
    journal: str = "",
    year: int | None = None,
    abstract: str = "",
    source: str = "",
    population: str = "",
    variables: list[str] | None = None,
    study_type: str = "",
    keywords: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "candidate_id": (
            datetime.now().strftime(
                "%Y%m%d%H%M%S%f"
            )
        ),
        "title": str(title).strip(),
        "doi": normalize_doi(doi),
        "authors": str(authors).strip(),
        "journal": str(journal).strip(),
        "year": year,
        "abstract": str(abstract).strip(),
        "source": str(source).strip(),
        "population": str(population).strip(),
        "variables": variables or [],
        "study_type": str(study_type).strip(),
        "keywords": keywords or [],
        "status": "candidate",
        "level_of_evidence": None,
        "clinical_message": "",
        "review_notes": "",
        "reviewed_by": "",
        "reviewed_date": None,
        "approved_by": "",
        "approved_date": None,
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        ),
    }


def add_candidate(
    candidate: dict[str, Any],
    search_date: str | None = None,
) -> tuple[bool, Path]:
    candidates = load_candidates(search_date)

    doi = normalize_doi(
        candidate.get("doi")
    )

    if doi and candidate_exists(
        candidates,
        doi,
    ):
        return False, get_candidates_path(
            search_date
        )

    candidates.append(candidate)

    path = save_candidates(
        candidates,
        search_date,
    )

    return True, path


def update_candidate_status(
    candidate_id: str,
    new_status: str,
    *,
    reviewer: str = "",
    notes: str = "",
    level_of_evidence: str | None = None,
    clinical_message: str = "",
    search_date: str | None = None,
) -> bool:
    if new_status not in VALID_STATUSES:
        raise ValueError(
            "Estado no válido: "
            + new_status
        )

    candidates = load_candidates(
        search_date
    )

    for candidate in candidates:
        if (
            candidate.get("candidate_id")
            != candidate_id
        ):
            continue

        candidate["status"] = new_status
        candidate["review_notes"] = notes

        if level_of_evidence is not None:
            candidate[
                "level_of_evidence"
            ] = level_of_evidence

        if clinical_message:
            candidate[
                "clinical_message"
            ] = clinical_message

        current_date = datetime.now().isoformat(
            timespec="seconds"
        )

        if new_status == "reviewed":
            candidate["reviewed_by"] = reviewer
            candidate["reviewed_date"] = current_date

        elif new_status == "approved":
            candidate["approved_by"] = reviewer
            candidate["approved_date"] = current_date

        save_candidates(
            candidates,
            search_date,
        )

        return True

    return False


def get_candidates_summary(
    search_date: str | None = None,
) -> dict[str, int]:
    candidates = load_candidates(
        search_date
    )

    summary = {
        "total": len(candidates),
        "candidate": 0,
        "reviewed": 0,
        "approved": 0,
        "rejected": 0,
    }

    for candidate in candidates:
        status = candidate.get(
            "status",
            "candidate",
        )

        if status in summary:
            summary[status] += 1

    return summary


def print_candidates_summary(
    search_date: str | None = None,
) -> None:
    summary = get_candidates_summary(
        search_date
    )

    print()
    print("PUBLICACIONES CANDIDATAS")
    print("-" * 92)
    print(f"Total      : {summary['total']}")
    print(f"Candidatas : {summary['candidate']}")
    print(f"Revisadas  : {summary['reviewed']}")
    print(f"Aprobadas  : {summary['approved']}")
    print(f"Rechazadas : {summary['rejected']}")
