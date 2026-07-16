# -*- coding: utf-8 -*-

"""
SportsLabResearch-BreastCancer-Wellbeing-Analyzer

Statistical Engine
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except Exception:
    SCIPY_AVAILABLE = False


def clean_numeric(values: Iterable) -> pd.Series:
    return pd.to_numeric(pd.Series(values), errors="coerce").dropna().astype(float)


def descriptive_statistics(values: Iterable) -> Dict[str, float]:
    series = clean_numeric(values)

    if series.empty:
        return {
            "n": 0,
            "mean": np.nan,
            "median": np.nan,
            "sd": np.nan,
            "variance": np.nan,
            "minimum": np.nan,
            "maximum": np.nan,
            "p25": np.nan,
            "p75": np.nan,
            "iqr": np.nan,
            "cv_percent": np.nan,
        }

    mean_value = float(series.mean())
    sd_value = float(series.std(ddof=1)) if len(series) > 1 else np.nan

    return {
        "n": int(series.count()),
        "mean": mean_value,
        "median": float(series.median()),
        "sd": sd_value,
        "variance": float(series.var(ddof=1)) if len(series) > 1 else np.nan,
        "minimum": float(series.min()),
        "maximum": float(series.max()),
        "p25": float(series.quantile(0.25)),
        "p75": float(series.quantile(0.75)),
        "iqr": float(series.quantile(0.75) - series.quantile(0.25)),
        "cv_percent": (
            float(sd_value / mean_value * 100)
            if pd.notna(sd_value) and mean_value != 0
            else np.nan
        ),
    }


def shapiro_test(values: Iterable) -> Dict[str, float | str]:
    series = clean_numeric(values)

    if not SCIPY_AVAILABLE or len(series) < 3:
        return {
            "test": "Shapiro-Wilk",
            "n": int(len(series)),
            "statistic": np.nan,
            "p": np.nan,
            "normal": "No evaluable",
        }

    sample = series.iloc[:5000]
    statistic, p_value = stats.shapiro(sample)

    return {
        "test": "Shapiro-Wilk",
        "n": int(len(sample)),
        "statistic": float(statistic),
        "p": float(p_value),
        "normal": "Sí" if p_value >= 0.05 else "No",
    }


def confidence_interval_mean(
    values: Iterable,
    confidence: float = 0.95,
) -> Tuple[float, float]:
    series = clean_numeric(values)

    if not SCIPY_AVAILABLE or len(series) < 2:
        return np.nan, np.nan

    mean_value = float(series.mean())
    standard_error = float(stats.sem(series))
    critical = float(stats.t.ppf((1 + confidence) / 2, len(series) - 1))
    margin = critical * standard_error

    return mean_value - margin, mean_value + margin


def cohen_d_independent(group_a: Iterable, group_b: Iterable) -> float:
    a = clean_numeric(group_a)
    b = clean_numeric(group_b)

    if len(a) < 2 or len(b) < 2:
        return np.nan

    pooled_variance = (
        ((len(a) - 1) * a.var(ddof=1))
        + ((len(b) - 1) * b.var(ddof=1))
    ) / (len(a) + len(b) - 2)

    if pooled_variance <= 0:
        return np.nan

    return float((a.mean() - b.mean()) / math.sqrt(pooled_variance))


def cohen_dz(before: Iterable, after: Iterable) -> float:
    paired = pd.DataFrame({
        "before": pd.to_numeric(pd.Series(before), errors="coerce"),
        "after": pd.to_numeric(pd.Series(after), errors="coerce"),
    }).dropna()

    if len(paired) < 2:
        return np.nan

    differences = paired["after"] - paired["before"]
    sd_difference = differences.std(ddof=1)

    if sd_difference == 0 or pd.isna(sd_difference):
        return np.nan

    return float(differences.mean() / sd_difference)


def hedges_g(group_a: Iterable, group_b: Iterable) -> float:
    d_value = cohen_d_independent(group_a, group_b)

    a = clean_numeric(group_a)
    b = clean_numeric(group_b)

    if pd.isna(d_value):
        return np.nan

    degrees_freedom = len(a) + len(b) - 2

    if degrees_freedom <= 1:
        return np.nan

    correction = 1 - (3 / (4 * degrees_freedom - 1))

    return float(d_value * correction)


def paired_comparison(before: Iterable, after: Iterable) -> Dict[str, float | str]:
    paired = pd.DataFrame({
        "before": pd.to_numeric(pd.Series(before), errors="coerce"),
        "after": pd.to_numeric(pd.Series(after), errors="coerce"),
    }).dropna()

    if paired.empty:
        return {
            "test": "No calculada",
            "n": 0,
            "before_mean": np.nan,
            "after_mean": np.nan,
            "delta": np.nan,
            "ci95_low": np.nan,
            "ci95_high": np.nan,
            "statistic": np.nan,
            "p": np.nan,
            "cohen_dz": np.nan,
        }

    differences = paired["after"] - paired["before"]
    normality = shapiro_test(differences)

    test_name = "No calculada"
    statistic = np.nan
    p_value = np.nan

    if SCIPY_AVAILABLE and len(paired) >= 3:
        try:
            if normality["normal"] == "Sí":
                statistic, p_value = stats.ttest_rel(
                    paired["after"],
                    paired["before"],
                    nan_policy="omit",
                )
                test_name = "t pareada"
            else:
                statistic, p_value = stats.wilcoxon(
                    paired["after"],
                    paired["before"],
                )
                test_name = "Wilcoxon"
        except Exception:
            pass

    ci_low, ci_high = confidence_interval_mean(differences)

    return {
        "test": test_name,
        "n": int(len(paired)),
        "before_mean": float(paired["before"].mean()),
        "after_mean": float(paired["after"].mean()),
        "delta": float(differences.mean()),
        "ci95_low": ci_low,
        "ci95_high": ci_high,
        "statistic": float(statistic) if pd.notna(statistic) else np.nan,
        "p": float(p_value) if pd.notna(p_value) else np.nan,
        "cohen_dz": cohen_dz(paired["before"], paired["after"]),
    }


def independent_comparison(
    group_a: Iterable,
    group_b: Iterable,
) -> Dict[str, float | str]:
    a = clean_numeric(group_a)
    b = clean_numeric(group_b)

    if len(a) < 2 or len(b) < 2:
        return {
            "test": "No calculada",
            "n_a": int(len(a)),
            "n_b": int(len(b)),
            "mean_a": np.nan,
            "mean_b": np.nan,
            "statistic": np.nan,
            "p": np.nan,
            "cohen_d": np.nan,
            "hedges_g": np.nan,
        }

    normal_a = shapiro_test(a)
    normal_b = shapiro_test(b)

    test_name = "No calculada"
    statistic = np.nan
    p_value = np.nan

    if SCIPY_AVAILABLE:
        try:
            if normal_a["normal"] == "Sí" and normal_b["normal"] == "Sí":
                statistic, p_value = stats.ttest_ind(
                    a,
                    b,
                    equal_var=False,
                    nan_policy="omit",
                )
                test_name = "t independiente de Welch"
            else:
                statistic, p_value = stats.mannwhitneyu(
                    a,
                    b,
                    alternative="two-sided",
                )
                test_name = "Mann-Whitney"
        except Exception:
            pass

    return {
        "test": test_name,
        "n_a": int(len(a)),
        "n_b": int(len(b)),
        "mean_a": float(a.mean()),
        "mean_b": float(b.mean()),
        "statistic": float(statistic) if pd.notna(statistic) else np.nan,
        "p": float(p_value) if pd.notna(p_value) else np.nan,
        "cohen_d": cohen_d_independent(a, b),
        "hedges_g": hedges_g(a, b),
    }


def smallest_worthwhile_change(
    baseline_values: Iterable,
    multiplier: float = 0.2,
) -> float:
    series = clean_numeric(baseline_values)

    if len(series) < 2:
        return np.nan

    return float(multiplier * series.std(ddof=1))


def responder_analysis(
    before: Iterable,
    after: Iterable,
    favourable_direction: int,
    swc: float = np.nan,
    mcid: float = np.nan,
) -> Dict[str, float | int]:
    paired = pd.DataFrame({
        "before": pd.to_numeric(pd.Series(before), errors="coerce"),
        "after": pd.to_numeric(pd.Series(after), errors="coerce"),
    }).dropna()

    if paired.empty:
        return {
            "n": 0,
            "swc_responders_n": 0,
            "swc_responders_percent": np.nan,
            "mcid_responders_n": 0,
            "mcid_responders_percent": np.nan,
        }

    change = (paired["after"] - paired["before"]) * favourable_direction
    n = len(change)

    swc_n = int((change >= swc).sum()) if pd.notna(swc) else 0
    mcid_n = int((change >= mcid).sum()) if pd.notna(mcid) else 0

    return {
        "n": int(n),
        "swc_responders_n": swc_n,
        "swc_responders_percent": swc_n / n * 100 if pd.notna(swc) else np.nan,
        "mcid_responders_n": mcid_n,
        "mcid_responders_percent": mcid_n / n * 100 if pd.notna(mcid) else np.nan,
    }


def linear_regression(
    x_values: Iterable,
    y_values: Iterable,
) -> Dict[str, float | int | str]:
    data = pd.DataFrame({
        "x": pd.to_numeric(pd.Series(x_values), errors="coerce"),
        "y": pd.to_numeric(pd.Series(y_values), errors="coerce"),
    }).dropna()

    if len(data) < 2:
        return {
            "n": int(len(data)),
            "slope": np.nan,
            "intercept": np.nan,
            "r_squared": np.nan,
            "p": np.nan,
            "equation": "No calculable",
        }

    if SCIPY_AVAILABLE:
        result = stats.linregress(data["x"], data["y"])

        return {
            "n": int(len(data)),
            "slope": float(result.slope),
            "intercept": float(result.intercept),
            "r_squared": float(result.rvalue ** 2),
            "p": float(result.pvalue),
            "equation": f"y = {result.intercept:.3f} + {result.slope:.3f}x",
        }

    slope, intercept = np.polyfit(data["x"], data["y"], 1)
    predicted = intercept + slope * data["x"]
    ss_res = float(((data["y"] - predicted) ** 2).sum())
    ss_tot = float(((data["y"] - data["y"].mean()) ** 2).sum())
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan

    return {
        "n": int(len(data)),
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": float(r_squared),
        "p": np.nan,
        "equation": f"y = {intercept:.3f} + {slope:.3f}x",
    }


def correlation(
    x_values: Iterable,
    y_values: Iterable,
    method: str = "pearson",
) -> Dict[str, float | int | str]:
    data = pd.DataFrame({
        "x": pd.to_numeric(pd.Series(x_values), errors="coerce"),
        "y": pd.to_numeric(pd.Series(y_values), errors="coerce"),
    }).dropna()

    if len(data) < 3 or not SCIPY_AVAILABLE:
        return {
            "method": method,
            "n": int(len(data)),
            "coefficient": np.nan,
            "p": np.nan,
        }

    if method.lower() == "spearman":
        coefficient, p_value = stats.spearmanr(data["x"], data["y"])
        test_name = "Spearman"
    else:
        coefficient, p_value = stats.pearsonr(data["x"], data["y"])
        test_name = "Pearson"

    return {
        "method": test_name,
        "n": int(len(data)),
        "coefficient": float(coefficient),
        "p": float(p_value),
    }


if __name__ == "__main__":
    before = [120, 125, 130, 128, 122]
    after = [118, 121, 126, 124, 120]

    print("=" * 80)
    print("STATISTICAL ENGINE")
    print("=" * 80)
    print(descriptive_statistics(before))
    print(paired_comparison(before, after))
    print(linear_regression(range(len(before)), before))
    print(correlation(before, after, method="pearson"))
