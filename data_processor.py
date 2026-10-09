import logging
import pandas as pd

logger = logging.getLogger(__name__)

def remove_duplicates(df):
    """Remove duplicate rows."""
    rows_before = len(df)
    df = df.drop_duplicates()
    rows_after = len(df)
    logger.debug(f"remove_duplicates: {rows_before} -> {rows_after} rows")
    return df


def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    if axis == "rows":
        before = len(df)
        df = df.dropna(axis=0)
        after = len(df)
        logger.debug(f"handle_missing: {before} -> {after} rows")
    elif axis == "columns":
        before = len(df.columns)
        df = df.dropna(axis=1)
        after = len(df.columns)
        logger.debug(f"handle_missing: {before} -> {after} columns")
    else:
        logger.error(f"Invalid axis: {axis}")
        raise ValueError("axis must be either 'rows' or 'columns'")
    return df


def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""
    if method not in ["iqr", "zscore"]:
        logger.error(f"Unsupported outlier method: {method}")
        raise ValueError(f"Unsupported outlier method: {method}")

    for col in columns:
        if col not in df.columns:
            logger.warning(f"Column not found: {col}")
            continue
        elif not pd.api.types.is_numeric_dtype(df[col]):
            logger.warning(f"Column is not numeric: {col}")
            continue
        else:
            rows_before = len(df)
            if method == "iqr":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
            elif method == "zscore":
                z_scores = (df[col] - df[col].mean()) / df[col].std()
                df = df[z_scores.abs() < threshold]
            rows_after = len(df)
            removed = rows_before - rows_after
            logger.debug(f"{col}: method={method}, threshold={threshold}, removed={removed}")
    return df


def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""
    processing = config["processing"]
    missing = processing["missing"]
    outliers = processing["outliers"]

    if processing["remove_duplicates"]:
        df = remove_duplicates(df)
    if missing["enabled"]:
        df = handle_missing(df, axis=missing["axis"])
    if outliers["enabled"]:
        df = remove_outliers(df, columns=outliers["columns"], method=outliers["method"], threshold=outliers["threshold"])
    return df


def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""
    rows_before = len(df_before)
    rows_after = len(df_after)
    rows_removed = rows_before - rows_after

    columns_before = len(df_before.columns)
    columns_after = len(df_after.columns)
    columns_removed = columns_before - columns_after

    return {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": rows_removed,
        "columns_before": columns_before,
        "columns_after": columns_after,
        "columns_removed": columns_removed
    }