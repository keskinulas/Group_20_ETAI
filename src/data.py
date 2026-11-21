import logging
from pathlib import Path

import pandas as pd
import yaml

from .preprocessing import clean_dataset, preprocess_customer_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[1]
logger = logging.getLogger(__name__)


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
    configured_columns = set(cleaning["numeric_text_columns"])
    configured_columns.update(cleaning["categorical_columns"])
    configured_columns.update(cleaning["canonical_categories"])
    configured_columns.update(cleaning["validity_rules"])
    configured_columns.update(cleaning["redundant_columns"])
    if protected & configured_columns:
        raise ValueError(f"Cleaning rules target protected columns: {sorted(protected & configured_columns)}")

    train_path = PROJECT_ROOT / data["train_path"]
    test_path = PROJECT_ROOT / data["batch_path"]
    train_output = PROJECT_ROOT / cleaning["train_output_path"]
    test_output = PROJECT_ROOT / cleaning["test_output_path"]
    customers_path = (
        PROJECT_ROOT / data["customers_path"]
        if data.get("customers_path")
        else None
    )
    customers_output = (
        PROJECT_ROOT / cleaning["customers_output_path"]
        if customers_path is not None
        else None
    )
    outputs = {train_output.resolve(), test_output.resolve()}
    if customers_output is not None:
        outputs.add(customers_output.resolve())
    expected_output_count = 3 if customers_output is not None else 2
    raw_directory = (PROJECT_ROOT / "data/raw").resolve()
    if len(outputs) != expected_output_count or any(
        path.is_relative_to(raw_directory) for path in outputs
    ):
        raise ValueError("Cleaning requires distinct output paths outside data/raw.")
    input_paths = {train_path.resolve(), test_path.resolve()}
    if customers_path is not None:
        input_paths.add(customers_path.resolve())
    if outputs & input_paths:
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
    if customers_path is not None and customers_path.exists():
        customer_id_column = data["customer_id_column"]
        customers = pd.read_csv(
            customers_path,
            dtype={customer_id_column: "string"},
        )
        cleaned_files[customers_output] = preprocess_customer_dataset(
            customers,
            {
                **cleaning,
                "customer_id_column": customer_id_column,
            },
        )
    elif customers_path is not None and data.get("use_customers", False):
        raise FileNotFoundError(
            f"Customer dataset is required but was not found: {customers_path}"
        )
    elif customers_path is not None:
        logger.info(
            "Customer dataset not found; skipping optional input: %s",
            customers_path,
        )

    for path, frame in cleaned_files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False)

    return {path: len(frame) for path, frame in cleaned_files.items()}
