# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Variables dictionary

All variables used by the platform are defined here.
"""

VARIABLES = {

    "participant": {
        "label": "Participant",
        "group": "Identification",
        "type": "text",
    },

    "date": {
        "label": "Date",
        "group": "Identification",
        "type": "date",
    },

    "site": {
        "label": "Site",
        "group": "Identification",
        "type": "text",
    },

    "moment": {
        "label": "Moment",
        "group": "Identification",
        "type": "text",
    },

    "sleep": {
        "label": "Sleep",
        "group": "Wellbeing",
        "unit": "1-10",
        "minimum": 1,
        "maximum": 10,
        "better": "higher",
        "pre_post": False,
        "longitudinal": True,
        "icbr": True,
    },

    "mood": {
        "label": "Mood",
        "group": "Wellbeing",
        "unit": "1-10",
        "minimum": 1,
        "maximum": 10,
        "better": "higher",
        "pre_post": True,
        "longitudinal": True,
        "icbr": True,
    },

    "stress": {
        "label": "Stress",
        "group": "Wellbeing",
        "unit": "1-10",
        "minimum": 1,
        "maximum": 10,
        "better": "lower",
        "pre_post": True,
        "longitudinal": True,
        "icbr": True,
    },

    "fatigue": {
        "label": "Fatigue",
        "group": "Wellbeing",
        "unit": "1-10",
        "minimum": 1,
        "maximum": 10,
        "better": "lower",
        "pre_post": True,
        "longitudinal": True,
        "icbr": True,
    },

    "upper_pain": {
        "label": "Upper Muscle Pain",
        "group": "Wellbeing",
        "unit": "1-10",
        "minimum": 1,
        "maximum": 10,
        "better": "lower",
        "pre_post": True,
        "longitudinal": True,
        "icbr": True,
    },

    "lower_pain": {
        "label": "Lower Muscle Pain",
        "group": "Wellbeing",
        "unit": "1-10",
        "minimum": 1,
        "maximum": 10,
        "better": "lower",
        "pre_post": True,
        "longitudinal": True,
        "icbr": True,
    },

    "sbp": {
        "label": "Systolic Blood Pressure",
        "group": "Health",
        "unit": "mmHg",
        "minimum": 70,
        "maximum": 250,
        "better": "lower",
        "pre_post": True,
        "longitudinal": True,
        "alert": 135,
    },

    "dbp": {
        "label": "Diastolic Blood Pressure",
        "group": "Health",
        "unit": "mmHg",
        "minimum": 40,
        "maximum": 150,
        "better": "lower",
        "pre_post": True,
        "longitudinal": True,
        "alert": 85,
    },

    "spo2": {
        "label": "Oxygen Saturation",
        "group": "Health",
        "unit": "%",
        "minimum": 70,
        "maximum": 100,
        "better": "higher",
        "pre_post": True,
        "longitudinal": True,
        "alert": 94,
    },

    "lifestyle": {
        "label": "Lifestyle",
        "group": "Health",
        "unit": "1-10",
        "minimum": 1,
        "maximum": 10,
        "better": "higher",
        "pre_post": False,
        "longitudinal": True,
    },

    "injury": {
        "label": "Injury",
        "group": "Context",
        "type": "text",
    },

    "injury_type": {
        "label": "Injury Type",
        "group": "Context",
        "type": "text",
    },

    "alcohol": {
        "label": "Alcohol",
        "group": "Context",
        "type": "text",
    },

    "illness": {
        "label": "Illness",
        "group": "Context",
        "type": "text",
    },

    "observations": {
        "label": "Observations",
        "group": "Context",
        "type": "text",
    },

}

ICBR_RECOVERY = [
    "sleep",
    "mood",
]

ICBR_LOAD = [
    "stress",
    "fatigue",
]

ICBR_PAIN = [
    "upper_pain",
    "lower_pain",
]


def get_variable(name):

    return VARIABLES.get(name)


def wellbeing_variables():

    return {

        k: v

        for k, v in VARIABLES.items()

        if v.get("group") == "Wellbeing"

    }


def health_variables():

    return {

        k: v

        for k, v in VARIABLES.items()

        if v.get("group") == "Health"

    }


def context_variables():

    return {

        k: v

        for k, v in VARIABLES.items()

        if v.get("group") == "Context"

    }


if __name__ == "__main__":

    print()

    print("=" * 80)

    print("VARIABLE DICTIONARY")

    print("=" * 80)

    print(f"Total variables : {len(VARIABLES)}")

    print(f"Wellbeing       : {len(wellbeing_variables())}")

    print(f"Health          : {len(health_variables())}")

    print(f"Context         : {len(context_variables())}")
