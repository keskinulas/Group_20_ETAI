# Group_20_ETAI

ETAI group project — Group 20, academic year 2026/27.

Predict whether a customer will make another purchase within 90 days of the current transaction and how much they will spend during that period.

## Project status

The repository includes a config-driven CSV cleaning step. The training and prediction commands below describe the planned interface.

## Setup

Python 3.11 is recommended. Run the following commands from the repository root.

### macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
mkdir -p data/raw
```

### Windows (PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
New-Item -ItemType Directory -Force data/raw
```

If PowerShell blocks activation, install dependencies with `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and use `.\.venv\Scripts\python.exe` instead of `python` in subsequent commands.

## Data and repository structure

Place `train.csv`, `test.csv`, `sample_submission.csv` and the optional `clientes.csv` in the local `data/raw/` directory. Configure file paths and column names in `config.yaml`. Raw data, virtual environments, trained models and generated outputs are excluded from Git. All configuration paths are relative to the repository root.

Planned directories:

```text
notebooks/  # 01_data_exploration, 02_classification, 03_regression, 04_explainability
src/        # data.py, features.py, train.py, predict_batch.py, predict_one.py
data/raw/   # Local CSV files
models/     # Saved pipelines produced during training
outputs/    # Prediction CSV files and evaluation results
```

The notebooks will document cleaning decisions, model comparisons and explainability analyses for both models. Training, batch prediction and single-purchase prediction will share the same feature generation logic. Saved pipelines will include preprocessing.

## Clean train and test data

```bash
python main.py clean --config config.yaml
```

The command reads the paths in `data.train_path` and `data.batch_path` and writes to the output paths in `cleaning`. By default, the cleaned CSVs are written to `data/processed/`. If `data.customers_path` exists, the same command also creates `data/processed/clientes.csv`. Train and test use the same column rules, and test retains its original row order. The optional duplicate rule applies to identical rows in train only.

The `cleaning` section controls numeric conversion, category normalization, valid ranges, and column removal for train/test. The `train_drop_if_all_missing` list removes train rows only when every listed purchase field is blank. Set it to `[]` to disable the rule. The default fields identify training records with no purchase date or current purchase totals. Other missing values remain blank in the cleaned CSVs. Any imputation fitted during model development should use the training partition.

- The original training and test files in `data/raw/` are preserved, while cleaned copies are created in `data/processed/`.
- Exact duplicate rows were removed only from the training dataset.
- Training records with no purchase date and no value in any configured purchase-total field were removed.
- Numeric columns stored as text were converted into numeric format, while invalid values were converted into missing values.
- Categorical columns were stripped of surrounding whitespace, and empty values were identified as missing values.
- The cleaning rules are configurable through `config.yaml`, ensuring consistent processing of both datasets.
- The customer preprocessing follows `notebooks/preprocessing_clientes_etai_project.ipynb`: it reconstructs missing geographic values only when the original data provides one unambiguous match, checks and reports duplicate rows and `customer_id` values without deleting them, keeps `customer_id`, `postal_area`, `municipality`, `country_or_region` and `commercial_region`, extracts the code from each retained geographic label, and fills remaining geographic missing values with `Unknown`.
- Customer records remain a separate processed CSV for joining by `customer_id`; the cleaning command does not merge them into train/test. The customer output columns, geographic relationships and missing-value category are configurable in `cleaning`.
- The customer file is preprocessed whenever it exists. If it is absent, preprocessing is skipped when `data.use_customers` is false and reported as an error when that flag is true.



## Planned commands

Once the code is implemented and the configuration is complete:

```bash
python -m src.train --config config.yaml
python -m src.predict_batch --config config.yaml
python -m src.predict_one --config config.yaml --input purchase.json
```

`purchase.json` will contain a JSON object describing one purchase. Required fields will be documented once the data schema is verified. Single-purchase prediction will return the repeat-purchase probability, the classification decision using the configured threshold and the spending estimate.

Batch prediction will produce a Kaggle CSV with `ID,repeat_purchase_90d` for every test row and a separate spending CSV with `ID,repeat_purchase_90d,spend_next_90d` for customers predicted to return. The Kaggle output will follow the structure of `sample_submission.csv`.








## Submission

The repository is named `Group_20_ETAI`. The handbook requires the submission archive to be named `Group20_ETAI_2627.zip`; the repository name does not change this requirement. The stated deadline is 22 December 2026 at 18:00 (the document does not specify a time zone). Include the final Kaggle CSV in the submission archive and verify that it matches the output of `predict_batch.py`.

## Handbook requirements

- Targets: `repeat_purchase_90d` and `spend_next_90d`, the amount spent in the following 90 days. `ID` identifies a modelling row and its Kaggle submission entry; `customer_id` is the join key for `clientes.csv`.
- Compare at least five classification algorithms and four regression algorithms. Justify preprocessing, feature engineering and selection, hyperparameter tuning and the assessment strategy. Random Forest in the initial configuration is a starting candidate.
- Keep classification and regression predictions coherent. Report regression RMSE, MAE and R² for customers who actually returned.
- Explain both models globally and for individual customers. The client interface must support new and returning customers.
- Features must be computable at purchase time. Predict each test row using only that row, the training data and `clientes.csv`, never other test rows. Never use the regression target as a classification feature.
- Prediction must load saved pipelines without retraining. Keep configurable choices in `config.yaml`.
- Lazy Predict and similar AutoML tools are prohibited. Group members must be able to explain and defend every step included in the notebooks and code.

Source: ETAI Project - 2627, sections II–VI. The PDF was reviewed locally and is not included in this repository.
