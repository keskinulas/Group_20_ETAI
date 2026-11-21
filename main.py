import argparse
import logging
from pathlib import Path

from src.data import PROJECT_ROOT, clean_csv_files


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean train, test, and optional customer CSV files."
    )
    parser.add_argument("command", choices=["clean"])
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "config.yaml")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    for path, rows in clean_csv_files(args.config).items():
        print(f"{path}: {rows} rows")


if __name__ == "__main__":
    main()
