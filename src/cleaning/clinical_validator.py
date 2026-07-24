# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Clinical Data Validator
"""

from __future__ import annotations

import pandas as pd

from src.config.variable_mapping import prepare_form_dataframe
from src.cleaning.clinical_cleaning import clean_clinical_data


RULES = {

    "hr": (30,220),

    "rmssd": (1,300),

    "ln_rmssd": (0,10),

    "sbp": (70,250),

    "dbp": (40,150),

    "spo2": (70,100),

    "sleep": (1,10),

    "mood": (1,5),

    "stress": (1,10),

    "fatigue": (1,10),

    "upper_pain": (1,10),

    "lower_pain": (1,10),

}


def validate_dataframe(df: pd.DataFrame):

    df = prepare_form_dataframe(df)
    df = clean_clinical_data(df)

    report=[]

    for variable,(minimum,maximum) in RULES.items():

        if variable not in df.columns:
            continue

        values=pd.to_numeric(df[variable],errors="coerce")

        total=int(values.notna().sum())

        below=int((values<minimum).sum())

        above=int((values>maximum).sum())

        valid=total-below-above

        report.append({

            "variable":variable,

            "total":total,

            "valid":valid,

            "below":below,

            "above":above,

            "availability_%":round(total/len(df)*100,1),

            "valid_%":round(valid/max(total,1)*100,1),

        })

    return pd.DataFrame(report)


def print_report(df):

    report=validate_dataframe(df)

    print()

    print("="*92)

    print("VALIDACIÓN CLÍNICA")

    print("="*92)

    print(f"{'Variable':<22}"
          f"{'Datos':>8}"
          f"{'Válidos':>10}"
          f"{'<Min':>8}"
          f"{'>Max':>8}"
          f"{'Disp.%':>10}"
          f"{'OK.%':>10}")

    print("-"*92)

    for _,r in report.iterrows():

        print(f"{r.variable:<22}"
              f"{int(r.total):>8}"
              f"{int(r.valid):>10}"
              f"{int(r.below):>8}"
              f"{int(r.above):>8}"
              f"{r['availability_%']:>9.1f}%"
              f"{r['valid_%']:>9.1f}%")

    return report


if __name__=="__main__":

    from src.connectors.form_source_connector import load_latest_source

    _,df=load_latest_source(include_drive=False)

    print_report(df)



