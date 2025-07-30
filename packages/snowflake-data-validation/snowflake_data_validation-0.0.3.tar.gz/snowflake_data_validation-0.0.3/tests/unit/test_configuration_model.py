import pytest
from deepdiff import DeepDiff
from pydantic_yaml import parse_yaml_raw_as

from snowflake.snowflake_data_validation.configuration.model.configuration_model import (
    ConfigurationModel,
)
from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.configuration.model.validation_configuration import (
    ValidationConfiguration,
)
from snowflake.snowflake_data_validation.utils.constants import (
    VALIDATION_CONFIGURATION_DEFAULT_VALUE,
    SCHEMA_VALIDATION_KEY,
    METRICS_VALIDATION_KEY,
    COLUMNAR_VALIDATION_KEY,
    ROW_VALIDATION_KEY,
    TOLERANCE_KEY,
    TYPE_MAPPING_FILE_PATH_KEY,
)

VALIDATION_CONFIGURATION = {
    SCHEMA_VALIDATION_KEY: True,
    METRICS_VALIDATION_KEY: True,
    COLUMNAR_VALIDATION_KEY: False,
    ROW_VALIDATION_KEY: False,
}

COMPARISON_CONFIGURATION = {
    TOLERANCE_KEY: 1.23,
    TYPE_MAPPING_FILE_PATH_KEY: "/dir1/file.yaml",
}

SQL_SERVER_SOURCE_PLATFORM = "SQL server"
SNOWFLAKE_TARGET_PLATFORM = "Snowflake"
OUTPUT_DIRECTORY_PATH = "/test/reports"


def test_configuration_model_generation_default_values():
    default_validation_configuration = ValidationConfiguration(
        **VALIDATION_CONFIGURATION_DEFAULT_VALUE
    )
    configuration_model = ConfigurationModel(
        source_platform=SQL_SERVER_SOURCE_PLATFORM,
        target_platform=SNOWFLAKE_TARGET_PLATFORM,
        output_directory_path=OUTPUT_DIRECTORY_PATH,
    )
    assert configuration_model.source_platform == SQL_SERVER_SOURCE_PLATFORM
    assert configuration_model.parallelization == False
    assert configuration_model.comparison_configuration is None
    assert configuration_model.tables == []

    validation_configuration_diff = DeepDiff(
        default_validation_configuration,
        configuration_model.validation_configuration,
        ignore_order=True,
    )

    assert validation_configuration_diff == {}


def test_configuration_model_generation_custom_values():
    table_configuration = TableConfiguration(
        fully_qualified_name="ex_database.ex_schema.ex_table",
        target_database="tgt_example_database",
        target_schema="tgt_example_schema",
        target_name="tgt_example_table",
        use_column_selection_as_exclude_list=True,
        column_selection_list=["excluded_column_1", "excluded_column_2"],
    )
    default_validation_configuration = ValidationConfiguration(
        **VALIDATION_CONFIGURATION_DEFAULT_VALUE
    )

    configuration_model = ConfigurationModel(
        source_platform=SQL_SERVER_SOURCE_PLATFORM,
        target_platform=SNOWFLAKE_TARGET_PLATFORM,
        output_directory_path=OUTPUT_DIRECTORY_PATH,
        parallelization=True,
        validation_configuration=default_validation_configuration,
        comparison_configuration=COMPARISON_CONFIGURATION,
        tables=[table_configuration],
    )

    assert configuration_model.source_platform == SQL_SERVER_SOURCE_PLATFORM
    assert configuration_model.parallelization == True

    validation_configuration_diff = DeepDiff(
        default_validation_configuration,
        configuration_model.validation_configuration,
        ignore_order=True,
    )

    assert validation_configuration_diff == {}

    comparison_configuration_diff = DeepDiff(
        COMPARISON_CONFIGURATION,
        configuration_model.comparison_configuration,
        ignore_order=True,
    )

    assert comparison_configuration_diff == {}

    assert len(configuration_model.tables) == 1
    assert configuration_model.tables[0] == table_configuration


def test_configuration_model_generation_pydantic_default_values():
    file_content = f"""source_platform: {SQL_SERVER_SOURCE_PLATFORM}
target_platform: {SNOWFLAKE_TARGET_PLATFORM}
output_directory_path: {OUTPUT_DIRECTORY_PATH}"""
    default_validation_configuration = ValidationConfiguration(
        **VALIDATION_CONFIGURATION_DEFAULT_VALUE
    )

    model = parse_yaml_raw_as(ConfigurationModel, file_content)

    assert model is not None

    assert model.source_platform == SQL_SERVER_SOURCE_PLATFORM
    assert model.parallelization == False
    assert model.comparison_configuration is None
    assert model.tables == []

    validation_configuration_diff = DeepDiff(
        default_validation_configuration,
        model.validation_configuration,
        ignore_order=True,
    )

    assert validation_configuration_diff == {}


def test_configuration_model_generation_pydantic_custom_values():
    file_content = r"""source_platform: SQL server
target_platform: Snowflake
output_directory_path: /test/reports
parallelization: true
validation_configuration:
  columnar_validation: false
  metrics_validation: true
  row_validation: false
  schema_validation: true
comparison_configuration:
  tolerance: 1.23
  type_mapping_file_path: /dir1/file.yaml
tables:
  - fully_qualified_name: ex_database.ex_schema.ex_table
    use_column_selection_as_exclude_list: true
    column_selection_list:
      - excluded_column_example_1
      - excluded_column_example_2
"""
    default_validation_configuration = ValidationConfiguration(
        **VALIDATION_CONFIGURATION
    )
    model = parse_yaml_raw_as(ConfigurationModel, file_content)

    assert model is not None

    assert model.source_platform == SQL_SERVER_SOURCE_PLATFORM
    assert model.parallelization == True

    validation_configuration_diff = DeepDiff(
        default_validation_configuration,
        model.validation_configuration,
        ignore_order=True,
    )

    assert validation_configuration_diff == {}

    comparison_configuration_diff = DeepDiff(
        COMPARISON_CONFIGURATION,
        model.comparison_configuration,
        ignore_order=True,
    )

    assert comparison_configuration_diff == {}

    assert len(model.tables) == 1

    table_configuration = TableConfiguration(
        fully_qualified_name="ex_database.ex_schema.ex_table",
        use_column_selection_as_exclude_list=True,
        column_selection_list=[
            "excluded_column_example_1",
            "excluded_column_example_2",
        ],
    )

    assert model.tables[0] == table_configuration


def test_configuration_model_generation_pydantic_load_missing_fields_exception():
    file_content = r"""field: value"""

    with (pytest.raises(ValueError) as ex_info):
        parse_yaml_raw_as(ConfigurationModel, file_content)

    assert r"""3 validation errors for ConfigurationModel
source_platform
  Field required [type=missing, input_value={'field': 'value'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/missing
target_platform
  Field required [type=missing, input_value={'field': 'value'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/missing
output_directory_path
  Field required [type=missing, input_value={'field': 'value'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/missing""" == str(
        ex_info.value
    )


def test_configuration_model_with_report_path():
    """Test that ConfigurationModel correctly handles the output_directory_path field."""
    file_content = r"""source_platform: SQL server
target_platform: Snowflake
parallelization: false
output_directory_path: /custom/output/path
validation_configuration:
  schema_validation: true
  metrics_validation: true
  columnar_validation: false
  row_validation: false
tables:
  - fully_qualified_name: example_database.example_schema.table_1
    use_column_selection_as_exclude_list: false
    column_selection_list: []
"""

    model = parse_yaml_raw_as(ConfigurationModel, file_content)

    assert model is not None
    assert model.source_platform == "SQL server"
    assert model.parallelization == False
    assert model.output_directory_path == "/custom/output/path"
    assert len(model.tables) == 1


def test_configuration_model_missing_output_directory_path_exception():
    """Test that ConfigurationModel raises validation error when output_directory_path is missing."""
    file_content_no_output_directory = r"""source_platform: SQL server"""

    with pytest.raises(ValueError) as ex_info:
        parse_yaml_raw_as(ConfigurationModel, file_content_no_output_directory)

    # Check that the error mentions output_directory_path is required
    assert "output_directory_path" in str(ex_info.value)
    assert "Field required" in str(ex_info.value)
