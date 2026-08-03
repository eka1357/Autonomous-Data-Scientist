from typing import Any
import pandas as pd
from app.core.profiler import clean_and_coerce_numeric_columns


def execute_cleaning_plan(
    df: pd.DataFrame, cleaning_plan: dict[str, Any]
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Executes human-readable data cleaning:
    - Numeric coercion (stripping currency symbols/commas)
    - Whitespace trimming on text columns
    - Duplicate row removal
    - Unwanted column dropping (>60% missing threshold)
    - Per-column missing value handling (median, mean, mode, Unknown, drop, ffill, bfill)

    Does NOT perform ML preprocessing (no label/one-hot encoding, scaling, normalization, or splitting).
    Returns a human-readable cleaned DataFrame and execution summary.
    """
    # 0. Clean currency symbols, commas, whitespace and attempt numeric coercion first
    cleaned_df = clean_and_coerce_numeric_columns(df)
    initial_rows, initial_cols = len(cleaned_df), len(cleaned_df.columns)
    applied_operations: list[str] = []

    # 1. Whitespace Trimming in text columns
    if cleaning_plan.get("trim_whitespace", True):
        trimmed_cols = 0
        for col in cleaned_df.select_dtypes(include=["object", "string"]).columns:
            cleaned_df[col] = cleaned_df[col].apply(lambda v: v.strip() if isinstance(v, str) else v)
            trimmed_cols += 1
        if trimmed_cols > 0:
            applied_operations.append(f"Trimmed leading/trailing whitespace in {trimmed_cols} text column(s)")

    # 2. Deduplication
    if cleaning_plan.get("remove_duplicates", True):
        before = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates()
        dropped = before - len(cleaned_df)
        if dropped > 0:
            applied_operations.append(f"Removed {dropped} duplicate row(s)")

    # 3. Drop Columns (e.g. columns missing > 60%)
    drop_cols = cleaning_plan.get("drop_columns", [])
    valid_drop_cols = [c for c in drop_cols if c in cleaned_df.columns]
    if valid_drop_cols:
        cleaned_df = cleaned_df.drop(columns=valid_drop_cols)
        applied_operations.append(f"Dropped columns (>60% missing or unwanted): {', '.join(valid_drop_cols)}")

    # 4. Fill Missing Values (Per-Column Strategy)
    fill_missing = cleaning_plan.get("fill_missing", {})
    if isinstance(fill_missing, dict):
        for col, strategy in fill_missing.items():
            if col not in cleaned_df.columns or cleaned_df[col].isna().sum() == 0:
                continue

            strat_str = str(strategy).lower()
            is_numeric = pd.api.types.is_numeric_dtype(cleaned_df[col])

            if strat_str == "mean" and is_numeric:
                val = cleaned_df[col].mean()
                cleaned_df[col] = cleaned_df[col].fillna(val)
                applied_operations.append(f"Filled missing in '{col}' using mean ({val:.2f})")
            elif strat_str in ("median", "mean") and is_numeric:
                val = cleaned_df[col].median()
                cleaned_df[col] = cleaned_df[col].fillna(val)
                applied_operations.append(f"Filled missing in '{col}' using median ({val:.2f})")
            elif strat_str in ("mode", "most_frequent"):
                mode_vals = cleaned_df[col].mode()
                val = mode_vals.iloc[0] if not mode_vals.empty else ("Unknown" if not is_numeric else 0)
                cleaned_df[col] = cleaned_df[col].fillna(val)
                applied_operations.append(f"Filled missing in '{col}' using mode ('{val}')")
            elif strat_str in ("unknown", "Unknown") and not is_numeric:
                cleaned_df[col] = cleaned_df[col].fillna("Unknown")
                applied_operations.append(f"Filled missing in '{col}' with 'Unknown'")
            elif strat_str == "drop":
                cleaned_df = cleaned_df.dropna(subset=[col])
                applied_operations.append(f"Dropped rows with missing values in '{col}'")
            elif strat_str == "ffill":
                cleaned_df[col] = cleaned_df[col].ffill()
                applied_operations.append(f"Forward filled missing in '{col}'")
            elif strat_str == "bfill":
                cleaned_df[col] = cleaned_df[col].bfill()
                applied_operations.append(f"Backward filled missing in '{col}'")
            else:
                if is_numeric:
                    val = cleaned_df[col].median()
                    cleaned_df[col] = cleaned_df[col].fillna(val)
                    applied_operations.append(f"Filled missing in '{col}' using median ({val:.2f})")
                else:
                    mode_vals = cleaned_df[col].mode()
                    val = mode_vals.iloc[0] if not mode_vals.empty else "Unknown"
                    cleaned_df[col] = cleaned_df[col].fillna(val)
                    applied_operations.append(f"Filled missing in '{col}' using mode ('{val}')")

    final_rows, final_cols = len(cleaned_df), len(cleaned_df.columns)
    execution_summary = {
        "rows_before": initial_rows,
        "rows_after": final_rows,
        "columns_before": initial_cols,
        "columns_after": final_cols,
        "operations_applied": applied_operations,
    }

    return cleaned_df, execution_summary
