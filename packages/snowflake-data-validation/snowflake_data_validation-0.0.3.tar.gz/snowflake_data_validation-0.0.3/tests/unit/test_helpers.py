# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import MagicMock

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from deepdiff import DeepDiff

ASSETS_DIRECTORY_NAME = "assets"
DUMMY_CONFIGURATION_JSON_FILE_NAME = "dummy_configuration_file.json"
DUMMY_METRICS_TEMPLATE_YAML_FILE_NAME = "dummy_metrics_template.yaml"
DUMMY_METRICS_TEMPLATE_DATATYPES_YAML_FILE_NAME = (
    "dummy_metrics_template_datatypes.yaml"
)
DUMMY_DATATYPES_TEMPLATE_YAML_FILE_NAME = "dummy_datatypes_template.yaml"
DUMMY_DATATYPES_NORMALIZATION_TEMPLATE_YAML_FILE_NAME = (
    "dummy_datatypes_normalization_template.yaml"
)
NOT_EXISTS_TEMPLATE_YAML_FILE_NAME = "not_exists.yaml"
NOT_VALID_FORMAT_TEMPLATE_YAML_FILE_NAME = "not_valid_format.yaml"
TEST_HELPERS_DIRECTORY_NAME = "test_helpers"


def test_read_json_file():
    from snowflake.snowflake_data_validation.utils.helpers import read_json_file
    from pathlib import Path

    file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_HELPERS_DIRECTORY_NAME)
        .joinpath(DUMMY_CONFIGURATION_JSON_FILE_NAME)
    )
    file_path_str = str(file_path)
    model = read_json_file(file_path_str)

    assert model is not None

    expected_model = {"key1": "value1", "key2": "value2"}
    diff = DeepDiff(
        expected_model,
        model,
        ignore_order=True,
    )

    assert diff == {}


def test_get_schema_name():
    from snowflake.snowflake_data_validation.utils.helpers import get_schema_name

    assert get_schema_name("database.schema.table") == "schema"
    assert get_schema_name("schema.table") == "schema"
    assert get_schema_name("table") is None
    assert get_schema_name("") is None
    assert get_schema_name("database..table") == ""


def test_get_table_name():
    from snowflake.snowflake_data_validation.utils.helpers import get_table_name

    assert get_table_name("database.schema.table") == "table"
    assert get_table_name("schema.table") == "table"
    assert get_table_name("table") == "table"
    assert get_table_name("") == ""
    assert get_table_name("database..table") == "table"


def test_get_decomposed_fully_qualified_name():
    from snowflake.snowflake_data_validation.utils.helpers import (
        get_decomposed_fully_qualified_name,
    )

    assert get_decomposed_fully_qualified_name("database.schema.table") == (
        "database",
        "schema",
        "table",
    )


def test_test_get_decomposed_fully_qualified_name_exception():
    from snowflake.snowflake_data_validation.utils.helpers import (
        get_decomposed_fully_qualified_name,
    )

    with (pytest.raises(ValueError) as ex_info):
        get_decomposed_fully_qualified_name("123")

    assert (
        "Invalid fully qualified name: 123. Expected format: database.schema.table"
        == str(ex_info.value)
    )


def test_copy_templates_to_temp_dir():
    from snowflake.snowflake_data_validation.utils.helpers import (
        copy_templates_to_temp_dir,
    )
    from pathlib import Path
    import os
    import tempfile

    source_templates_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_HELPERS_DIRECTORY_NAME)
    )
    core_templates_path = source_templates_path
    expected_files_copied_path_collection = sorted(os.listdir(source_templates_path))

    with tempfile.TemporaryDirectory() as temp_dir:
        copy_templates_to_temp_dir(
            str(source_templates_path), str(core_templates_path), str(temp_dir)
        )

        files_copied_collection = sorted(os.listdir(temp_dir))
        assert files_copied_collection == expected_files_copied_path_collection


def test_normalize_dataframe():
    from snowflake.snowflake_data_validation.utils.helpers import (
        normalize_dataframe,
    )
    import pandas as pd

    df = pd.DataFrame({"column1": [1, 2, 3, 4], "column2": ["a", "b", "c", "d"]})

    expected_df = pd.DataFrame(
        {"COLUMN1": [1, 2, 3, 4], "COLUMN2": ["a", "b", "c", "d"]}
    )

    assert normalize_dataframe(df).equals(expected_df)


def test_create_temp_dir():
    from snowflake.snowflake_data_validation.utils.helpers import create_temp_dir
    from pathlib import Path

    temporal_dir_path = create_temp_dir("test_prefix")
    assert Path(temporal_dir_path).exists() == True


def test_create_new_table_metadata_row():
    from snowflake.snowflake_data_validation.utils.helpers import (
        create_new_table_metadata_row,
    )
    import pandas as pd

    columns = ["COLUMN1", "COLUMN2", "COLUMN3", "COLUMN4", "COLUMN5"]
    validated_value = "failed"
    column = "column"
    source_value = "value_source"
    target_value = "target_value"
    comment = "comment"

    df = create_new_table_metadata_row(
        columns, validated_value, column, source_value, target_value, comment
    )

    expected_df = pd.DataFrame(
        {
            "COLUMN1": [validated_value],
            "COLUMN2": [column],
            "COLUMN3": [source_value],
            "COLUMN4": [target_value],
            "COLUMN5": [comment],
        }
    )

    assert df.equals(expected_df)


def test_create_new_column_metadata_row():
    from snowflake.snowflake_data_validation.utils.helpers import (
        create_new_column_metadata_row,
    )
    import pandas as pd

    columns = ["COLUMN1", "COLUMN2", "COLUMN3", "COLUMN4", "COLUMN5"]
    column = "column"
    metric = "metric"
    source_value = "value_source"
    target_value = "target_value"
    comment = "comment"

    df = create_new_column_metadata_row(
        columns, column, metric, source_value, target_value, comment
    )

    expected_df = pd.DataFrame(
        {
            "COLUMN1": [column],
            "COLUMN2": [metric],
            "COLUMN3": [source_value],
            "COLUMN4": [target_value],
            "COLUMN5": [comment],
        }
    )

    assert df.equals(expected_df)


def test_is_numeric():
    from snowflake.snowflake_data_validation.utils.helpers import is_numeric

    assert is_numeric(123) == True
    assert is_numeric(123.45) == True
    assert is_numeric("123") == True
    assert is_numeric("abc") == False
    assert is_numeric(None) == False


def test_load_metrics_templates_from_yaml():
    from snowflake.snowflake_data_validation.utils.helpers import (
        load_metrics_templates_from_yaml,
    )
    from pathlib import Path
    import pandas as pd

    file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_HELPERS_DIRECTORY_NAME)
        .joinpath(DUMMY_METRICS_TEMPLATE_YAML_FILE_NAME)
    )

    datatypes_normalization_templates = {
        "TYPE1": "TO_CHAR({{ metric_query }}, 'N4')",
        "TYPE2": "TO_CHAR({{ metric_query }})",
        "TYPE3": "TO_CHAR({{ metric_query }}, 'N1')",
    }

    df = load_metrics_templates_from_yaml(file_path, datatypes_normalization_templates)

    expected_df = pd.DataFrame(
        {
            "type": ["TYPE1", "TYPE1", "TYPE2"],
            "metric": ["METRIC1", "METRIC2", "METRIC1"],
            "template": [
                'METRIC1("{{ col_name }}")',
                'METRIC2("{{ col_name }}")',
                'METRIC1("{{ col_name }}")',
            ],
            "normalization": [
                "TO_CHAR({{ metric_query }}, 'N4')",
                "TO_CHAR({{ metric_query }}, 'N4')",
                "TO_CHAR({{ metric_query }})",
            ],
        }
    )
    assert df.equals(expected_df)


def test_load_metrics_templates_datatypes_from_yaml():
    from snowflake.snowflake_data_validation.utils.helpers import (
        load_metrics_templates_from_yaml,
    )
    from pathlib import Path
    import pandas as pd

    file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_HELPERS_DIRECTORY_NAME)
        .joinpath(DUMMY_METRICS_TEMPLATE_DATATYPES_YAML_FILE_NAME)
    )

    datatypes_normalization_templates = {
        "TYPE1": "TO_CHAR({{ metric_query }}, 'N4')",
        "TYPE2": "TO_CHAR({{ metric_query }})",
        "TYPE3": "TO_CHAR({{ metric_query }}, 'YYYY-DD-MM')",
    }

    df = load_metrics_templates_from_yaml(file_path, datatypes_normalization_templates)

    expected_df = pd.DataFrame(
        {
            "type": ["TYPE1", "TYPE1", "TYPE2"],
            "metric": ["METRIC1", "METRIC2", "METRIC1"],
            "template": [
                'METRIC1("{{ col_name }}")',
                'METRIC2("{{ col_name }}")',
                'METRIC1("{{ col_name }}")',
            ],
            "normalization": [
                "TO_CHAR({{ metric_query }}, 'N4')",
                "TO_CHAR({{ metric_query }})",
                "TO_CHAR({{ metric_query }}, 'YYYY-DD-MM')",
            ],
        }
    )
    assert df.equals(expected_df)


def test_load_metrics_templates_from_yaml_file_not_found_exception():
    from snowflake.snowflake_data_validation.utils.helpers import (
        load_metrics_templates_from_yaml,
    )
    from pathlib import Path

    with (pytest.raises(FileNotFoundError) as ex_info):
        file_path = (
            Path(__file__)
            .parent.joinpath(ASSETS_DIRECTORY_NAME)
            .joinpath(TEST_HELPERS_DIRECTORY_NAME)
            .joinpath(NOT_EXISTS_TEMPLATE_YAML_FILE_NAME)
        )
        load_metrics_templates_from_yaml(file_path, {})

    assert (str(ex_info.value)).startswith("Template file not found at:")


def test_load_metrics_templates_from_yaml_missing_datatype_key_exception():
    from snowflake.snowflake_data_validation.utils.helpers import (
        load_metrics_templates_from_yaml,
    )
    from pathlib import Path

    with (pytest.raises(RuntimeError) as ex_info):
        file_path = (
            Path(__file__)
            .parent.joinpath(ASSETS_DIRECTORY_NAME)
            .joinpath(TEST_HELPERS_DIRECTORY_NAME)
            .joinpath(DUMMY_METRICS_TEMPLATE_DATATYPES_YAML_FILE_NAME)
        )
        load_metrics_templates_from_yaml(file_path, {})

    assert (
        str(ex_info.value) == "Missing TYPE1 datatype in datatypes normalization file."
    )


def test_load_metrics_templates_from_yaml_not_valid_format_exception():
    from snowflake.snowflake_data_validation.utils.helpers import (
        load_metrics_templates_from_yaml,
    )

    yaml_content = r"""key1: value1
key2
  - value2
key3: [value3, value4"""

    with (pytest.raises(RuntimeError) as ex_info):
        file_path = MagicMock()
        file_path.read_text.return_value = yaml_content
        file_path.name = "not_valid_format.yaml"
        load_metrics_templates_from_yaml(file_path, {})

    expected_error_message = r"""Error in the format of not_valid_format.yaml. Please check the following:
Incorrect indentation: YAML relies heavily on consistent indentation using spaces (not tabs).
Invalid characters: Certain characters might need to be quoted.
Syntax errors in lists or dictionaries: Incorrect use of hyphens for list items or nested structures.
Special characters not quoted: If a string contains special characters it might need to be enclosed in quotes."""

    assert expected_error_message == str(ex_info.value)


def test_reformat_metrics_yaml_data():
    from snowflake.snowflake_data_validation.utils.helpers import (
        _reformat_metrics_yaml_data,
    )

    import yaml
    from pathlib import Path

    file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_HELPERS_DIRECTORY_NAME)
        .joinpath(DUMMY_METRICS_TEMPLATE_YAML_FILE_NAME)
    )

    datatypes_normalization_templates = {
        "TYPE1": "TO_CHAR({{ metric_query }}, 'N4')",
        "TYPE2": "TO_CHAR({{ metric_query }})",
    }

    file_content = file_path.read_text()
    yaml_data = yaml.safe_load(file_content)
    yaml_data_reformatted = _reformat_metrics_yaml_data(
        yaml_data, datatypes_normalization_templates
    )

    expected_model = {
        "type": ["TYPE1", "TYPE1", "TYPE2"],
        "metric": ["METRIC1", "METRIC2", "METRIC1"],
        "template": [
            'METRIC1("{{ col_name }}")',
            'METRIC2("{{ col_name }}")',
            'METRIC1("{{ col_name }}")',
        ],
        "normalization": [
            "TO_CHAR({{ metric_query }}, 'N4')",
            "TO_CHAR({{ metric_query }}, 'N4')",
            "TO_CHAR({{ metric_query }})",
        ],
    }

    diff = DeepDiff(
        expected_model,
        yaml_data_reformatted,
        ignore_order=True,
    )

    assert diff == {}


def test_load_datatypes_templates_from_yaml():
    from snowflake.snowflake_data_validation.utils.helpers import (
        load_datatypes_templates_from_yaml,
    )
    from pathlib import Path
    import pandas as pd

    file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_HELPERS_DIRECTORY_NAME)
        .joinpath(DUMMY_DATATYPES_TEMPLATE_YAML_FILE_NAME)
    )
    df = load_datatypes_templates_from_yaml(file_path, "some_dialect")

    expected_df = pd.DataFrame(
        {
            "some_dialect": ["TYPE1", "TYPE2"],
            "DIALECT1": ["TYPE1_DIALECT1", "TYPE2_DIALECT1"],
        }
    )
    assert df.equals(expected_df)


def test_load_datatypes_templates_from_yaml_file_not_found_exception():
    from snowflake.snowflake_data_validation.utils.helpers import (
        load_datatypes_templates_from_yaml,
    )
    from pathlib import Path

    with (pytest.raises(FileNotFoundError) as ex_info):
        file_path = (
            Path(__file__)
            .parent.joinpath(ASSETS_DIRECTORY_NAME)
            .joinpath(TEST_HELPERS_DIRECTORY_NAME)
            .joinpath(NOT_EXISTS_TEMPLATE_YAML_FILE_NAME)
        )
        load_datatypes_templates_from_yaml(file_path, "some_dialect")

    assert (str(ex_info.value)).startswith("Template file not found at:")


def test_load_datatypes_templates_from_yaml_not_valid_format_exception():
    from snowflake.snowflake_data_validation.utils.helpers import (
        load_metrics_templates_from_yaml,
    )

    yaml_content = r"""key1: value1
key2
  - value2
key3: [value3, value4"""

    with (pytest.raises(RuntimeError) as ex_info):
        file_path = MagicMock()
        file_path.read_text.return_value = yaml_content
        file_path.name = "not_valid_format.yaml"
        load_metrics_templates_from_yaml(file_path, {})

    expected_error_message = r"""Error in the format of not_valid_format.yaml. Please check the following:
Incorrect indentation: YAML relies heavily on consistent indentation using spaces (not tabs).
Invalid characters: Certain characters might need to be quoted.
Syntax errors in lists or dictionaries: Incorrect use of hyphens for list items or nested structures.
Special characters not quoted: If a string contains special characters it might need to be enclosed in quotes."""

    assert expected_error_message == str(ex_info.value)


def test_reformat_datatypes_yaml_data():
    from snowflake.snowflake_data_validation.utils.helpers import (
        _reformat_datatypes_yaml_data,
    )

    import yaml
    from pathlib import Path

    file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_HELPERS_DIRECTORY_NAME)
        .joinpath(DUMMY_DATATYPES_TEMPLATE_YAML_FILE_NAME)
    )

    file_content = file_path.read_text()
    yaml_data = yaml.safe_load(file_content)
    yaml_data_reformatted = _reformat_datatypes_yaml_data(yaml_data, "some_dialect")

    expected_model = {
        "some_dialect": ["TYPE1", "TYPE2"],
        "DIALECT1": ["TYPE1_DIALECT1", "TYPE2_DIALECT1"],
    }

    diff = DeepDiff(
        expected_model,
        yaml_data_reformatted,
        ignore_order=True,
    )

    assert diff == {}


def test_load_datatypes_normalization_templates_from_yaml():
    from snowflake.snowflake_data_validation.utils.helpers import (
        load_datatypes_normalization_templates_from_yaml,
    )
    from pathlib import Path
    import pandas as pd

    file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_HELPERS_DIRECTORY_NAME)
        .joinpath(DUMMY_DATATYPES_NORMALIZATION_TEMPLATE_YAML_FILE_NAME)
    )
    model = load_datatypes_normalization_templates_from_yaml(file_path)

    expected_model = {
        "TYPE1": "TO_CHAR({{ metric_query }}, 'N4')",
        "TYPE2": "TO_CHAR({{ metric_query }})",
        "TYPE3": "TO_CHAR({{ metric_query }}, 'N1')",
    }

    diff = DeepDiff(
        expected_model,
        model,
        ignore_order=True,
    )

    assert diff == {}


def test_load_datatypes_normalization_templates_from_yaml_file_not_found_exception():
    from snowflake.snowflake_data_validation.utils.helpers import (
        load_datatypes_normalization_templates_from_yaml,
    )
    from pathlib import Path

    with (pytest.raises(FileNotFoundError) as ex_info):
        file_path = (
            Path(__file__)
            .parent.joinpath(ASSETS_DIRECTORY_NAME)
            .joinpath(TEST_HELPERS_DIRECTORY_NAME)
            .joinpath(NOT_EXISTS_TEMPLATE_YAML_FILE_NAME)
        )
        load_datatypes_normalization_templates_from_yaml(file_path)

    assert (str(ex_info.value)).startswith("Template file not found at:")


def test_load_datatypes_normalization_templates_from_yaml_not_valid_format_exception():
    from snowflake.snowflake_data_validation.utils.helpers import (
        load_datatypes_normalization_templates_from_yaml,
    )

    yaml_content = r"""key1: value1
key2
  - value2
key3: [value3, value4"""

    with (pytest.raises(RuntimeError) as ex_info):
        file_path = MagicMock()
        file_path.read_text.return_value = yaml_content
        file_path.name = "not_valid_format.yaml"
        load_datatypes_normalization_templates_from_yaml(file_path)

    expected_error_message = r"""Error in the format of not_valid_format.yaml. Please check the following:
Incorrect indentation: YAML relies heavily on consistent indentation using spaces (not tabs).
Invalid characters: Certain characters might need to be quoted.
Syntax errors in lists or dictionaries: Incorrect use of hyphens for list items or nested structures.
Special characters not quoted: If a string contains special characters it might need to be enclosed in quotes."""

    assert expected_error_message == str(ex_info.value)
