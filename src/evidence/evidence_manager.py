# -*- coding: utf-8 -*-

from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[2]

CURRENT = ROOT / "evidence" / "current"


def load_manifest():

    with open(
        CURRENT / "manifest.json",
        encoding="utf-8-sig"
    ) as f:

        return json.load(f)


def load_variables():

    with open(
        CURRENT / "variables.json",
        encoding="utf-8-sig"
    ) as f:

        return json.load(f)


def load_bibliography():

    with open(
        CURRENT / "bibliography.json",
        encoding="utf-8-sig"
    ) as f:

        return json.load(f)


def get_variable(name):

    variables = load_variables()

    return variables.get(name.upper())


def get_version():

    return load_manifest()["version"]
