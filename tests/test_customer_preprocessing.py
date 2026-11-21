import unittest

import pandas as pd

from src.preprocessing import preprocess_customer_dataset


class CustomerPreprocessingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = {
            "customer_id_column": "customer_id",
            "customer_columns_to_keep": ["customer_id", "postal_area"],
            "customer_geographic_columns": ["postal_area"],
            "customer_missing_category": "Unknown",
            "customer_location_relationships": [["postal_code", "postal_area"]],
        }

    def test_fills_unique_matches_and_preserves_duplicate_customer_ids(self) -> None:
        frame = pd.DataFrame(
            {
                "customer_id": ["1", "1"],
                "postal_code": ["P1", "P1"],
                "postal_area": ["Area A", None],
            }
        )

        cleaned = preprocess_customer_dataset(frame, self.config)

        self.assertEqual(len(cleaned), 2)
        self.assertEqual(cleaned["postal_area"].tolist(), ["Area A", "Area A"])

    def test_does_not_fill_ambiguous_matches(self) -> None:
        frame = pd.DataFrame(
            {
                "customer_id": ["1", "2", "3"],
                "postal_code": ["P1", "P1", "P1"],
                "postal_area": ["Area A", "Area B", None],
            }
        )

        cleaned = preprocess_customer_dataset(frame, self.config)

        self.assertEqual(cleaned.loc[2, "postal_area"], "Unknown")

    def test_extracts_geographic_codes_and_preserves_unknown(self) -> None:
        frame = pd.DataFrame(
            {
                "customer_id": ["1", "2"],
                "postal_code": ["P1", "P2"],
                "postal_area": [
                    "Postal area PA12: Example description",
                    "Unknown",
                ],
            }
        )

        cleaned = preprocess_customer_dataset(frame, self.config)

        self.assertEqual(cleaned["customer_id"].tolist(), ["1", "2"])
        self.assertEqual(cleaned["postal_area"].tolist(), ["PA12", "Unknown"])

    def test_rejects_missing_relationship_columns(self) -> None:
        frame = pd.DataFrame({"customer_id": ["1"], "postal_area": [None]})

        with self.assertRaisesRegex(ValueError, "postal_code"):
            preprocess_customer_dataset(frame, self.config)


if __name__ == "__main__":
    unittest.main()
