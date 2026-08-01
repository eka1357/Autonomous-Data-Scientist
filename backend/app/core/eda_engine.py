import os
from typing import Any
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server environment
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


def compute_eda_statistics_and_charts(
    df: pd.DataFrame, dataset_id: str, output_charts_dir: str
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    """
    Computes comprehensive EDA statistics, correlation matrices, IQR outliers,
    and renders visualization charts saved to disk.
    """
    os.makedirs(output_charts_dir, exist_ok=True)

    rows, cols = len(df), len(df.columns)
    dup_count = int(df.duplicated().sum())
    missing_dict = {col: int(df[col].isna().sum()) for col in df.columns}
    dtypes_dict = {col: str(df[col].dtype) for col in df.columns}

    # 1. Numeric Statistics
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_stats: dict[str, Any] = {}
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) == 0:
            continue
        col_mean = float(series.mean())
        col_median = float(series.median())
        col_std = float(series.std()) if len(series) > 1 else 0.0
        col_var = float(series.var()) if len(series) > 1 else 0.0
        col_min = float(series.min())
        col_max = float(series.max())
        col_skew = float(stats.skew(series)) if len(series) > 2 else 0.0
        col_kurt = float(stats.kurtosis(series)) if len(series) > 3 else 0.0

        numeric_stats[col] = {
            "mean": round(col_mean, 4),
            "median": round(col_median, 4),
            "std": round(col_std, 4),
            "variance": round(col_var, 4),
            "min": round(col_min, 4),
            "max": round(col_max, 4),
            "skewness": round(col_skew, 4),
            "kurtosis": round(col_kurt, 4),
        }

    # 2. Categorical Statistics
    categorical_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
    categorical_stats: dict[str, Any] = {}
    for col in categorical_cols:
        series = df[col].dropna()
        unique_cnt = int(series.nunique())
        top_freqs = series.value_counts().head(5).to_dict()
        top_freqs_clean = {str(k): int(v) for k, v in top_freqs.items()}

        categorical_stats[col] = {
            "unique_count": unique_cnt,
            "top_frequencies": top_freqs_clean,
            "most_common": str(series.mode().iloc[0]) if not series.empty else None,
        }

    statistics = {
        "basic": {
            "row_count": rows,
            "column_count": cols,
            "duplicate_count": dup_count,
            "data_types": dtypes_dict,
            "missing_values": missing_dict,
        },
        "numeric": numeric_stats,
        "categorical": categorical_stats,
    }

    # 3. Correlation Matrix
    correlations: dict[str, Any] = {}
    if len(numeric_cols) >= 2:
        corr_df = df[numeric_cols].corr(method="pearson").fillna(0.0)
        correlations = {
            col: {c2: round(float(corr_df.loc[col, c2]), 4) for c2 in numeric_cols}
            for col in numeric_cols
        }

    # 4. Outlier Detection using IQR Method
    outliers: dict[str, Any] = {}
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) == 0:
            continue
        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outlier_mask = (series < lower_bound) | (series > upper_bound)
        outlier_count = int(outlier_mask.sum())
        outlier_pct = round((outlier_count / len(series)) * 100, 2)

        outliers[col] = {
            "q1": round(q1, 4),
            "q3": round(q3, 4),
            "iqr": round(iqr, 4),
            "lower_bound": round(lower_bound, 4),
            "upper_bound": round(upper_bound, 4),
            "outlier_count": outlier_count,
            "outlier_percentage": outlier_pct,
        }

    # 5. Visualizations Generation (Matplotlib)
    generated_charts: dict[str, str] = {}

    # A. Numeric Histograms & Boxplots
    for col in numeric_cols:
        series = df[col].dropna()
        if series.empty:
            continue

        # Histogram
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(series, bins=20, color="#3b82f6", edgecolor="#1e3a8a", alpha=0.8)
        ax.set_title(f"Distribution of {col}", fontsize=12, fontweight="bold")
        ax.set_xlabel(col)
        ax.set_ylabel("Frequency")
        ax.grid(True, linestyle="--", alpha=0.5)
        fig.tight_layout()
        hist_filename = f"hist_{col}.png"
        hist_path = os.path.join(output_charts_dir, hist_filename)
        fig.savefig(hist_path, dpi=100)
        plt.close(fig)
        generated_charts[f"hist_{col}"] = hist_filename

        # Boxplot
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.boxplot(series, vert=False, patch_artist=True, boxprops=dict(facecolor="#8b5cf6", color="#4c1d95"))
        ax.set_title(f"Box Plot of {col}", fontsize=12, fontweight="bold")
        ax.set_xlabel(col)
        ax.grid(True, linestyle="--", alpha=0.5)
        fig.tight_layout()
        box_filename = f"box_{col}.png"
        box_path = os.path.join(output_charts_dir, box_filename)
        fig.savefig(box_path, dpi=100)
        plt.close(fig)
        generated_charts[f"box_{col}"] = box_filename

    # B. Correlation Heatmap
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr().fillna(0.0).values
        fig, ax = plt.subplots(figsize=(7, 6))
        cax = ax.matshow(corr_matrix, cmap="coolwarm", vmin=-1, vmax=1)
        fig.colorbar(cax)
        ax.set_xticks(range(len(numeric_cols)))
        ax.set_yticks(range(len(numeric_cols)))
        ax.set_xticklabels(numeric_cols, rotation=45, ha="left")
        ax.set_yticklabels(numeric_cols)
        ax.set_title("Correlation Heatmap", fontsize=12, fontweight="bold", pad=20)
        fig.tight_layout()
        corr_filename = "corr_heatmap.png"
        corr_path = os.path.join(output_charts_dir, corr_filename)
        fig.savefig(corr_path, dpi=100)
        plt.close(fig)
        generated_charts["corr_heatmap"] = corr_filename

    # C. Missing Values Chart
    fig, ax = plt.subplots(figsize=(6, 4))
    cols_list = list(missing_dict.keys())
    missing_vals = [missing_dict[c] for c in cols_list]
    ax.bar(cols_list, missing_vals, color="#ef4444")
    ax.set_title("Missing Values per Column", fontsize=12, fontweight="bold")
    ax.set_ylabel("Count")
    ax.set_xticklabels(cols_list, rotation=45, ha="right")
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    missing_filename = "missing.png"
    missing_path = os.path.join(output_charts_dir, missing_filename)
    fig.savefig(missing_path, dpi=100)
    plt.close(fig)
    generated_charts["missing"] = missing_filename

    # D. Categorical Count Plots
    for col in categorical_cols[:5]:  # limit to top 5 categorical columns
        series = df[col].dropna().value_counts().head(10)
        if series.empty:
            continue
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(series.index.astype(str), series.values, color="#10b981")
        ax.set_title(f"Top Values for {col}", fontsize=12, fontweight="bold")
        ax.set_xlabel(col)
        ax.set_ylabel("Count")
        ax.set_xticklabels(series.index.astype(str), rotation=45, ha="right")
        ax.grid(True, linestyle="--", alpha=0.5)
        fig.tight_layout()
        cat_filename = f"cat_{col}.png"
        cat_path = os.path.join(output_charts_dir, cat_filename)
        fig.savefig(cat_path, dpi=100)
        plt.close(fig)
        generated_charts[f"cat_{col}"] = cat_filename

    return statistics, correlations, outliers, generated_charts
