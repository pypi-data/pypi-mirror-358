"""Module to instantiate a client to connect to Smartsheet and provide helpful
methods to retrieve data."""

from functools import lru_cache
from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel, Field, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from smartsheet import Smartsheet

from aind_smartsheet_api.models import SheetFields, SheetRow

T = TypeVar("T", bound=BaseModel)


class SmartsheetSettings(BaseSettings):
    """Configuration class. Mostly a wrapper around smartsheet.Smartsheet
    class constructor arguments."""

    access_token: SecretStr = Field(
        ..., description="API token can be created in Smartsheet UI"
    )
    user_agent: Optional[str] = Field(
        default=None,
        description=(
            "The user agent to use when making requests. "
            "Helps identify requests."
        ),
    )
    max_connections: int = Field(
        default=8, description="Maximum connection pool size."
    )
    sheet_id_map: Optional[Dict[str, int]] = Field(
        default=None, description="Optional dictionary to store sheet ids."
    )
    model_config = SettingsConfigDict(env_prefix="SMARTSHEET_", extra="forbid")


class SmartsheetClient:
    """Main client to connect to a Smartsheet sheet. Requires an API token
    and the sheet id."""

    def __init__(self, smartsheet_settings: SmartsheetSettings):
        """
        Class constructor
        Parameters
        ----------
        smartsheet_settings : SmartsheetSettings
        """
        self.smartsheet_settings = smartsheet_settings
        self.smartsheet_client = Smartsheet(
            user_agent=self.smartsheet_settings.user_agent,
            max_connections=self.smartsheet_settings.max_connections,
            access_token=(
                self.smartsheet_settings.access_token.get_secret_value()
            ),
        )

    @lru_cache(maxsize=1)
    def get_raw_sheet(self, sheet_id: int) -> str:
        """
        Retrieve the sheet as a json dictionary..
        Parameters
        ----------
        sheet_id : int

        Returns
        -------
        str
          Raises an error if there is an issue retrieving the sheet.

        """
        smartsheet_response = self.smartsheet_client.Sheets.get_sheet(sheet_id)
        return smartsheet_response.to_json()

    def get_sheet_fields(self, sheet_id: int) -> SheetFields:
        """

        Parameters
        ----------
        sheet_id : int

        Returns
        -------
        SheetFields

        """
        raw_sheet = self.get_raw_sheet(sheet_id=sheet_id)
        return SheetFields.model_validate_json(raw_sheet)

    @staticmethod
    def _column_id_map(sheet_fields: SheetFields) -> Dict[int, str]:
        """
        SmartSheet uses integer ids for the columns. We need a way to
        map the column titles to the ids so we can retrieve information using
        just the titles.
        Parameters
        ----------
        sheet_fields : SheetFields

        Returns
        -------
        Dict[int, str]

        """
        return {c.id: c.title for c in sheet_fields.columns}

    @staticmethod
    def _map_row_to_dict(
        row: SheetRow, column_id_map: Dict[int, str]
    ) -> Dict[str, Any]:
        """
        Maps a row into a dictionary that maps the column names to their values
        Parameters
        ----------
        row : SheetRow
          A SheetRow that will be parsed. This a list of cells with a columnId
          and a cell value.
        column_id_map: Dict[int, str]
          Map of column ids into the column names

        Returns
        -------
        Dict[str, Any]
          The list of row cells is converted to a dictionary.

        """
        output_dict = {}
        for cell in row.cells:
            column_id = cell.columnId
            column_name = column_id_map[column_id]
            output_dict[column_name] = cell.value
        return output_dict

    def get_parsed_sheet(self, sheet_id: int) -> List[Dict[str, Any]]:
        """
        Parse raw sheet json into basic dictionary of {"name": "value"}
        Parameters
        ----------
        sheet_id : int

        Returns
        -------
        Dict[str, Any]

        """

        sheet_fields = self.get_sheet_fields(sheet_id=sheet_id)
        column_id_map = self._column_id_map(sheet_fields=sheet_fields)
        parsed_rows = list()
        for row in sheet_fields.rows:
            row_dict = self._map_row_to_dict(row, column_id_map=column_id_map)
            parsed_rows.append(row_dict)
        return parsed_rows

    def get_parsed_sheet_model(
        self, sheet_id: int, model: Type[T], validate: bool = True
    ) -> List[Type[T]]:
        """
        Parse raw sheet json into basic dictionary of {"name": "value"}
        Parameters
        ----------
        sheet_id : int
        model : T
          BaseModel type
        validate : bool
          If set to True, will raise errors if pydantic validation fails.
          If set to False, will use model_construct in places where validation
          fails. Default is True.

        Returns
        -------
        List[Type[T]]

        """

        sheet_fields = self.get_sheet_fields(sheet_id=sheet_id)
        column_id_map = self._column_id_map(sheet_fields=sheet_fields)
        parsed_rows = list()
        for row in sheet_fields.rows:
            row_dict = self._map_row_to_dict(row, column_id_map=column_id_map)
            try:
                row_as_model = model.model_validate(row_dict)
                parsed_rows.append(row_as_model)

            except ValidationError as e:
                if validate:
                    raise e
                else:
                    row_as_model = model.model_construct(**row_dict)
                    parsed_rows.append(row_as_model)
        return parsed_rows
