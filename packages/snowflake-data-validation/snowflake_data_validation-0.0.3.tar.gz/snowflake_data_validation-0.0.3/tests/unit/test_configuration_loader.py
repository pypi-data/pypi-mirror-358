# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path

import pytest
from deepdiff import DeepDiff

from snowflake.snowflake_data_validation.configuration.configuration_loader import (
    ConfigurationLoader,
)
from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.configuration.model.validation_configuration import (
    ValidationConfiguration,
)
from snowflake.snowflake_data_validation.configuration.singleton import Singleton
from snowflake.snowflake_data_validation.utils.constants import (
    COLUMNAR_VALIDATION_KEY,
    METRICS_VALIDATION_KEY,
    ROW_VALIDATION_KEY,
    SCHEMA_VALIDATION_KEY,
    TOLERANCE_KEY,
    TYPE_MAPPING_FILE_PATH_KEY,
    DATA_VALIDATION_CONFIGURATION_FILE_YAML,
)


@pytest.fixture(autouse=True)
def singleton():
    Singleton._instances = {}


ASSETS_DIRECTORY_NAME = "assets"
TEST_CONFIGURATION_LOADER_DIRECTORY_NAME = "test_configuration_loader"


def test_load_configuration_model():
    configuration_file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_CONFIGURATION_LOADER_DIRECTORY_NAME)
        .joinpath("test_load_configuration_model")
        .joinpath(DATA_VALIDATION_CONFIGURATION_FILE_YAML)
    )

    configuration_loader = ConfigurationLoader(configuration_file_path)
    configuration_model = configuration_loader.get_configuration_model()

    assert configuration_model is not None

    assert configuration_model.source_platform == "SQL server"
    assert configuration_model.parallelization == False

    default_validation_configuration = {
        SCHEMA_VALIDATION_KEY: True,
        METRICS_VALIDATION_KEY: True,
        ROW_VALIDATION_KEY: False,
        COLUMNAR_VALIDATION_KEY: False,
    }

    validation_configuration_expected = ValidationConfiguration(
        **default_validation_configuration
    )

    validation_configuration_diff = DeepDiff(
        validation_configuration_expected,
        configuration_model.validation_configuration,
        ignore_order=True,
    )

    assert validation_configuration_diff == {}

    comparison_configuration_expected = {
        TOLERANCE_KEY: 0.01,
        TYPE_MAPPING_FILE_PATH_KEY: "/dir1/file.yaml",
    }

    comparison_configuration_diff = DeepDiff(
        comparison_configuration_expected,
        configuration_model.comparison_configuration,
        ignore_order=True,
    )

    assert comparison_configuration_diff == {}

    database_mappings_expected = {"example_database_2": "tgt_example_database"}

    database_mappings_diff = DeepDiff(
        database_mappings_expected,
        configuration_model.database_mappings,
        ignore_order=True,
    )

    assert database_mappings_diff == {}

    schema_mappings_expected = {"example_schema_2": "tgt_example_schema"}

    schema_mappings_diff = DeepDiff(
        schema_mappings_expected,
        configuration_model.schema_mappings,
        ignore_order=True,
    )

    assert schema_mappings_diff == {}

    tables_expected = [
        TableConfiguration(
            fully_qualified_name="example_database.example_schema.table_1",
            use_column_selection_as_exclude_list=True,
            column_selection_list=[
                "excluded_column_example_1",
                "excluded_column_example_2",
            ],
        ),
        TableConfiguration(
            fully_qualified_name="example_database.example_schema.table_2",
            use_column_selection_as_exclude_list=False,
            column_selection_list=[],
        ),
        TableConfiguration(
            fully_qualified_name="example_database_2.example_schema_2.table_3",
            target_fully_qualified_name="tgt_example_database.tgt_example_schema.tgt_example_table",
            target_database="tgt_example_database",
            target_schema="tgt_example_schema",
            target_name="tgt_example_table",
            use_column_selection_as_exclude_list=False,
            column_selection_list=[],
        ),
        TableConfiguration(
            fully_qualified_name="example_database.example_schema.table_4",
            use_column_selection_as_exclude_list=False,
            column_selection_list=[],
            validation_configuration={
                SCHEMA_VALIDATION_KEY: True,
                METRICS_VALIDATION_KEY: False,
                COLUMNAR_VALIDATION_KEY: False,
                ROW_VALIDATION_KEY: False,
            },
        ),
    ]

    assert configuration_model.tables == tables_expected


def test_load_configuration_model_file_not_found_exception():
    configuration_file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(DATA_VALIDATION_CONFIGURATION_FILE_YAML)
    )

    with (pytest.raises(FileNotFoundError) as ex_info):
        ConfigurationLoader(configuration_file_path)

    assert str(ex_info.value).startswith("Configuration file not found in")


def test_load_configuration_model_not_valid_name_exception():
    configuration_file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_CONFIGURATION_LOADER_DIRECTORY_NAME)
        .joinpath("data_validation.xml")
    )

    with (pytest.raises(Exception) as ex_info):
        ConfigurationLoader(configuration_file_path)

    assert (
        "data_validation.xml is not a valid configuration file name. The correct file name are conf.yaml and conf.yml"
        == str(ex_info.value)
    )


def test_load_configuration_model_reading_file_exception():
    configuration_file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_CONFIGURATION_LOADER_DIRECTORY_NAME)
        .joinpath("test_load_configuration_model_reading_file_exception")
        .joinpath(DATA_VALIDATION_CONFIGURATION_FILE_YAML)
    )

    with (pytest.raises(Exception) as ex_info):
        ConfigurationLoader(configuration_file_path)

    assert r"""An error occurred while loading the conf.yaml or conf.yml file:
4 validation errors for ConfigurationModel
source_platform
  Input should be a valid string [type=string_type, input_value=3045, input_type=int]
    For further information visit https://errors.pydantic.dev/2.11/v/string_type
target_platform
  Field required [type=missing, input_value={'source_platform': 3045,...n_selection_list': []}]}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/missing
output_directory_path
  Field required [type=missing, input_value={'source_platform': 3045,...n_selection_list': []}]}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/missing
parallelization
  Input should be a valid boolean, unable to interpret input [type=bool_parsing, input_value='DATA', input_type=str]
    For further information visit https://errors.pydantic.dev/2.11/v/bool_parsing""" == str(
        ex_info.value
    )


def test_load_configuration_model_path_file_is_none_exception():
    configuration_file_path: Path = None

    with (pytest.raises(ValueError) as ex_info):
        ConfigurationLoader(configuration_file_path)

    assert "The configuration file path cannot be None value" == str(ex_info.value)
