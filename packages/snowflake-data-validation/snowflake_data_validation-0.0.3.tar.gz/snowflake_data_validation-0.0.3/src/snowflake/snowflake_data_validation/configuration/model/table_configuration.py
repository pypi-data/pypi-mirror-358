from typing import Optional

from pydantic import BaseModel, model_validator
from typing_extensions import Self

from snowflake.snowflake_data_validation.configuration.model.validation_configuration import (
    ValidationConfiguration,
)
from snowflake.snowflake_data_validation.utils.helpers import (
    get_decomposed_fully_qualified_name,
)


class TableConfiguration(BaseModel):

    """Table configuration model.

    Args:
        pydantic.BaseModel (pydantic.BaseModel): pydantic BaseModel

    """

    fully_qualified_name: str
    use_column_selection_as_exclude_list: bool
    column_selection_list: list[str]
    validation_configuration: Optional[ValidationConfiguration] = None

    source_database: Optional[str] = None
    source_schema: Optional[str] = None
    source_table: Optional[str] = None
    target_name: Optional[str] = None

    target_fully_qualified_name: str = ""
    where_clause: str = ""
    target_where_clause: str = ""
    has_where_clause: bool = False
    target_database: Optional[str] = None
    target_schema: Optional[str] = None

    @model_validator(mode="after")
    def load(self) -> Self:
        self._load_source_decomposed_fully_qualified_name()
        self._load_target_fully_qualified_name()
        self._set_has_where_clause()
        self._set_target_where_clause()
        return self

    def _load_source_decomposed_fully_qualified_name(self) -> None:
        decomposed_tuple = get_decomposed_fully_qualified_name(
            self.fully_qualified_name
        )
        self.source_database = decomposed_tuple[0]
        self.source_schema = decomposed_tuple[1]
        self.source_table = decomposed_tuple[2]

    def _load_target_fully_qualified_name(self) -> None:
        if self.target_database is None:
            self.target_database = self.source_database

        if self.target_schema is None:
            self.target_schema = self.source_schema

        if self.target_name is None:
            self.target_name = self.source_table

        self.target_fully_qualified_name = (
            f"{self.target_database}.{self.target_schema}.{self.target_name}"
        )

    def _set_has_where_clause(self) -> None:
        self.has_where_clause = self.where_clause != ""

    def _set_target_where_clause(self) -> None:
        # Once we support column name mapping, this will need to be updated
        # to use the target column names instead of the source column names.
        self.target_where_clause: str = self.where_clause
