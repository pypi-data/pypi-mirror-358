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

import json
import os
import re
import tempfile

from functools import wraps
from pathlib import Path
from typing import Any, Union

import pandas as pd
import yaml

from snowflake.snowflake_data_validation.utils.constants import (
    COL_NAME_QUOTES_PLACEHOLDER,
    EDITABLE_YAML_FILE_FORMAT_ERROR,
    METRIC_COLUMN_KEY,
    METRIC_NORMALIZATION_KEY,
    METRIC_QUERY_KEY,
    METRIC_QUERY_PLACEHOLDER,
    METRIC_RETURN_DATATYPE_KEY,
    NEWLINE,
    NORMALIZATION_COLUMN_KEY,
    NOT_APPLICABLE_CRITERIA_VALUE,
    TEMPLATE_COLUMN_KEY,
    TYPE_COLUMN_KEY,
)


is_numeric_regex = r"^-?\d+(\.\d+)?$"


def read_json_file(file_name: str) -> dict[str, any]:
    """Read data from a JSON file.

    Args:
        file_name (str): The name of the file to read from.

    Returns:
        dict[str, any]: The data read from the file.

    """
    with open(file_name) as readfile:
        data = json.load(readfile)
    return data


def get_schema_name(qualified_table_name: str) -> Union[str, None]:
    """Get the schema name from a qualified table name.

    Args:
        qualified_table_name (str): The qualified table name.

    Returns:
        str or None: The schema name if present, otherwise None.

    """
    name = qualified_table_name.split(".")
    if len(name) == 1:
        return None
    elif len(name) == 2:
        return name[0]
    else:
        return name[1]


def get_table_name(qualified_table_name: str) -> str:
    """Get the table name from a qualified table name.

    Args:
        qualified_table_name (str): The qualified table name.

    Returns:
        str: The table name.

    """
    name = qualified_table_name.split(".")
    if len(name) == 1:
        return name[0]
    elif len(name) == 2:
        return name[1]
    else:
        return name[2]


def get_decomposed_fully_qualified_name(
    fully_qualified_name: str,
) -> tuple[str, str, str]:
    """Decomposes a fully qualified name into its database, schema, and table components.

    Args:
        fully_qualified_name (str): The fully qualified name in the format 'database.schema.table'.

    Returns:
        tuple: A tuple containing the database, schema, and table as strings.

    Raises:
        ValueError: If the fully qualified name does not have exactly three parts separated by dots.

    """
    parts = fully_qualified_name.split(".")
    if len(parts) != 3:
        raise ValueError(
            f"Invalid fully qualified name: {fully_qualified_name}. Expected format: database.schema.table"
        )

    database, schema, table = parts

    return database, schema, table


# WIP We should evaluate the need for a directory manager class, it could exist in the Context class
# and potentially move this functionality to a more appropriate location inside it
def copy_templates_to_temp_dir(
    source_templates_path: str, core_templates_path: str, templates_temp_dir_path: str
) -> None:
    """Copy template files from source and core template directories to a temporary directory.

    This function ensures that the temporary directory exists, and then copies all files
    and directories from the specified source and core template paths into the temporary
    directory. If the temporary directory cannot be created or the files cannot be copied,
    an appropriate exception is raised.

    Args:
        source_templates_path (str): The path to the source templates directory.
        core_templates_path (str): The path to the core templates directory.
        templates_temp_dir_path (str): The path to the temporary directory where templates
                                       will be copied.

    Raises:
        RuntimeError: If the temporary directory cannot be created or if an error occurs
                      during the copying of templates.

    """
    try:
        for path in [core_templates_path, source_templates_path]:
            if os.path.exists(path):
                for item in os.listdir(path):
                    source_item = os.path.join(path, item)
                    dest_item = os.path.join(templates_temp_dir_path, item)
                    if os.path.isdir(source_item):
                        os.makedirs(dest_item, exist_ok=True)
                    else:
                        with open(source_item, "rb") as src, open(
                            dest_item, "wb"
                        ) as dst:
                            dst.write(src.read())
    except Exception as e:
        raise RuntimeError(
            f"Failed to copy templates from {core_templates_path} or "
            f"{source_templates_path} to {templates_temp_dir_path}: {e}"
        ) from e


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the DataFrame by standardizing column names and types.

    Args:
        df (pd.DataFrame): The DataFrame to normalize.

    Returns:
        pd.DataFrame: A normalized DataFrame with uppercase column names, NaN values filled with
                     NOT_APPLICABLE_CRITERIA_VALUE, and rows sorted by all columns.

    """
    df.columns = [
        col.upper() for col in df.columns
    ]  # WIP in the future we should generate the columns names from a column mapping if provided
    df_copy = df.fillna(NOT_APPLICABLE_CRITERIA_VALUE, inplace=False)
    return df_copy.sort_values(by=list(df_copy.columns)).reset_index(drop=True)


def create_temp_dir(prefix="sdv_") -> str:
    """Create a temporary directory with a specified prefix.

    This function generates a temporary directory in the system's default
    temporary file location. The directory name will start with the given
    prefix, followed by a unique identifier.

    Args:
        prefix (str): The prefix for the temporary directory name. Defaults to "sdv_".

    Returns:
        str: The path to the created temporary directory.

    """
    temp_dir_path = tempfile.mkdtemp(prefix=prefix)
    return temp_dir_path


def create_new_table_metadata_row(
    columns: list[str],
    validated_value: str,
    column: str,
    source_value: Any,
    target_value: Any,
    comment: str,
) -> pd.DataFrame:
    """Create a new row for the differences DataFrame.

    This function generates a new pandas DataFrame containing a single row
    with metadata about differences between source and target data. It is
    typically used to log discrepancies during data validation processes.

    Args:
        columns (list[str]): A list of column names for the resulting DataFrame.
        validated_value (str): A value indicating the validation status or result.
        column (str): The name of the column being validated.
        source_value (any): The value from the source data.
        target_value (any): The value from the target data.
        comment (str): A comment or description of the discrepancy.

    Returns:
        pandas.DataFrame: A DataFrame containing a single row with the provided
        metadata.

    """
    """Create a new row for the differences DataFrame."""
    return pd.DataFrame(
        [
            [
                validated_value,
                column,
                source_value,
                target_value,
                comment,
            ]
        ],
        columns=columns,
    )


def create_new_column_metadata_row(
    columns: list[str],
    column_name: str,
    metric: str,
    source_value: any,
    target_value: any,
    comments: str,
) -> pd.DataFrame:
    """Create a new row of metadata for a column and returns it as a pandas DataFrame.

    Args:
        columns (list[str]): A list of column names for the DataFrame.
        column_name (str): The name of the column being described.
        metric (str): The metric or property associated with the column.
        source_value (Any): The value of the metric from the source.
        target_value (Any): The value of the metric from the target.
        comments (str): Additional comments or notes about the column.

    Returns:
        pd.DataFrame: A DataFrame containing a single row with the provided metadata.

    """
    return pd.DataFrame(
        [
            [
                column_name,
                metric,
                source_value,
                target_value,
                comments,
            ]
        ],
        columns=columns,
    )


def get_connection_file_path(platform_name: str) -> Path:
    """Construct the file path for a connection configuration file based on the given platform name.

    The function generates a file path by appending the current working directory
    with a file name in the format "{platform_name}_conn.toml".

    Args:
        platform_name (str): The name of the platform for which the connection file path is being generated.

    Returns:
        Path: A Path object representing the full file path to the connection configuration file.

    """
    current_dir = os.getcwd()
    # WIP: We should use the context manager to get the current directory
    toml_file_path: Path = Path(current_dir) / f"{platform_name}_conn.toml"
    return toml_file_path


def is_numeric(value: any) -> bool:
    """Determine if the given value is numeric.

    A value is considered numeric if it is an instance of int or float,
    or if it matches the numeric pattern (including integers and decimals).
    As a safety net, if the regex check passes, we also verify that the
    value can actually be converted to float.

    Args:
        value: The value to check. Can be of any type.

    Returns:
        bool: True if the value is numeric, False otherwise.

    """
    if isinstance(value, (int, float)):
        return True

    if bool(re.match(is_numeric_regex, str(value))):
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    return False


def import_dependencies(package: str = None, helper_text: str = ""):
    """Import a helper function from a package.

    Args:
        package (str): The name of the package to import from.
        helper_text (str): The name of the helper function to import.

    Returns:
        Any: The imported helper function or None if not found.

    """

    def decorator(func):
        @wraps(func)
        def _wrapper():
            try:
                return func()
            except ModuleNotFoundError as e:
                help = helper_text
                if package:
                    help += f"Please install the missing depencies. \
                    Run pip install snowflake-data-validation[{package}]"
                raise ModuleNotFoundError(f"{e}\n\n{help}") from e

        return _wrapper

    return decorator


def load_metrics_templates_from_yaml(
    yaml_path: Path, datatypes_normalization_templates: dict[str, str]
) -> pd.DataFrame:
    """Load metrics templates from a YAML file into a pandas DataFrame.

    Args:
        yaml_path (Path): The file path to the YAML file.
        datatypes_normalization_templates (dict[str, str]): A dictionary containing
        normalization templates for data types.

    Raises:
        FileNotFoundError: If the specified YAML file does not exist.
        KeyError: If a required key is missing in the YAML data.
        RuntimeError: If there is an error in the format of the YAML file.

    Returns:
        pd.DataFrame: A DataFrame containing the data from the YAML file.

    """
    if not yaml_path.exists():
        raise FileNotFoundError(f"Template file not found at: {yaml_path}")

    try:
        file_content = yaml_path.read_text()
        yaml_data = yaml.safe_load(file_content)
        yaml_data_reformatted = _reformat_metrics_yaml_data(
            yaml_data=yaml_data,
            datatypes_normalization_templates=datatypes_normalization_templates,
        )
        df = pd.DataFrame.from_dict(yaml_data_reformatted)

    except KeyError as e:
        error_message = f"Missing {e.args[0]} datatype in datatypes normalization file."
        raise RuntimeError(error_message) from e

    except Exception as e:
        error_message = EDITABLE_YAML_FILE_FORMAT_ERROR.format(file_name=yaml_path.name)
        raise RuntimeError(error_message) from e

    return df


def load_datatypes_templates_from_yaml(yaml_path: Path, platform: str) -> pd.DataFrame:
    """Load datatypes templates from a YAML file into a pandas DataFrame.

    Args:
        yaml_path (Path): The file path to the YAML file.
        platform (str): The platform identifier to use.

    Raises:
        FileNotFoundError: If the specified YAML file does not exist.
        RuntimeError: If there is an error in the format of the YAML file.

    Returns:
        pd.DataFrame: A DataFrame containing the data from the YAML file.

    """
    if not yaml_path.exists():
        raise FileNotFoundError(f"Template file not found at: {yaml_path}")

    try:
        file_content = yaml_path.read_text()
        yaml_data = yaml.safe_load(file_content)
        yaml_data_reformatted = _reformat_datatypes_yaml_data(yaml_data, platform)
        df = pd.DataFrame.from_dict(yaml_data_reformatted)

    except Exception as e:
        error_message = EDITABLE_YAML_FILE_FORMAT_ERROR.format(file_name=yaml_path.name)
        raise RuntimeError(error_message) from e

    return df


def load_datatypes_normalization_templates_from_yaml(yaml_path: Path) -> dict[str, str]:
    """Load datatypes normalization templates from a YAML file into a pandas DataFrame.

    Args:
        yaml_path (Path): The file path to the YAML file.

    Raises:
        FileNotFoundError: If the specified YAML file does not exist.
        RuntimeError: If there is an error in the format of the YAML file.

    Returns:
        dict[str, str]: A dictionary containing the data from the YAML file.

    """
    if not yaml_path.exists():
        raise FileNotFoundError(f"Template file not found at: {yaml_path}")

    try:
        file_content = yaml_path.read_text()
        yaml_data = yaml.safe_load(file_content)
        yaml_data_reformatted = {
            key.upper(): yaml_data[key] for key in yaml_data.keys()
        }

    except Exception as e:
        error_message = EDITABLE_YAML_FILE_FORMAT_ERROR.format(file_name=yaml_path.name)
        raise RuntimeError(error_message) from e

    return yaml_data_reformatted


def _reformat_datatypes_yaml_data(
    yaml_data: dict, platform: str
) -> dict[str, list[str]]:
    """Reformat YAML data to ensure it is in a consistent format.

    Args:
        yaml_data (dict): The original YAML data.
        platform (str): The platform identifier to use.

    Raises:
        ValueError: If the YAML data does not contain the expected structure.

    Returns:
        dict: The reformatted YAML data.

    """
    source_platform_data_types_collection = list(yaml_data.keys())
    platform_data_types_dict_collection = {
        str.lower(platform): source_platform_data_types_collection
    }
    temporal_platform_data_types_dict_collection = {}
    for source_data_type in source_platform_data_types_collection:
        for target_data_type in yaml_data[source_data_type]:
            if (
                temporal_platform_data_types_dict_collection.get(target_data_type)
                is None
            ):
                temporal_platform_data_types_dict_collection[target_data_type] = []
            current_data_type = yaml_data[source_data_type][target_data_type]
            temporal_platform_data_types_dict_collection[target_data_type].append(
                current_data_type
            )

    platform_data_types_dict_collection.update(
        temporal_platform_data_types_dict_collection
    )
    return platform_data_types_dict_collection


def _reformat_metrics_yaml_data(
    yaml_data: dict, datatypes_normalization_templates: dict[str, str]
) -> dict[str, list[str]]:
    """Reformat YAML data to ensure it is in a consistent format.

    Args:
        yaml_data (dict): The original YAML data.
        datatypes_normalization_templates (dict[str, str]): A dictionary containing
        normalization templates for data types.

    Raises:
        ValueError: If the YAML data does not contain the expected structure.

    Returns:
        dict: The reformatted YAML data.

    """
    type_column = []
    metric_column = []
    metric_template_column = []
    metric_normalization_template_column = []

    data_type_collection = list(yaml_data.keys())
    for data_type in data_type_collection:
        metric_name_collection = list(yaml_data[data_type].keys())
        template_collection = list(yaml_data[data_type].values())
        for metric_name, templates in zip(metric_name_collection, template_collection):
            type_column.append(data_type.upper())
            metric_column.append(metric_name)
            metric_template_column.append(templates[METRIC_QUERY_KEY])

            if templates.get(METRIC_NORMALIZATION_KEY, None) is not None:
                metric_normalization_template_column.append(
                    templates[METRIC_NORMALIZATION_KEY]
                )
            else:
                metric_return_datatype = templates[METRIC_RETURN_DATATYPE_KEY]
                normalization_template = datatypes_normalization_templates[
                    metric_return_datatype.upper()
                ]
                normalization_template_normalized = normalization_template.replace(
                    COL_NAME_QUOTES_PLACEHOLDER, METRIC_QUERY_PLACEHOLDER
                )
                metric_normalization_template_column.append(
                    normalization_template_normalized
                )

    type_metric_dict_collection = {
        TYPE_COLUMN_KEY: type_column,
        METRIC_COLUMN_KEY: metric_column,
        TEMPLATE_COLUMN_KEY: metric_template_column,
        NORMALIZATION_COLUMN_KEY: metric_normalization_template_column,
    }

    return type_metric_dict_collection


def write_to_file(file_path: str, content: str) -> None:
    """Write content to a file with UTF-8 encoding.

    Creates the directory if it doesn't exist.

    Args:
        file_path (str): The full path to the file including directory and filename.
        content (str): The content to write to the file.

    """
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(content)
        f.write(NEWLINE)


def _dump_and_write_yaml_template(template_path: str, output_directory: str) -> str:
    """Dump the content of a YAML template file to a new file.

    Args:
        template_path (str): The path to the YAML template file.
        output_directory (str): The directory where the output file will be written.

    Returns:
        str: The path to the output file where the content was written.

    """
    with open(template_path, encoding="utf-8") as f:
        content = yaml.safe_load(f)
    output_file = os.path.join(output_directory, os.path.basename(template_path))
    with open(output_file, "w", encoding="utf-8") as out_f:
        yaml.dump(content, out_f, default_flow_style=False)
    return str(output_file)


def load_datatypes_mapping_templates_from_yaml(
    yaml_path: Path, target_platform: str
) -> dict[str, str]:
    """Load datatypes mapping templates from a YAML file into a dictionary.

    Args:
        yaml_path (Path): The file path to the YAML file.
        target_platform (str): The target platform identifier to use for mapping.

    Raises:
        FileNotFoundError: If the specified YAML file does not exist.
        RuntimeError: If there is an error in the format of the YAML file.

    Returns:
        dict[str, str]: A dictionary containing the data from the YAML file.

    """
    if not yaml_path.exists():
        raise FileNotFoundError(f"Template file not found at: {yaml_path}")

    try:
        file_content = yaml_path.read_text()
        if len(file_content) == 0:
            return {}

        yaml_data = yaml.safe_load(file_content)

    except Exception as e:
        error_message = EDITABLE_YAML_FILE_FORMAT_ERROR.format(file_name=yaml_path.name)
        raise RuntimeError(error_message) from e

    return yaml_data
