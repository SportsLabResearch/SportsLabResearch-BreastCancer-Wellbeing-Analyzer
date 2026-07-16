# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Path Manager
"""

from __future__ import annotations

from pathlib import Path

import yaml


CONFIG_FILE = Path("config/paths.yml")


class PathManager:

    def __init__(self):

        self.config = self.load()

    def load(self):

        if not CONFIG_FILE.exists():

            return {

                "input_paths": [

                    "data/input",

                ]

            }

        with open(

            CONFIG_FILE,

            encoding="utf-8",

        ) as f:

            return yaml.safe_load(f)

    @property
    def input_paths(self):

        return [

            Path(path)

            for path in self.config.get(

                "input_paths",

                [],

            )

        ]


if __name__ == "__main__":

    manager = PathManager()

    print()

    print("=" * 80)

    print("CONFIGURED INPUT PATHS")

    print("=" * 80)

    for path in manager.input_paths:

        print(path)

