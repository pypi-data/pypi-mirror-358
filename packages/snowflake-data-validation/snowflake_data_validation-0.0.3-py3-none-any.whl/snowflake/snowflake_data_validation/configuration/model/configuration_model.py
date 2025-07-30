from typing import Optional, Union

from pydantic import BaseModel, model_validator
from typing_extensions import Self

from snowflake.snowflake_data_validation.configuration.model.connection_types import (
    Connection,
)
from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.configuration.model.validation_configuration import (
    ValidationConfiguration,
)
from snowflake.snowflake_data_validation.utils.constants import (
    VALIDATION_CONFIGURATION_DEFAULT_VALUE,
)


class ConfigurationModel(BaseModel):

    """Configuration model.

    Args:
        pydantic.BaseModel (pydantic.BaseModel): pydantic BaseModel

    """

    source_platform: str
    target_platform: str
    output_directory_path: str
    parallelization: bool = False
    source_connection: Optional[Connection] = None
    target_connection: Optional[Connection] = None
    source_validation_files_path: Optional[str] = None
    target_validation_files_path: Optional[str] = None
    validation_configuration: ValidationConfiguration = ValidationConfiguration(
        **VALIDATION_CONFIGURATION_DEFAULT_VALUE
    )
    comparison_configuration: Optional[dict[str, Union[str, float]]] = None
    database_mappings: dict[str, str] = {}
    schema_mappings: dict[str, str] = {}
    tables: list[TableConfiguration] = []

    @model_validator(mode="after")
    def load(self) -> Self:
        self._set_target_fully_qualified_name()
        return self

    def _set_target_fully_qualified_name(self) -> None:
        for table in self.tables:
            self._load_target_fully_qualified_name(table)

    def _load_target_fully_qualified_name(self, table: TableConfiguration) -> None:
        if self.database_mappings.get(table.source_database, None) is not None:
            table.target_database = self.database_mappings[table.source_database]

        if self.schema_mappings.get(table.source_schema, None) is not None:
            table.target_schema = self.schema_mappings[table.source_schema]

        table.target_fully_qualified_name = (
            f"{table.target_database}.{table.target_schema}.{table.target_name}"
        )
