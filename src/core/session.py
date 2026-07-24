# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Sesión de trabajo activa.
"""

from __future__ import annotations

import pandas as pd


_current_participant: dict | None = None
_current_dataframe: pd.DataFrame | None = None


def set_current_participant(
    participant_id: str,
    name: str,
    site: str,
    dataframe: pd.DataFrame,
) -> None:
    global _current_participant
    global _current_dataframe

    _current_participant = {
        "participant_id": str(participant_id),
        "name": str(name),
        "site": str(site),
    }

    _current_dataframe = dataframe.copy()


def get_current_participant() -> dict | None:
    return _current_participant


def get_current_dataframe() -> pd.DataFrame | None:
    if _current_dataframe is None:
        return None

    return _current_dataframe.copy()


def clear_session() -> None:
    global _current_participant
    global _current_dataframe

    _current_participant = None
    _current_dataframe = None


def has_active_participant() -> bool:
    return (
        _current_participant is not None
        and _current_dataframe is not None
        and not _current_dataframe.empty
    )
