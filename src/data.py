from pathlib import Path

import pandas as pd
import yaml

from .preprocessing import clean_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def clean_csv_files(config_path: Path) -> dict[Path, int]:
    with config_path.open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    data = config["data"]
    cleaning = config["cleaning"]
    id_column = data["id_column"]
    protected = {
        id_column,
        data["customer_id_column"],
        data["classification_target"],
        data["regression_target"],
    }
    configured_columns = set().union(
        cleaning["numeric_text_columns"],
        cleaning["categorical_columns"],
        cleaning["canonical_categories"],
        cleaning["validity_rules"],
        cleaning["redundant_columns"],
    )
    if protected & configured_columns:
        raise ValueError(f"Cleaning rules target protected columns: {sorted(protected & configured_columns)}")

    train_path = PROJECT_ROOT / data["train_path"]
    test_path = PROJECT_ROOT / data["batch_path"]
    train_output = PROJECT_ROOT / cleaning["train_output_path"]
    test_output = PROJECT_ROOT / cleaning["test_output_path"]
    outputs = {train_output.resolve(), test_output.resolve()}
    if len(outputs) != 2 or any(path.is_relative_to(PROJECT_ROOT / "data/raw") for path in outputs):
        raise ValueError("Cleaning requires two distinct output paths outside data/raw.")
    if outputs & {train_path.resolve(), test_path.resolve()}:
        raise ValueError("Cleaning output paths overlap with input paths.")

    id_types = {column: "string" for column in (id_column, data["customer_id_column"])}
    train = pd.read_csv(train_path, dtype=id_types, keep_default_na=False, na_values=[""])
    test = pd.read_csv(test_path, dtype=id_types, keep_default_na=False, na_values=[""])
    if cleaning["drop_exact_train_duplicates"]:
        train = train.drop_duplicates()

    required_purchase_fields = cleaning.get("train_drop_if_all_missing", [])
    if required_purchase_fields:
        train = train.dropna(subset=required_purchase_fields, how="all")

    cleaned_files = {
        train_output: clean_dataset(train, cleaning),
        test_output: clean_dataset(test, cleaning),
    }
    for path, frame in cleaned_files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False)

    return {path: len(frame) for path, frame in cleaned_files.items()}
