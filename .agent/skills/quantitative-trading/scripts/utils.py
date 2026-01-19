import numpy as np
import pandas as pd
from datetime import date, datetime

def make_serializable(obj):
    """
    Recursively convert objects to JSON-serializable types.
    Handles:
    - numpy types (int64, float64, bool_, array)
    - pandas types (Series, DataFrame, Timestamp)
    - datetime objects
    - nested dicts and lists
    """
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.floating, float)):
        return float(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return make_serializable(obj.tolist())
    elif isinstance(obj, (pd.Series, pd.DataFrame)):
        return make_serializable(obj.to_dict())
    elif isinstance(obj, (datetime, date, pd.Timestamp)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_serializable(item) for item in obj]
    elif obj is None:
        return None
    else:
        return str(obj)
