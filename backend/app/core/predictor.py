from typing import Any
import numpy as np
import pandas as pd


def _sanitize_val(val: Any) -> Any:
    if isinstance(val, (np.generic, np.number)):
        return val.item()
    if isinstance(val, np.ndarray):
        return val.tolist()
    return val


def predict_with_model(model: Any, input_df: pd.DataFrame) -> tuple[list[Any], list[Any] | None]:
    """
    Executes inference with a serialized trained model.

    Returns:
    (predictions_list, probabilities_list_or_none)
    """
    # Align features if model has feature_names_in_ attribute
    if hasattr(model, "feature_names_in_"):
        expected_features = list(model.feature_names_in_)
        # Fill missing features with 0.0
        for col in expected_features:
            if col not in input_df.columns:
                input_df[col] = 0.0
        input_df = input_df[expected_features]

    preds = model.predict(input_df)
    predictions = [_sanitize_val(p) for p in preds]

    probabilities = None
    if hasattr(model, "predict_proba"):
        try:
            probas = model.predict_proba(input_df)
            probabilities = [_sanitize_val(p) for p in probas]
        except Exception:
            probabilities = None

    return predictions, probabilities
