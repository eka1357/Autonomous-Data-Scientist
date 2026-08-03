from typing import Any
import numpy as np
import pandas as pd
from sklearn.feature_selection import VarianceThreshold
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (
    LabelEncoder,
    MinMaxScaler,
    Normalizer,
    OrdinalEncoder,
    RobustScaler,
    StandardScaler,
)


def execute_preprocessing_plan(
    df: pd.DataFrame, preprocessing_plan: dict[str, Any]
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.Series | pd.DataFrame | None,
    pd.Series | pd.DataFrame | None,
    dict[str, Any],
]:
    """
    Executes machine learning preprocessing on cleaned dataset:
    - Categorical Encodings (Label Encoding, One-Hot Encoding, Ordinal Encoding)
    - Numeric Scalings (Standard Scaling, MinMax Scaling, Robust Scaling, Normalization)
    - Feature Selection (Optional, e.g. Variance Threshold)
    - Train / Test Split (X_train, X_test, y_train, y_test)

    Returns:
    (ml_df, X_train, X_test, y_train, y_test, execution_summary)
    """
    ml_df = df.copy()
    initial_rows, initial_cols = len(ml_df), len(ml_df.columns)
    applied_operations: list[str] = []

    target_col = preprocessing_plan.get("target_column")
    if target_col and target_col not in ml_df.columns:
        target_col = None

    # Separate target series if specified, so target doesn't get encoded/scaled accidentally unless requested
    target_series = None
    if target_col and target_col in ml_df.columns:
        target_series = ml_df[target_col].copy()

    # 1. Categorical Encodings
    encode_cat = preprocessing_plan.get("encode_categorical", {})
    if isinstance(encode_cat, dict):
        for col, method in encode_cat.items():
            if col not in ml_df.columns or col == target_col:
                continue
            meth_str = str(method).lower()
            if meth_str in ("onehot", "one_hot", "one-hot"):
                dummies = pd.get_dummies(ml_df[col], prefix=col, drop_first=False, dtype=int)
                ml_df = pd.concat([ml_df.drop(columns=[col]), dummies], axis=1)
                applied_operations.append(
                    f"One-Hot encoded column '{col}' into {len(dummies.columns)} binary columns"
                )
            elif meth_str in ("label", "label_encoder"):
                le = LabelEncoder()
                ml_df[col] = le.fit_transform(ml_df[col].astype(str))
                applied_operations.append(f"Label encoded column '{col}'")
            elif meth_str in ("ordinal", "ordinal_encoder"):
                oe = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
                ml_df[col] = oe.fit_transform(ml_df[[col]]).ravel()
                applied_operations.append(f"Ordinal encoded column '{col}'")

    # If target column is categorical/string, label encode target if needed
    if target_col and target_series is not None and not pd.api.types.is_numeric_dtype(target_series):
        le_target = LabelEncoder()
        target_series = pd.Series(
            le_target.fit_transform(target_series.astype(str)),
            index=target_series.index,
            name=target_col,
        )
        ml_df[target_col] = target_series
        applied_operations.append(f"Label encoded target column '{target_col}'")

    # Auto-encode remaining object/string/category columns if not explicitly handled
    for col in ml_df.columns:
        if col == target_col:
            continue
        if not pd.api.types.is_numeric_dtype(ml_df[col]):
            le = LabelEncoder()
            ml_df[col] = le.fit_transform(ml_df[col].astype(str))
            applied_operations.append(f"Auto Label-encoded string column '{col}'")

    # 2. Numeric Scalings & Normalization
    scale_num = preprocessing_plan.get("scale_numeric", {})
    if isinstance(scale_num, list):
        scale_dict = {col: "standard" for col in scale_num}
    elif isinstance(scale_num, dict):
        scale_dict = scale_num
    else:
        scale_dict = {}

    for col, method in scale_dict.items():
        if col not in ml_df.columns or col == target_col:
            continue
        if not pd.api.types.is_numeric_dtype(ml_df[col]):
            continue
        meth_str = str(method).lower()
        col_values = ml_df[[col]].astype(float)

        if meth_str in ("standard", "standardize", "standard_scaler"):
            scaler = StandardScaler()
            ml_df[col] = scaler.fit_transform(col_values).ravel()
            applied_operations.append(f"Standard scaled column '{col}'")
        elif meth_str in ("minmax", "min_max", "minmax_scaler"):
            scaler = MinMaxScaler()
            ml_df[col] = scaler.fit_transform(col_values).ravel()
            applied_operations.append(f"MinMax scaled column '{col}'")
        elif meth_str in ("robust", "robust_scaler"):
            scaler = RobustScaler()
            ml_df[col] = scaler.fit_transform(col_values).ravel()
            applied_operations.append(f"Robust scaled column '{col}'")
        elif meth_str in ("normalize", "normalizer", "l2_normalize"):
            norm = Normalizer()
            ml_df[col] = norm.fit_transform(col_values).ravel()
            applied_operations.append(f"Normalized column '{col}'")

    # 3. Optional Feature Selection
    feature_selection = preprocessing_plan.get("feature_selection")
    if isinstance(feature_selection, dict) and feature_selection.get("enabled", True):
        threshold = feature_selection.get("threshold", 0.0)
        feature_cols = [c for c in ml_df.columns if c != target_col]
        if len(feature_cols) > 1 and threshold >= 0:
            vt = VarianceThreshold(threshold=threshold)
            try:
                vt.fit(ml_df[feature_cols])
                selected_indices = vt.get_support(indices=True)
                selected_cols = [feature_cols[i] for i in selected_indices]
                dropped_cols = set(feature_cols) - set(selected_cols)
                if dropped_cols:
                    keep_cols = selected_cols + ([target_col] if target_col in ml_df.columns else [])
                    ml_df = ml_df[keep_cols]
                    applied_operations.append(
                        f"VarianceThreshold feature selection removed {len(dropped_cols)} low-variance columns: {list(dropped_cols)}"
                    )
            except Exception as e:
                applied_operations.append(f"Skipped VarianceThreshold selection: {e}")

    # 4. Train / Test Split
    test_size = float(preprocessing_plan.get("test_size", 0.2))
    random_state = int(preprocessing_plan.get("random_state", 42))

    X = ml_df.drop(columns=[target_col]) if target_col and target_col in ml_df.columns else ml_df.copy()
    y = ml_df[target_col].copy() if target_col and target_col in ml_df.columns else None

    if len(X) > 1:
        try:
            if y is not None:
                stratify_y = None
                if pd.api.types.is_integer_dtype(y) or y.nunique() <= 20:
                    class_counts = y.value_counts()
                    if (class_counts >= 2).all() and len(class_counts) > 1:
                        stratify_y = y

                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_size, random_state=random_state, stratify=stratify_y
                )
            else:
                X_train, X_test = train_test_split(X, test_size=test_size, random_state=random_state)
                y_train, y_test = None, None
        except Exception:
            # Fallback without stratification
            try:
                if y is not None:
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=test_size, random_state=random_state, stratify=None
                    )
                else:
                    X_train, X_test = train_test_split(X, test_size=test_size, random_state=random_state)
                    y_train, y_test = None, None
            except Exception:
                X_train, X_test = X.copy(), X.copy()
                y_train = y.copy() if y is not None else None
                y_test = y.copy() if y is not None else None
    else:
        X_train, X_test = X.copy(), X.copy()
        y_train = y.copy() if y is not None else None
        y_test = y.copy() if y is not None else None

    applied_operations.append(
        f"Train/Test split performed (test_size={test_size}, random_state={random_state}). Train shape: {X_train.shape}, Test shape: {X_test.shape}"
    )

    final_rows, final_cols = len(ml_df), len(ml_df.columns)
    summary = {
        "rows_before": initial_rows,
        "rows_after": final_rows,
        "columns_before": initial_cols,
        "columns_after": final_cols,
        "target_column": target_col,
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "feature_count": len(X.columns),
        "feature_names": list(X.columns),
        "operations_applied": applied_operations,
    }

    return ml_df, X_train, X_test, y_train, y_test, summary
