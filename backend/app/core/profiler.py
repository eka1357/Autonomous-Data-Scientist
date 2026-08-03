import math
import re
from typing import Any
import numpy as np
import pandas as pd


def _sanitize_value(val: Any) -> Any:
    if val is None or pd.isna(val):
        return None
    if isinstance(val, (float, np.floating)):
        if math.isnan(val) or math.isinf(val):
            return None
        return float(val)
    if isinstance(val, (int, np.integer)):
        return int(val)
    return str(val)


def clean_and_coerce_numeric_columns(df: pd.DataFrame, coercion_threshold: float = 0.5) -> pd.DataFrame:
    """
    Strips currency symbols ($ € £ ¥ etc.), commas, and whitespace from object columns
    and attempts numeric coercion with pd.to_numeric(errors='coerce').
    Only keeps a column as numeric if coercion succeeds for at least coercion_threshold of values.
    """
    df_cleaned = df.copy()
    for col in df_cleaned.columns:
        col_series = df_cleaned[col]
        if pd.api.types.is_object_dtype(col_series) or isinstance(col_series.dtype, pd.CategoricalDtype):
            s_str = col_series.astype(str).str.strip()
            # Strip currency symbols $, €, £, ¥, and whitespace (leave commas and periods)
            cleaned_s = s_str.str.replace(r"[\$£€¥\s]", "", regex=True)

            def parse_euro_num(val):
                if pd.isna(val) or val == "": return val
                val = str(val)
                if "," in val and "." in val:
                    if val.rfind(",") > val.rfind("."):
                        val = val.replace(".", "").replace(",", ".")
                    else:
                        val = val.replace(",", "")
                elif "," in val and "." not in val:
                    parts = val.split(",")
                    if len(parts) == 2 and len(parts[1]) in (1, 2):
                        val = val.replace(",", ".")
                    else:
                        val = val.replace(",", "")
                return val

            cleaned_s = cleaned_s.apply(parse_euro_num)
            numeric_s = pd.to_numeric(cleaned_s, errors="coerce")

            # Count valid original entries (excluding nulls / empty / nan representations)
            valid_orig_mask = col_series.notna() & (~s_str.isin(["", "nan", "None", "null", "NaN", "N/A", "n/a"]))
            valid_orig_count = int(valid_orig_mask.sum())

            if valid_orig_count > 0:
                coerced_count = int(numeric_s[valid_orig_mask].notna().sum())
                if (coerced_count / valid_orig_count) >= coercion_threshold:
                    df_cleaned[col] = numeric_s
    return df_cleaned


def profile_csv_file(file_path: str) -> dict[str, Any]:
    # 1. Encoding validation & CSV reading
    encodings = ["utf-8", "latin-1", "utf-8-sig"]
    df = None
    last_err = None

    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            break
        except Exception as exc:
            last_err = exc

    if df is None:
        raise ValueError(f"Failed to read CSV file with supported encodings: {last_err}")

    # 2. Strip currency symbols, commas, and whitespace & coerce numeric columns BEFORE inferring dtypes
    df = clean_and_coerce_numeric_columns(df)

    # 3. Computations (re-run AFTER cleaning step)
    row_count = int(len(df))
    column_count = int(len(df.columns))
    column_names = [str(c) for c in df.columns]
    data_types = {str(c): str(dtype) for c, dtype in df.dtypes.items()}
    missing_values = {str(c): int(df[c].isna().sum()) for c in df.columns}
    duplicate_row_count = int(df.duplicated().sum())

    # 4. Numeric Summary Statistics
    numeric_df = df.select_dtypes(include=["number"])
    summary_stats: dict[str, dict[str, Any]] = {}

    if not numeric_df.empty:
        desc = numeric_df.describe()
        for col in numeric_df.columns:
            col_str = str(col)
            summary_stats[col_str] = {
                "count": _sanitize_value(desc.at["count", col]),
                "mean": _sanitize_value(desc.at["mean", col]),
                "std": _sanitize_value(desc.at["std", col]),
                "min": _sanitize_value(desc.at["min", col]),
                "25%": _sanitize_value(desc.at["25%", col]),
                "50%": _sanitize_value(desc.at["50%", col]),
                "75%": _sanitize_value(desc.at["75%", col]),
                "max": _sanitize_value(desc.at["max", col]),
            }

    return {
        "row_count": row_count,
        "column_count": column_count,
        "column_names": column_names,
        "data_types": data_types,
        "missing_values": missing_values,
        "duplicate_row_count": duplicate_row_count,
        "summary_stats": summary_stats,
    }
