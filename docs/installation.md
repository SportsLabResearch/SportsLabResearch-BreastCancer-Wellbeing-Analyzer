# Installation

## Requirements

- Windows, macOS or Linux
- Python 3.11 or later
- Git

## Download

```bash
git clone https://github.com/SportsLabResearch/SportsLabResearch-BreastCancer-Wellbeing-Analyzer.git
cd SportsLabResearch-BreastCancer-Wellbeing-Analyzer
```

## Install dependencies

```bash
python -m pip install -r requirements.txt
```

On Windows PowerShell, `py` can be used instead of `python`:

```powershell
py -m pip install -r requirements.txt
```

## Verify the project

```powershell
py -m py_compile main.py
```

## Build this documentation

```powershell
py -m pip install mkdocs-material
py -m mkdocs serve
```

Open `http://127.0.0.1:8000/`.
