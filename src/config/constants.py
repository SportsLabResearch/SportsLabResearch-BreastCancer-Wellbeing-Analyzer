# -*- coding: utf-8 -*-

"""
Clinical and analytical constants.
"""

WELLBEING_VARIABLES = {
    "sleep": "Sueño",
    "mood": "Mood / Estado de ánimo",
    "stress": "Estrés",
    "fatigue": "Fatiga",
    "upper_pain": "Dolor muscular superior",
    "lower_pain": "Dolor muscular inferior",
}

HEALTH_VARIABLES = {
    "sbp": "Presión arterial sistólica",
    "dbp": "Presión arterial diastólica",
    "spo2": "Saturación de oxígeno",
    "lifestyle": "Estilo de vida",
}

CONTEXT_VARIABLES = {
    "injury": "Lesión",
    "injury_type": "Tipo de lesión",
    "alcohol": "Alcohol",
    "illness": "Enfermedad",
    "observations": "Observaciones",
}

ICBR_NEGATIVE_VARIABLES = {
    "Estrés",
    "Fatiga",
    "Dolor muscular superior",
    "Dolor muscular inferior",
}

ICBR_WEIGHTS = {
    "ICBR-R": {
        "name": "Recuperación",
        "variables": {
            "Sueño": 0.4335,
            "Mood / Estado de ánimo": 0.7983,
        },
    },
    "ICBR-CP": {
        "name": "Carga percibida",
        "variables": {
            "Estrés": 0.6744,
            "Fatiga": 0.9853,
        },
    },
    "ICBR-D": {
        "name": "Dolor",
        "variables": {
            "Dolor muscular superior": 0.7484,
            "Dolor muscular inferior": 0.9244,
        },
    },
}

PRE_POST_VARIABLES = {
    "sbp",
    "dbp",
    "spo2",
    "mood",
    "stress",
    "fatigue",
    "upper_pain",
    "lower_pain",
}

LONGITUDINAL_VARIABLES = set(WELLBEING_VARIABLES) | set(HEALTH_VARIABLES)

HOME_SBP_THRESHOLD = 135
HOME_DBP_THRESHOLD = 85

SPO2_WARNING_THRESHOLD = 94
SPO2_CRITICAL_THRESHOLD = 90
