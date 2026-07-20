---
hide:
  - toc
---

# BreastCancer Wellbeing Analyzer

[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?logo=github)](https://github.com/SportsLabResearch/SportsLabResearch-BreastCancer-Wellbeing-Analyzer)
[![Release](https://img.shields.io/github/v/release/SportsLabResearch/SportsLabResearch-BreastCancer-Wellbeing-Analyzer)](https://github.com/SportsLabResearch/SportsLabResearch-BreastCancer-Wellbeing-Analyzer/releases)
[![Zenodo](https://img.shields.io/badge/Zenodo-DOI-1682D4?logo=zenodo)](https://zenodo.org/search?q=SportsLabResearch-BreastCancer-Wellbeing-Analyzer)

Scientific software for importing, organizing and analysing longitudinal wellbeing data in women with breast cancer.

<div class="hero-actions" markdown>
[GitHub](https://github.com/SportsLabResearch/SportsLabResearch-BreastCancer-Wellbeing-Analyzer){ .md-button .md-button--primary }
[Documentation](https://sportslabresearch.github.io/SportsLabResearch-BreastCancer-Wellbeing-Analyzer/){ .md-button }
[Zenodo](https://zenodo.org/search?q=SportsLabResearch-BreastCancer-Wellbeing-Analyzer){ .md-button }
</div>

## Main features

<div class="grid cards" markdown>

-   **Questionnaire data**

    Reads local Excel, CSV and TXT exports produced from Google Forms or synchronized through Google Drive.

-   **Quality control**

    Organizes records, cleans column names and excludes invalid or duplicated output files.

-   **Wellbeing analysis**

    Supports longitudinal analysis of wellbeing indicators collected by the project questionnaire.

-   **Scientific outputs**

    Provides a reproducible basis for Excel and Word reports, tables and figures.

</div>

## Workflow

```mermaid
flowchart LR
    A[Google Forms] --> B[Excel / CSV export]
    B --> C[Automatic source detection]
    C --> D[Data cleaning]
    D --> E[Wellbeing analysis]
    E --> F[Excel and Word reports]
```

## Scope

The software is intended for research and monitoring workflows. It does not replace clinical assessment, diagnosis or medical decision-making.
