from typing import Any
import numpy as np
import pandas as pd


def execute_preprocessing_plan(
    df: pd.DataFrame, preprocessing_plan: dict[str, Any]
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Executes machine learning preprocessing on human-readable cleaned data:
    - Categorical Encoding (One-hot encoding, Label/Ordinal encoding)
    - Numeric Scaling (Standardization, MinMax scaling)
    Outputs ML-ready numerical dataset ready for model training.
    """
    ml_df = df.copy()
    initial_rows, initial_cols = len(ml_df), len(ml_df.columns)
    applied_operations: list[str] = []

    # 1. Categorical Encoding
    encode_cat = preprocessing_plan.get("encode_categorical", {})
    if isinstance(encode_cat, dict):
        for col, method in encode_cat.items():
            if col not in ml_df.columns:
                continue
            meth_str = str(method).lower()
            if meth_str == "onehot":
                dummies = pd.get_dummies(ml_df[col], prefix=col, drop_first=False, dtype=int)
                ml_df = pd.concat([ml_df.drop(columns=[col]), dummies], axis=1)
                applied_operations.append(f"One-hot encoded column '{col}' into {len(dummies.columns)} binary columns")
            elif meth_str in ("label", "ordinal"):
                codes, _ = pd.factorize(ml_df[col])
                ml_df[col] = codes
                applied_operations.append(f"Label encoded column '{col}'")

    # 2. Numeric Scaling
    scale_num = preprocessing_plan.get("scale_numeric", {})
    if isinstance(scale_num, list):
        scale_dict = {col: "standard" for col in scale_num}
    elif isinstance(scale_num, dict):
        scale_dict = scale_num
    else:
        scale_dict = {}

    for col, method in scale_dict.items():
        if col not in ml_df.columns or not pd.api.types.is_numeric_dtype(ml_df[col]):
            continue
        meth_str = str(method).lower()
        col_series = ml_df[col].astype(float)

        if meth_str in ("standard", "standardize"):
            std_val = col_series.std()
            if std_val != 0 and not np.isnan(std_val):
                ml_df[col] = (col_series - col_series.mean()) / std_val
                applied_operations.append(f"Standard scaled column '{col}'")
        elif meth_str in ("minmax", "min_max"):
            min_val, max_val = col_series.min(), col_series.max()
            range_val = max_val - min_val
            if range_val != 0 and not np.isnan(range_val):
                ml_df[col] = (col_series - min_val) / range_val
                applied_operations.append(f"Min-max scaled column '{col}'")

    final_rows, final_cols = len(ml_df), len(ml_df.columns)
    summary = {
        "rows_before": initial_rows,
        "rows_after": final_rows,
        "columns_before": initial_cols,
        "columns_after": final_cols,
        "operations_applied": applied_operations,
    }

    return ml_df, summary
