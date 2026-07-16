# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Core project information.
"""

from src.config.project_config import *

def print_header():

    print("=" * 80)
    print(PROJECT_NAME)
    print("=" * 80)
    print(f"Version      : {VERSION}")
    print(f"Organization : {ORGANIZATION}")
    print(f"Author       : {AUTHOR}")
    print(f"Population   : {PRIMARY_POPULATION}")
    print("=" * 80)
    print("Modules")
    print("-" * 80)

    print(f"ICBR-M..................... {ENABLE_ICBR}")
    print(f"Blood Pressure............. {ENABLE_BLOOD_PRESSURE}")
    print(f"SpO2....................... {ENABLE_SPO2}")
    print(f"Longitudinal............... {ENABLE_LONGITUDINAL}")
    print(f"PRE / POST................. {ENABLE_PRE_POST}")
    print(f"Word Reports............... {GENERATE_WORD}")
    print(f"Excel Reports.............. {GENERATE_EXCEL}")
    print(f"Clinical Dashboard......... {GENERATE_DASHBOARD}")

    print("=" * 80)


if __name__ == "__main__":
    print_header()

