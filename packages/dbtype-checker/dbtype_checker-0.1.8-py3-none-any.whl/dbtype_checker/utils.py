
import pandas as pd

MAX_INFER_ROWS = 10_000  # Max number of rows to sample for inference

def infer_type_by_values(series: pd.Series):
    """
    Infers type by inspecting actual values using pandas and regex logic.
    """
    cleaned = series.dropna().astype(str).str.strip().str.lower()
    total = len(cleaned)

    if total == 0:
        return str

    bool_like = cleaned.isin(['true', 'false', 'yes', 'no']).sum() / total
    int_like = cleaned.str.match(r"^-?\d+$").sum() / total
    float_like = cleaned.str.match(r"^-?\d*\.\d+$").sum() / total
    datetime_like = pd.to_datetime(series, errors="coerce").notna().sum() / total

    if bool_like > 0.95:
        return bool
    elif int_like > 0.95:
        return int
    elif float_like + int_like > 0.95:
        return float
    elif datetime_like > 0.95:
        return "datetime"
    else:
        return str

def infer_type(column_name: str, values):
    """
    Infers the final data type by inspecting actual data values.
    Uses only pandas-based logic.
    """
    series = pd.Series(values[:MAX_INFER_ROWS])
    value_type = infer_type_by_values(series)

    return {
        "column": column_name,
        "inferred_by_values": value_type,
        "final_inferred_type": value_type
    }
