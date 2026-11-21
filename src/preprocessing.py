import logging

import pandas as pd


logger = logging.getLogger(__name__)


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


def preprocess_customer_dataset(frame: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Reconstruct geographic values and retain their codes for downstream models."""
    relationships = [tuple(pair) for pair in config["customer_location_relationships"]]
    columns_to_keep = config["customer_columns_to_keep"]
    geographic_columns = config["customer_geographic_columns"]
    required_columns = set(columns_to_keep)
    required_columns.update(geographic_columns)
    for source, target in relationships:
        required_columns.update((source, target))

    missing_columns = required_columns - set(frame.columns)
    if missing_columns:
        raise ValueError(
            f"Customer dataset is missing required columns: {sorted(missing_columns)}"
        )

    original = frame.copy()
    reconstructed = original.copy()
    lookups = {}

    for source, target in relationships:
        known = original[[source, target]].dropna()
        lookups[(source, target)] = (
            known.groupby(source, dropna=True)[target]
            .agg(set)
            .to_dict()
        )

    for target in dict.fromkeys(target for _, target in relationships):
        for index in original.index[original[target].isna()]:
            candidates = set()
            ambiguous = False

            for source, related_target in relationships:
                if related_target != target:
                    continue

                source_value = original.at[index, source]
                if pd.isna(source_value):
                    continue

                possible = lookups[(source, target)].get(source_value, set())
                if len(possible) > 1:
                    ambiguous = True
                elif len(possible) == 1:
                    candidates.update(possible)

            if not ambiguous and len(candidates) == 1:
                reconstructed.at[index, target] = next(iter(candidates))

    recovered = original.isna().sum() - reconstructed.isna().sum()
    duplicate_rows = int(reconstructed.duplicated().sum())
    duplicate_customer_ids = int(
        reconstructed[config["customer_id_column"]].duplicated().sum()
    )
    recovered_columns = recovered[recovered > 0].to_dict()
    logger.info(
        "Customer geography: recovered %s missing values; duplicate rows: %s; "
        "duplicate customer IDs: %s",
        recovered_columns,
        duplicate_rows,
        duplicate_customer_ids,
    )

    cleaned = reconstructed.loc[:, columns_to_keep].copy()
    cleaned.loc[:, geographic_columns] = cleaned[geographic_columns].fillna(
        config["customer_missing_category"]
    )
    for column in geographic_columns:
        values = cleaned[column].astype("string")
        codes = values.str.extract(r"^\s*.*\b([A-Za-z]+\d+)\s*:")[0]
        cleaned[column] = codes.fillna(values)
    return cleaned
