# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Global project configuration.
"""

from pathlib import Path

# -----------------------------------------------------------------------------
# PROJECT
# -----------------------------------------------------------------------------

PROJECT_NAME = "SportsLabResearch-BreastCancer-Wellbeing-Analyzer"

VERSION = "0.1.0-alpha"

AUTHOR = "José Pino-Ortega"

ORGANIZATION = "SportsLabResearch"

DESCRIPTION = (
    "Scientific software for the multidimensional assessment and "
    "longitudinal monitoring of wellbeing and health-related outcomes "
    "in women with breast cancer."
)

# -----------------------------------------------------------------------------
# FOLDERS
# -----------------------------------------------------------------------------

ROOT = Path(".")

DATA = ROOT / "data"

INPUT = DATA / "input"

OUTPUT = DATA / "output"

RESULTS = ROOT / "results"

DOCS = ROOT / "docs"

DOCUMENTS = ROOT / "documents"

ASSETS = ROOT / "assets"

# -----------------------------------------------------------------------------
# INPUT DATA
# -----------------------------------------------------------------------------

SUPPORTED_FORMATS = [
    ".xlsx",
    ".xls",
    ".csv"
]

# -----------------------------------------------------------------------------
# TARGET POPULATION
# -----------------------------------------------------------------------------

PRIMARY_POPULATION = "Women with breast cancer"

ALLOW_OTHER_POPULATIONS = True

# -----------------------------------------------------------------------------
# MODULES
# -----------------------------------------------------------------------------

ENABLE_ICBR = True

ENABLE_BLOOD_PRESSURE = True

ENABLE_SPO2 = True

ENABLE_LONGITUDINAL = True

ENABLE_PRE_POST = True

ENABLE_WORD = True

ENABLE_EXCEL = True

ENABLE_DASHBOARD = True

# -----------------------------------------------------------------------------
# CLINICAL THRESHOLDS
# -----------------------------------------------------------------------------

HOME_SBP = 135

HOME_DBP = 85

SPO2_WARNING = 94

SPO2_CRITICAL = 90

# -----------------------------------------------------------------------------
# REPORTS
# -----------------------------------------------------------------------------

GENERATE_WORD = True

GENERATE_EXCEL = True

GENERATE_DASHBOARD = True

# -----------------------------------------------------------------------------
# END
# -----------------------------------------------------------------------------
