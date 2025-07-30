"""Tests classes in models module"""

import json
import os
import unittest
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, call, patch

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from aind_smartsheet_api.client import SmartsheetClient, SmartsheetSettings

RESOURCE_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"
EXAMPLE_SHEET = RESOURCE_DIR / "example_sheet.json"


class TestSmartsheetSettings(unittest.TestCase):
    """Tests configs for SmartsheetSettings."""

    @patch.dict(
        os.environ,
        {
            "SMARTSHEET_ACCESS_TOKEN": "abc-123",
            "SMARTSHEET_USER_AGENT": "secret_agent",
        },
        clear=True,
    )
    def test_env_var(self):
        """Tests class can be set via env vars."""
        smart_sheet_settings = SmartsheetSettings()
        self.assertEqual(
            "abc-123", smart_sheet_settings.access_token.get_secret_value()
        )
        self.assertEqual("secret_agent", smart_sheet_settings.user_agent)

    def test_optional_sheet_id_map(self):
        """Tests optional sheet_id_map."""
        smart_sheet_settings = SmartsheetSettings(
            access_token="abc-123",
            sheet_id_map={"sheet_1": 1234, "sheet_2": 5678},
        )
        self.assertEqual(
            "abc-123", smart_sheet_settings.access_token.get_secret_value()
        )
        self.assertEqual(
            {"sheet_1": 1234, "sheet_2": 5678},
            smart_sheet_settings.sheet_id_map,
        )


class TestSmartsheetClient(unittest.TestCase):
    """Tests methods in SmartsheetClient class"""

    class MockSheetModel1(BaseModel):
        """Mocked class to hold sheet model with all valid fields for mocked
        sheet contents"""

        project_name: Optional[str] = Field(None, alias="Project Name")
        project_code: str = Field(..., alias="Project Code")
        funding_institution: str = Field(..., alias="Funding Institution")
        grant_number: Optional[str] = Field(None, alias="Grant Number")
        investigators: str = Field(..., alias="Investigators")
        model_config = ConfigDict(populate_by_name=True)

    class MockSheetModel2(BaseModel):
        """Mocked class to hold sheet model with some invalid fields for
        mocked sheet contents"""

        project_name: str = Field(..., alias="Project Name")
        project_code: str = Field(..., alias="Project Code")
        funding_institution: str = Field(..., alias="Funding Institution")
        # Some grant numbers are None, so this will be invalid
        grant_number: str = Field(..., alias="Grant Number")
        investigators: str = Field(..., alias="Investigators")
        model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def setUpClass(cls) -> None:
        """Read in json files for mock responses"""
        with open(EXAMPLE_SHEET, "r") as f:
            contents = json.load(f)
        cls.example_sheet: str = json.dumps(contents)
        default_settings = SmartsheetSettings(access_token="abc-123")
        cls.default_client = SmartsheetClient(
            smartsheet_settings=default_settings
        )

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_get_sheet_cache(self, mock_get_sheet: MagicMock):
        """Tests get_sheet pulls from cache if called twice"""
        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        default_settings = SmartsheetSettings(access_token="abc-123")
        client = SmartsheetClient(smartsheet_settings=default_settings)

        response1 = client.get_raw_sheet(sheet_id=2014892103339908)
        response2 = client.get_raw_sheet(sheet_id=2014892103339908)
        self.assertEqual(response1, response2)
        mock_get_sheet.assert_has_calls(
            [call(2014892103339908), call().to_json()]
        )

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_get_sheet_model(self, mock_get_sheet: MagicMock):
        """Tests get_sheet_model method"""
        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        sheet_fields = self.default_client.get_sheet_fields(
            sheet_id=2014892103339908
        )
        self.assertEqual(5, len(sheet_fields.columns))
        self.assertEqual(3, len(sheet_fields.rows))

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_column_id_map(self, mock_get_sheet: MagicMock):
        """Tests _column_id_map method"""
        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        sheet_fields = self.default_client.get_sheet_fields(
            sheet_id=2014892103339908
        )
        col_id_map = self.default_client._column_id_map(
            sheet_fields=sheet_fields
        )
        expected_col_id_map = {
            3981351074090884: "Project Name",
            1729551260405636: "Project Code",
            2990791841501060: "Funding Institution",
            3446515788894084: "Grant Number",
            4825776004222852: "Investigators",
        }
        self.assertEqual(expected_col_id_map, col_id_map)

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_map_row_to_dict(self, mock_get_sheet: MagicMock):
        """Tests _map_row_to_dict method"""

        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        sheet_fields = self.default_client.get_sheet_fields(
            sheet_id=2014892103339908
        )
        col_id_map = self.default_client._column_id_map(
            sheet_fields=sheet_fields
        )
        first_row = sheet_fields.rows[0]
        row_as_dict = self.default_client._map_row_to_dict(
            row=first_row, column_id_map=col_id_map
        )
        expected_row_as_dict = {
            "Project Name": "AIND Scientific Activities",
            "Project Code": "122-01-001-10",
            "Funding Institution": "Allen Institute",
            "Grant Number": None,
            "Investigators": "person.two@acme.org, J Smith, John Doe II",
        }
        self.assertEqual(expected_row_as_dict, row_as_dict)

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_get_parsed_sheet(self, mock_get_sheet: MagicMock):
        """Tests get_parsed_sheet method"""

        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        parsed_sheet = self.default_client.get_parsed_sheet(
            sheet_id=2014892103339908
        )
        expected_output = [
            {
                "Project Name": "AIND Scientific Activities",
                "Project Code": "122-01-001-10",
                "Funding Institution": "Allen Institute",
                "Grant Number": None,
                "Investigators": "person.two@acme.org, J Smith, John Doe II",
            },
            {
                "Project Name": None,
                "Project Code": "122-01-001-10",
                "Funding Institution": "Allen Institute",
                "Grant Number": None,
                "Investigators": "John Doe, person.one@acme.org",
            },
            {
                "Project Name": "v1omFISH",
                "Project Code": "121-01-010-10",
                "Funding Institution": "Allen Institute",
                "Grant Number": None,
                "Investigators": "person.one@acme.org, Jane Doe",
            },
        ]

        self.assertEqual(expected_output, parsed_sheet)

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_get_parsed_sheet_model_case_1(self, mock_get_sheet: MagicMock):
        """Tests get_parsed_sheet_model method with validate set to True and
        no validation errors"""

        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        parsed_sheet = self.default_client.get_parsed_sheet_model(
            sheet_id=2014892103339908,
            model=self.MockSheetModel1,
            validate=True,
        )
        expected_output = [
            self.MockSheetModel1(
                project_name="AIND Scientific Activities",
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                grant_number=None,
                investigators="person.two@acme.org, J Smith, John Doe II",
            ),
            self.MockSheetModel1(
                project_name=None,
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                grant_number=None,
                investigators="John Doe, person.one@acme.org",
            ),
            self.MockSheetModel1(
                project_name="v1omFISH",
                project_code="121-01-010-10",
                funding_institution="Allen Institute",
                grant_number=None,
                investigators="person.one@acme.org, Jane Doe",
            ),
        ]
        self.assertEqual(expected_output, parsed_sheet)

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_get_parsed_sheet_model_case_2(self, mock_get_sheet: MagicMock):
        """Tests get_parsed_sheet_model method with validate set to True and
        validation errors"""

        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        with self.assertRaises(ValidationError):
            self.default_client.get_parsed_sheet_model(
                sheet_id=2014892103339908,
                model=self.MockSheetModel2,
                validate=True,
            )

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_get_parsed_sheet_model_case_3(self, mock_get_sheet: MagicMock):
        """Tests get_parsed_sheet_model method with validate set to False and
        validation errors"""

        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        parsed_sheet = self.default_client.get_parsed_sheet_model(
            sheet_id=2014892103339908,
            model=self.MockSheetModel2,
            validate=False,
        )
        expected_output = [
            self.MockSheetModel2.model_construct(
                project_name="AIND Scientific Activities",
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                grant_number=None,
                investigators="person.two@acme.org, J Smith, John Doe II",
            ),
            self.MockSheetModel2.model_construct(
                project_name=None,
                project_code="122-01-001-10",
                funding_institution="Allen Institute",
                grant_number=None,
                investigators="John Doe, person.one@acme.org",
            ),
            self.MockSheetModel2.model_construct(
                project_name="v1omFISH",
                project_code="121-01-010-10",
                funding_institution="Allen Institute",
                grant_number=None,
                investigators="person.one@acme.org, Jane Doe",
            ),
        ]
        self.assertEqual(expected_output, parsed_sheet)


if __name__ == "__main__":
    unittest.main()
