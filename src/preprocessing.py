import pandas as pd


def clean_dataset(frame: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Apply row-local cleaning rules to either input split."""
    cleaned = frame.copy()
    tokens = {str(token).strip().casefold() for token in config["placeholder_tokens"]}
    bounds_by_column = config["validity_rules"]

    for column in dict.fromkeys([*config["numeric_text_columns"], *bounds_by_column]):
        if column not in cleaned:
            continue
        values = cleaned[column]
        placeholders = values.astype("string").str.strip().str.casefold().isin(tokens)
        numeric = pd.to_numeric(values.mask(placeholders), errors="coerce")
        bounds = bounds_by_column.get(column, {})
        if "min" in bounds:
            numeric = numeric.mask(numeric < bounds["min"])
        if "max" in bounds:
            numeric = numeric.mask(numeric > bounds["max"])
        cleaned[column] = numeric

    categories = config["canonical_categories"]
    for column in dict.fromkeys([*config["categorical_columns"], *categories]):
        if column not in cleaned:
            continue
        values = cleaned[column].astype("string").str.strip()
        keys = values.str.casefold()
        mapping = {
            str(key).strip().casefold(): value
            for key, value in categories.get(column, {}).items()
        }
        cleaned[column] = keys.map(mapping).fillna(values).mask(keys.isin(tokens))

    return cleaned.drop(columns=config["redundant_columns"], errors="ignore")
