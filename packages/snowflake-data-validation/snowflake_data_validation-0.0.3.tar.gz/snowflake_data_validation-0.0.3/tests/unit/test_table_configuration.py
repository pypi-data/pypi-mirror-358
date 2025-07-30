import pytest
from deepdiff import DeepDiff
from pydantic_yaml import parse_yaml_raw_as

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.configuration.model.validation_configuration import (
    ValidationConfiguration,
)
from snowflake.snowflake_data_validation.utils.constants import (
    VALIDATION_CONFIGURATION_DEFAULT_VALUE,
)


def test_table_configuration_generation_default_values():
    table_configuration = TableConfiguration(
        fully_qualified_name="ex_database.ex_schema.ex_table",
        use_column_selection_as_exclude_list=True,
        column_selection_list=["excluded_column_1", "excluded_column_2"],
    )

    assert table_configuration.fully_qualified_name == "ex_database.ex_schema.ex_table"
    assert table_configuration.source_database == "ex_database"
    assert table_configuration.source_schema == "ex_schema"
    assert table_configuration.source_table == "ex_table"

    assert table_configuration.target_database == table_configuration.source_database
    assert table_configuration.target_schema == table_configuration.source_schema
    assert table_configuration.target_name == table_configuration.source_table

    assert table_configuration.use_column_selection_as_exclude_list == True
    assert table_configuration.column_selection_list == [
        "excluded_column_1",
        "excluded_column_2",
    ]

    assert table_configuration.where_clause == ""
    assert table_configuration.target_where_clause == ""
    assert table_configuration.has_where_clause == False

    assert table_configuration.validation_configuration is None


def test_table_configuration_generation_custom_values():
    default_validation_configuration = ValidationConfiguration(
        **VALIDATION_CONFIGURATION_DEFAULT_VALUE
    )
    table_configuration = TableConfiguration(
        fully_qualified_name="ex_database.ex_schema.ex_table",
        target_database="target_database",
        target_schema="target_schema",
        target_name="target_table",
        use_column_selection_as_exclude_list=True,
        column_selection_list=["excluded_column_1"],
        validation_configuration=default_validation_configuration,
        where_clause="id > 1 AND id < 100",
        target_where_clause="id > 1 AND id < 100",
        has_where_clause=True,
    )

    assert table_configuration.fully_qualified_name == "ex_database.ex_schema.ex_table"
    assert table_configuration.source_database == "ex_database"
    assert table_configuration.source_schema == "ex_schema"
    assert table_configuration.source_table == "ex_table"

    assert table_configuration.target_database == "target_database"
    assert table_configuration.target_schema == "target_schema"
    assert table_configuration.target_name == "target_table"

    assert table_configuration.use_column_selection_as_exclude_list == True
    assert table_configuration.column_selection_list == ["excluded_column_1"]

    validation_configuration_diff = DeepDiff(
        default_validation_configuration,
        table_configuration.validation_configuration,
        ignore_order=True,
    )

    assert table_configuration.where_clause == "id > 1 AND id < 100"
    assert table_configuration.target_where_clause == "id > 1 AND id < 100"
    assert table_configuration.has_where_clause == True

    assert validation_configuration_diff == {}


def test_table_configuration_generation_pydantic_default_values():
    file_content = r"""fully_qualified_name: example_database.example_schema.table
use_column_selection_as_exclude_list: true
column_selection_list:
  - excluded_column_example_1
  - excluded_column_example_2
"""

    table_configuration = parse_yaml_raw_as(TableConfiguration, file_content)

    assert table_configuration is not None

    assert (
        table_configuration.fully_qualified_name
        == "example_database.example_schema.table"
    )
    assert table_configuration.source_database == "example_database"
    assert table_configuration.source_schema == "example_schema"
    assert table_configuration.source_table == "table"

    assert table_configuration.target_database == table_configuration.source_database
    assert table_configuration.target_schema == table_configuration.source_schema
    assert table_configuration.target_name == table_configuration.source_table

    assert table_configuration.use_column_selection_as_exclude_list == True
    assert table_configuration.column_selection_list == [
        "excluded_column_example_1",
        "excluded_column_example_2",
    ]

    assert table_configuration.where_clause == ""
    assert table_configuration.target_where_clause == ""
    assert table_configuration.has_where_clause == False

    assert table_configuration.validation_configuration is None


def test_table_configuration_generation_pydantic_custom_values():
    file_content = r"""fully_qualified_name: example_database.example_schema.table
use_column_selection_as_exclude_list: false
column_selection_list: []
target_database: target_database
target_schema: target_schema
target_name: target_table
validation_configuration:
    columnar_validation: true
    metrics_validation: true
    row_validation: true
    schema_validation: true
where_clause: id > 1 AND id < 100
"""
    default_validation_configuration = ValidationConfiguration(
        **VALIDATION_CONFIGURATION_DEFAULT_VALUE
    )
    table_configuration = parse_yaml_raw_as(TableConfiguration, file_content)

    assert table_configuration is not None

    assert (
        table_configuration.fully_qualified_name
        == "example_database.example_schema.table"
    )
    assert table_configuration.source_database == "example_database"
    assert table_configuration.source_schema == "example_schema"
    assert table_configuration.source_table == "table"

    assert table_configuration.target_database == "target_database"
    assert table_configuration.target_schema == "target_schema"
    assert table_configuration.target_name == "target_table"

    assert table_configuration.use_column_selection_as_exclude_list == False
    assert table_configuration.column_selection_list == []

    validation_configuration_diff = DeepDiff(
        default_validation_configuration,
        table_configuration.validation_configuration,
        ignore_order=True,
    )

    assert validation_configuration_diff == {}

    assert table_configuration.where_clause == "id > 1 AND id < 100"
    assert table_configuration.target_where_clause == "id > 1 AND id < 100"
    assert table_configuration.has_where_clause == True


def test_table_configuration_generation_pydantic_load_source_decomposed_fully_qualified_name_exception():
    file_content = r"""fully_qualified_name: table
use_column_selection_as_exclude_list: false
column_selection_list: []
"""

    with (pytest.raises(ValueError) as ex_info):
        parse_yaml_raw_as(TableConfiguration, file_content)

    assert r"""1 validation error for TableConfiguration
  Value error, Invalid fully qualified name: table. Expected format: database.schema.table [type=value_error, input_value={'fully_qualified_name': ...umn_selection_list': []}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/value_error""" == str(
        ex_info.value
    )


def test_table_configuration_generation_pydantic_load_missing_fields_exception():
    file_content = r"""fully_qualified_name: example_database.example_schema.table"""

    with (pytest.raises(ValueError) as ex_info):
        parse_yaml_raw_as(TableConfiguration, file_content)

    assert r"""2 validation errors for TableConfiguration
use_column_selection_as_exclude_list
  Field required [type=missing, input_value={'fully_qualified_name': ...e.example_schema.table'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/missing
column_selection_list
  Field required [type=missing, input_value={'fully_qualified_name': ...e.example_schema.table'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/missing""" == str(
        ex_info.value
    )
