# -*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime
import json

ROOT = Path(__file__).resolve().parents[2]

CURRENT = ROOT / "evidence" / "current"

MANIFEST = CURRENT / "manifest.json"


def update_required():

    with open(MANIFEST,encoding="utf-8") as f:

        manifest=json.load(f)

    last=datetime.strptime(
        manifest["last_update"],
        "%Y-%m-%d"
    )

    return (
        datetime.now()-last
    ).days>=30


def update():

    if update_required():

        print(
            "Scientific evidence update required."
        )

    else:

        print(
            "Scientific evidence is up to date."
        )
