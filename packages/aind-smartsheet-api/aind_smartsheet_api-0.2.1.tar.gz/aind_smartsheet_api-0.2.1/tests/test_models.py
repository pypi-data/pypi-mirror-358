"""Tests classes in models module"""

import json
import os
import unittest
from datetime import datetime, timezone
from pathlib import Path

from aind_smartsheet_api.models import SheetFields, SheetRow, SheetRowCell

RESOURCE_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"
EXAMPLE_SHEET = RESOURCE_DIR / "example_sheet.json"


class TestParsing(unittest.TestCase):
    """Tests validators for SheetRow and SheetFields class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Read example json files"""
        with open(EXAMPLE_SHEET, "r") as f:
            contents = json.load(f)
        cls.example_sheet: str = json.dumps(contents)

    def test_parse_datetime_str(self):
        """Tests _parse_datetime_str validator function."""
        example_row = SheetRow(
            cells=[
                SheetRowCell(
                    columnId=1729551260405636,
                    value="122-01-001-10",
                    displayValue="122-01-001-10",
                )
            ],
            createdAt="2023-08-07T23:39:14+00:00Z",
            expanded=False,
            id=123456,
            modifiedAt="2023-12-20T18:32:10+00:00",
            rowNumber=1,
        )
        expected_validated_row = SheetRow(
            cells=[
                SheetRowCell(
                    columnId=1729551260405636,
                    value="122-01-001-10",
                    displayValue="122-01-001-10",
                )
            ],
            createdAt=datetime(2023, 8, 7, 23, 39, 14, tzinfo=timezone.utc),
            expanded=False,
            id=123456,
            modifiedAt=datetime(2023, 12, 20, 18, 32, 10, tzinfo=timezone.utc),
            rowNumber=1,
        )
        self.assertEqual(expected_validated_row, example_row)

    def test_sheet_fields(self):
        """Tests SheetFields parses json file into generic model"""
        json_contents = self.example_sheet
        sheet_fields = SheetFields.model_validate_json(json_contents)
        self.assertEqual(5, len(sheet_fields.columns))
        self.assertEqual(3, len(sheet_fields.rows))


if __name__ == "__main__":
    unittest.main()
