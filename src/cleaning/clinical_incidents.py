# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Clinical Incident Detector
"""

from __future__ import annotations

import pandas as pd


def detect_incidents(df: pd.DataFrame):

    incidents=[]

    def add(level,variable,row,value,message):

        incidents.append({

            "level":level,

            "variable":variable,

            "row":int(row),

            "value":value,

            "message":message,

        })

    if "hr" in df.columns:

        hr=pd.to_numeric(df["hr"],errors="coerce")

        rr=pd.to_numeric(df.get("mean_rr"),errors="coerce")

        for i,v in hr.items():

            if pd.isna(v):
                continue

            if v<30:
                add("ERROR","hr",i,v,"Frecuencia cardiaca inferior a 30 lpm")

            elif v>220:
                add("ERROR","hr",i,v,"Frecuencia cardiaca superior a 220 lpm")

            elif (
                v > 220
                and pd.notna(rr.loc[i])
                and rr.loc[i] > 220
                and abs(v - rr.loc[i]) < 5
            ):

                add(
                    "ERROR",
                    "hr",
                    i,
                    v,
                    "Posible intercambio HR ↔ Mean RR",
                )

    if "rmssd" in df.columns:

        rmssd=pd.to_numeric(df["rmssd"],errors="coerce")

        for i,v in rmssd.items():

            if pd.isna(v):
                continue

            if v<=0:

                add(
                    "ERROR",
                    "rmssd",
                    i,
                    v,
                    "RMSSD no válido",
                )

            elif v>300:

                add(
                    "WARNING",
                    "rmssd",
                    i,
                    v,
                    "RMSSD extremadamente elevado",
                )

    return pd.DataFrame(incidents)


def print_incidents(df):

    incidents=detect_incidents(df)

    print()
    print("="*92)
    print("INCIDENCIAS CLÍNICAS")
    print("="*92)

    if incidents.empty:

        print("No se detectaron incidencias.")

        return incidents

    print(
        incidents
        .groupby(["level","variable"])
        .size()
        .rename("casos")
        .to_string()
    )

    print()
    print("-"*92)

    print(
        incidents
        .head(25)
        .to_string(index=False)
    )

    return incidents


if __name__=="__main__":

    from src.connectors.form_source_connector import load_latest_source

    _,df=load_latest_source(include_drive=False)

    print_incidents(df)


