import math
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

    # 2. Computations
    row_count = int(len(df))
    column_count = int(len(df.columns))
    column_names = [str(c) for c in df.columns]
    data_types = {str(c): str(dtype) for c, dtype in df.dtypes.items()}
    missing_values = {str(c): int(df[c].isna().sum()) for c in df.columns}
    duplicate_row_count = int(df.duplicated().sum())

    # 3. Numeric Summary Statistics
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
