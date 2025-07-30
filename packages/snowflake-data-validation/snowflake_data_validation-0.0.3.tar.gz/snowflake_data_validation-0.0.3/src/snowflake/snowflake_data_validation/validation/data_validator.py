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

import logging

import pandas as pd

from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputMessageLevel,
)
from snowflake.snowflake_data_validation.utils.constants import (
    COLUMN_DATATYPE,
    COLUMN_VALIDATED,
    NOT_APPLICABLE_CRITERIA_VALUE,
    NOT_EXIST_TARGET,
    TABLE_NAME_KEY,
    ValidationLevel,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.helpers import (
    is_numeric,
    normalize_dataframe,
)
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.validation.validation_report_buffer import (
    ValidationReportBuffer,
)


LOGGER = logging.getLogger(__name__)

VALIDATION_REPORT_NAME = "data_validation_report.csv"


def _normalize_datatype(datatype: str) -> str:
    """Normalize data types to handle equivalent types.

    This is a temporary fix for the issue where Snowflake displays "TEXT" instead of "VARCHAR".
    TODO: Remove this once the issue is fixed.

    Args:
        datatype (str): The data type to normalize.

    Returns:
        str: The normalized data type.

    """
    # Treat VARCHAR and TEXT as equivalent
    if datatype.upper() in {"VARCHAR", "TEXT"}:
        return "VARCHAR"
    return datatype.upper()


def _create_validation_row(
    validation_type: str,
    table_name: str,
    column_validated: str,
    evaluation_criteria: str,
    source_value: any,
    snowflake_value: any,
    status: str,
    comments: str,
) -> pd.DataFrame:
    """Create a standardized validation result row.

    Args:
        validation_type (str): The type of validation being performed.
        table_name (str): The name of the table being validated.
        column_validated (str): The column being validated.
        evaluation_criteria (str): The criteria used for evaluation.
        source_value (any): The value from the source.
        snowflake_value (any): The value from Snowflake.
        status (str): The validation status (SUCCESS/FAILURE).
        comments (str): Additional comments about the validation.

    Returns:
        pd.DataFrame: A single-row DataFrame with the validation result.

    """
    return pd.DataFrame(
        {
            "VALIDATION_TYPE": [validation_type],
            "TABLE": [table_name],
            "COLUMN_VALIDATED": [column_validated],
            "EVALUATION_CRITERIA": [evaluation_criteria],
            "SOURCE_VALUE": [source_value],
            "SNOWFLAKE_VALUE": [snowflake_value],
            "STATUS": [status],
            "COMMENTS": [comments],
        }
    )


def _add_validation_row_to_data(
    differences_data: pd.DataFrame, validation_row: pd.DataFrame
) -> pd.DataFrame:
    """Add a validation row to the differences data."""
    return pd.concat([differences_data, validation_row], ignore_index=True)


def _validate_datatype_field(
    source_value: str,
    target_value: str,
    context: Context,
    object_name: str,
    source_validated_value: str,
    column: str,
) -> tuple[pd.DataFrame, bool]:
    """Validate datatype field with mapping logic.

    Returns:
        tuple: (validation_row_df, is_success)

    """
    if context.datatypes_mappings:
        mapped_value = context.datatypes_mappings.get(source_value.upper(), None)
        if mapped_value and _normalize_datatype(target_value) == _normalize_datatype(
            mapped_value
        ):
            success_message = (
                f"Values match: source({source_value}) "
                f"has a mapping to Snowflake({target_value})"
            )
            return (
                _create_validation_row(
                    validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                    table_name=object_name,
                    column_validated=source_validated_value,
                    evaluation_criteria=column,
                    source_value=source_value,
                    snowflake_value=target_value,
                    status="SUCCESS",
                    comments=success_message,
                ),
                True,
            )
        else:
            comment = (
                f"No mapping found for datatype '{source_value}': "
                f"source({source_value}), Snowflake({target_value})"
                if not mapped_value
                else f"Values differ: source({source_value}), Snowflake({target_value})"
            )
            LOGGER.debug(
                "Datatype mismatch for column %s: source=%s, target=%s",
                source_validated_value,
                source_value,
                target_value,
            )
            return (
                _create_validation_row(
                    validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                    table_name=object_name,
                    column_validated=source_validated_value,
                    evaluation_criteria=column,
                    source_value=source_value,
                    snowflake_value=target_value,
                    status="FAILURE",
                    comments=comment,
                ),
                False,
            )
    else:
        # No mappings available - direct comparison
        if source_value.upper() == target_value.upper():
            return (
                _create_validation_row(
                    validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                    table_name=object_name,
                    column_validated=source_validated_value,
                    evaluation_criteria=column,
                    source_value=source_value,
                    snowflake_value=target_value,
                    status="SUCCESS",
                    comments=f"Values match: source({source_value}), Snowflake({target_value})",
                ),
                True,
            )
        else:
            LOGGER.debug(
                "Datatype mismatch for column %s: source=%s, target=%s",
                source_validated_value,
                source_value,
                target_value,
            )
            return (
                _create_validation_row(
                    validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                    table_name=object_name,
                    column_validated=source_validated_value,
                    evaluation_criteria=column,
                    source_value=source_value,
                    snowflake_value=target_value,
                    status="FAILURE",
                    comments=f"Values differ: source({source_value}), Snowflake({target_value})",
                ),
                False,
            )


def _validate_column_field(
    column: str,
    source_value: any,
    target_value: any,
    context: Context,
    object_name: str,
    source_validated_value: str,
) -> tuple[pd.DataFrame, bool]:
    """Validate a single column field and return validation row and success status.

    Returns:
        tuple: (validation_row_df, is_success)

    """
    # Skip if both values are NaN or identical
    if pd.isna(source_value) and pd.isna(target_value):
        return pd.DataFrame(), True  # No validation row needed, but success

    if source_value == target_value:
        return (
            _create_validation_row(
                validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                table_name=object_name,
                column_validated=source_validated_value,
                evaluation_criteria=column,
                source_value=source_value,
                snowflake_value=target_value,
                status="SUCCESS",
                comments=f"Values match: source({source_value}), Snowflake({target_value})",
            ),
            True,
        )

    # Handle datatype validation with special logic
    if column == COLUMN_DATATYPE:
        return _validate_datatype_field(
            source_value,
            target_value,
            context,
            object_name,
            source_validated_value,
            column,
        )

    # Handle specific precision/scale/length criteria with WARNING status
    warning_criteria = {
        "NUMERIC_PRECISION",
        "NUMERIC_SCALE",
        "CHARACTER_MAXIMUM_LENGTH",
    }
    if column in warning_criteria:

        if is_numeric(source_value) and is_numeric(target_value):
            if float(source_value) < float(target_value):
                return (
                    _create_validation_row(
                        validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                        table_name=object_name,
                        column_validated=source_validated_value,
                        evaluation_criteria=column,
                        source_value=source_value,
                        snowflake_value=target_value,
                        status="WARNING",
                        comments=f"Source value ({source_value}) is lower than target value ({target_value})",
                    ),
                    True,  # Consider WARNING as success
                )

    # Handle FAILURE status
    LOGGER.debug(
        "Value mismatch for column %s in %s: source=%s, target=%s",
        source_validated_value,
        column,
        source_value,
        target_value,
    )
    return (
        _create_validation_row(
            validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
            table_name=object_name,
            column_validated=source_validated_value,
            evaluation_criteria=column,
            source_value=source_value,
            snowflake_value=target_value,
            status="FAILURE",
            comments=f"Values differ: source({source_value}), Snowflake({target_value})",
        ),
        False,
    )


@log
def validate_table_metadata(
    object_name: str, target_df: pd.DataFrame, source_df: pd.DataFrame, context: Context
) -> bool:
    """Validate the metadata of two tables by normalizing and comparing their dataframes.

    Args:
        object_name (str): The name of the object (e.g., table) being validated.
        target_df (pd.DataFrame): The dataframe representing the target table's metadata.
        source_df (pd.DataFrame): The dataframe representing the source table's metadata.
        context (Context): The execution context containing relevant configuration and runtime information.

    Returns:
        bool: True if the normalized dataframes are equal, False otherwise.

    """
    LOGGER.info("Starting table metadata validation for: %s", object_name)
    context.output_handler.handle_message(
        message=f"Running Schema Validation for {object_name}",
        level=OutputMessageLevel.INFO,
    )

    LOGGER.debug("Normalizing target and source DataFrames")
    normalized_target = normalize_dataframe(target_df)
    normalized_source = normalize_dataframe(source_df)

    differences_data = pd.DataFrame(
        columns=[
            "VALIDATION_TYPE",
            "TABLE",
            "COLUMN_VALIDATED",
            "EVALUATION_CRITERIA",
            "SOURCE_VALUE",
            "SNOWFLAKE_VALUE",
            "STATUS",
            "COMMENTS",
        ]
    )

    target_validated_set = set(normalized_target[COLUMN_VALIDATED].values)

    for _, source_row in normalized_source.iterrows():
        source_validated_value = source_row[COLUMN_VALIDATED]

        # Handle missing columns in target
        if source_validated_value not in target_validated_set:
            LOGGER.debug("Column %s not found in target table", source_validated_value)
            new_row = _create_validation_row(
                validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                table_name=object_name,
                column_validated=source_validated_value,
                evaluation_criteria=COLUMN_VALIDATED,
                source_value=source_validated_value,
                snowflake_value=NOT_EXIST_TARGET,
                status="FAILURE",
                comments="The column does not exist in the target table.",
            )
            differences_data = _add_validation_row_to_data(differences_data, new_row)
            continue

        # Validate existing columns
        target_row = normalized_target[
            normalized_target[COLUMN_VALIDATED] == source_validated_value
        ]
        column_has_differences = False

        for column in normalized_source.columns:
            # Skip irrelevant columns
            if column in {COLUMN_VALIDATED, TABLE_NAME_KEY}:
                continue

            source_value = source_row[column]
            target_value = target_row[column].values[0]

            validation_row, field_success = _validate_column_field(
                column,
                source_value,
                target_value,
                context,
                object_name,
                source_validated_value,
            )

            if not validation_row.empty:
                differences_data = _add_validation_row_to_data(
                    differences_data, validation_row
                )

            if not field_success:
                column_has_differences = True

        # Record overall column success if no field differences found
        if not column_has_differences:
            success_row = _create_validation_row(
                validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                table_name=object_name,
                column_validated=source_validated_value,
                evaluation_criteria=COLUMN_VALIDATED,
                source_value=source_validated_value,
                snowflake_value=source_validated_value,
                status="SUCCESS",
                comments="Column exists in target table and all metadata matches.",
            )
            differences_data = _add_validation_row_to_data(
                differences_data, success_row
            )

    # Filter out rows where both SOURCE and TARGET are NOT_APPLICABLE_CRITERIA_VALUE
    # These represent validation criteria that don't apply to certain data types
    differences_data = differences_data[
        ~(
            (differences_data["SOURCE_VALUE"] == NOT_APPLICABLE_CRITERIA_VALUE)
            & (differences_data["SNOWFLAKE_VALUE"] == NOT_APPLICABLE_CRITERIA_VALUE)
        )
    ]

    # Determine if there are actual failures (excluding WARNING status)
    failure_rows = differences_data[differences_data["STATUS"] == "FAILURE"]
    has_failures = len(failure_rows) > 0

    buffer = ValidationReportBuffer()
    buffer.add_data(differences_data)
    LOGGER.debug(
        "Added schema validation data for %s to buffer (queue size: %d)",
        object_name,
        buffer.get_queue_size(),
    )

    display_data = differences_data.drop(
        columns=["VALIDATION_TYPE", "TABLE"], errors="ignore"
    )

    context.output_handler.handle_message(
        header="Schema validation results:",
        dataframe=display_data,
        level=(OutputMessageLevel.WARNING if has_failures else OutputMessageLevel.INFO),
    )

    return not has_failures


@log
def validate_column_metadata(
    object_name: str,
    target_df: pd.DataFrame,
    source_df: pd.DataFrame,
    context: Context,
    tolerance: float = 0.001,
) -> bool:
    """Validate that the column metadata of the target DataFrame matches the source DataFrame.

    This method normalizes both the target and source DataFrames and then compares their
    column metadata cell by cell to ensure they are equivalent within a given tolerance.

    Args:
        object_name (str): The name of the object (e.g., table) being validated.
        target_df (pd.DataFrame): The target DataFrame whose column metadata is to be validated.
        source_df (pd.DataFrame): The source DataFrame to compare against.
        context (Context): The execution context containing relevant configuration and runtime information.
        tolerance (float, optional): The tolerance level for numerical differences. Defaults to 0.001.

    Returns:
        bool: True if the column metadata of both DataFrames are equal within the tolerance, False otherwise.

    """
    LOGGER.info(
        "Starting column metadata validation for: %s with tolerance: %f",
        object_name,
        tolerance,
    )
    context.output_handler.handle_message(
        message=f"Running Metrics Validation for {object_name}",
        level=OutputMessageLevel.INFO,
    )

    normalized_target = normalize_dataframe(target_df)
    normalized_source = normalize_dataframe(source_df)

    differences_data = pd.DataFrame(
        columns=[
            "VALIDATION_TYPE",
            "TABLE",
            "COLUMN_VALIDATED",
            "EVALUATION_CRITERIA",
            "SOURCE_VALUE",
            "SNOWFLAKE_VALUE",
            "STATUS",
            "COMMENTS",
        ]
    )
    target_validated_set = set(normalized_target[COLUMN_VALIDATED].values)

    has_differences = False

    for _, source_row in normalized_source.iterrows():
        column_name = source_row[COLUMN_VALIDATED]
        source_validated_value = source_row[COLUMN_VALIDATED]

        if source_validated_value not in target_validated_set:
            new_row = _create_validation_row(
                validation_type=ValidationLevel.METRICS_VALIDATION.value,
                table_name=object_name,
                column_validated=source_validated_value,
                evaluation_criteria=COLUMN_VALIDATED,
                source_value=source_validated_value,
                snowflake_value=NOT_EXIST_TARGET,
                status="FAILURE",
                comments="The column does not exist in the target table.",
            )
            differences_data = pd.concat([differences_data, new_row], ignore_index=True)
            has_differences = True
        else:
            target_row = normalized_target[
                normalized_target[COLUMN_VALIDATED] == source_validated_value
            ]

            column_has_differences = False

            for col in normalized_source.columns:
                if col == COLUMN_VALIDATED or col == TABLE_NAME_KEY:
                    continue

                source_value = source_row[col]
                target_value = target_row[col].values[0]

                # Skip if both values are NaN or identical
                if pd.isna(source_value) and pd.isna(target_value):
                    # Record successful validation for NaN values
                    success_row = _create_validation_row(
                        validation_type=ValidationLevel.METRICS_VALIDATION.value,
                        table_name=object_name,
                        column_validated=column_name,
                        evaluation_criteria=col,
                        source_value="NULL",
                        snowflake_value="NULL",
                        status="SUCCESS",
                        comments="Both values are NULL/NaN - validation passed",
                    )
                    differences_data = pd.concat(
                        [differences_data, success_row], ignore_index=True
                    )
                    continue
                if source_value == target_value:
                    # Record successful validation for exact matches
                    success_row = _create_validation_row(
                        validation_type=ValidationLevel.METRICS_VALIDATION.value,
                        table_name=object_name,
                        column_validated=column_name,
                        evaluation_criteria=col,
                        source_value=str(source_value),
                        snowflake_value=str(target_value),
                        status="SUCCESS",
                        comments=f"Values match exactly: {source_value}",
                    )
                    differences_data = pd.concat(
                        [differences_data, success_row], ignore_index=True
                    )
                    continue

                # Check numeric values with tolerance
                if is_numeric(source_value) and is_numeric(target_value):
                    source_num = float(source_value)
                    target_num = float(target_value)
                    if abs(source_num - target_num) <= tolerance:
                        # Record successful validation within tolerance
                        success_row = _create_validation_row(
                            validation_type=ValidationLevel.METRICS_VALIDATION.value,
                            table_name=object_name,
                            column_validated=column_name,
                            evaluation_criteria=col,
                            source_value=str(source_value),
                            snowflake_value=str(target_value),
                            status="SUCCESS",
                            comments=(
                                f"Values within tolerance ({tolerance}): "
                                f"source({source_value}), target({target_value})"
                            ),
                        )
                        differences_data = pd.concat(
                            [differences_data, success_row], ignore_index=True
                        )
                        continue
                    comment = (
                        f"Values differ beyond tolerance of {tolerance}: "
                        f"source({source_value}), target({target_value})"
                    )
                else:
                    comment = (
                        f"Values differ: source({source_value}), target({target_value})"
                    )

                column_has_differences = True
                has_differences = True
                new_row = _create_validation_row(
                    validation_type=ValidationLevel.METRICS_VALIDATION.value,
                    table_name=object_name,
                    column_validated=column_name,
                    evaluation_criteria=col,
                    source_value=str(source_value),
                    snowflake_value=str(target_value),
                    status="FAILURE",
                    comments=comment,
                )
                differences_data = pd.concat(
                    [differences_data, new_row], ignore_index=True
                )

            # If the column exists and had no differences, record overall column success
            if not column_has_differences:
                success_row = _create_validation_row(
                    validation_type=ValidationLevel.METRICS_VALIDATION.value,
                    table_name=object_name,
                    column_validated=column_name,
                    evaluation_criteria=COLUMN_VALIDATED,
                    source_value=source_validated_value,
                    snowflake_value=source_validated_value,
                    status="SUCCESS",
                    comments="Column exists in target table and all metrics match.",
                )
                differences_data = pd.concat(
                    [differences_data, success_row], ignore_index=True
                )

    # Add validation data to buffer instead of writing directly to file
    buffer = ValidationReportBuffer()

    # Filter out rows where both SOURCE and TARGET are NOT_APPLICABLE_CRITERIA_VALUE
    # These represent validation criteria that don't apply to certain data types
    differences_data = differences_data[
        ~(
            (differences_data["SOURCE_VALUE"] == NOT_APPLICABLE_CRITERIA_VALUE)
            & (differences_data["SNOWFLAKE_VALUE"] == NOT_APPLICABLE_CRITERIA_VALUE)
        )
    ]

    buffer.add_data(differences_data)
    LOGGER.debug(
        "Added metrics validation data for %s to buffer (queue size: %d)",
        object_name,
        buffer.get_queue_size(),
    )

    display_data = differences_data.drop(
        columns=["VALIDATION_TYPE", "TABLE"], errors="ignore"
    )

    context.output_handler.handle_message(
        header="Metrics validation results:",
        dataframe=display_data,
        level=(
            OutputMessageLevel.WARNING if has_differences else OutputMessageLevel.INFO
        ),
    )

    return not has_differences


@log
def validate_non_numeric_difference(
    differences_data, object_name, column_name, metric, source_value, target_value
):
    """Validate non-numeric differences between source and target values for a specific column and metric.

    This function checks if there is a difference between the source and target values for a given column and metric.
    If a difference is found, it creates a new metadata row describing the discrepancy and appends it to the
    `differences_data` DataFrame.

    Args:
        differences_data (pd.DataFrame): A DataFrame containing metadata about differences identified during validation.
        object_name (str): The name of the object (e.g., table) being validated.
        column_name (str): The name of the column being validated.
        metric (str): The metric or validation rule being applied.
        source_value (Any): The value from the source dataset.
        target_value (Any): The value from the target dataset.

    Returns:
        pd.DataFrame: An updated DataFrame with the original differences and a new row if a difference was found.

    """
    LOGGER.debug(
        "Validating non-numeric difference for %s.%s.%s: source=%s, target=%s",
        object_name,
        column_name,
        metric,
        source_value,
        target_value,
    )
    new_row = _create_validation_row(
        validation_type=ValidationLevel.METRICS_VALIDATION.value,
        table_name=object_name,
        column_validated=column_name,
        evaluation_criteria=metric,
        source_value=source_value,
        snowflake_value=target_value,
        status="FAILURE",
        comments=f"Values differ: source({source_value}), target({target_value}).",
    )
    if not new_row.empty:
        differences_data = (
            pd.concat([differences_data, new_row], ignore_index=True)
            if not differences_data.empty
            else new_row
        )

    return differences_data


@log
def validate_numeric_difference(
    tolerance: float,
    differences_data: pd.DataFrame,
    object_name: str,
    column_name: str,
    metric: str,
    source_value: any,
    target_value: any,
    context: Context,
):
    """Validate the numeric difference between source and target values against a specified tolerance.

    This function checks if the absolute difference between the source and target values exceeds the given tolerance.
    If the difference is greater than the tolerance, it creates a new metadata row describing the discrepancy and
    appends it to the `differences_data` DataFrame.

    Args:
        tolerance (float): The maximum allowable difference between the source and target values.
        differences_data (pd.DataFrame): A DataFrame containing metadata about detected differences.
        object_name (str): The name of the object (e.g., table) being validated.
        column_name (str): The name of the column being validated.
        metric (str): The metric or description associated with the validation.
        source_value (float or str): The source value to be compared.
        target_value (float or str): The target value to be compared.
        context (Context): The execution context containing relevant configuration and runtime information.

    Returns:
        tuple: A tuple containing:
            - differences_data (pd.DataFrame): The updated DataFrame with any new discrepancy metadata rows appended.
            - source_value (float): The source value converted to a float.
            - target_value (float): The target value converted to a float.

    Raises:
        ValueError: If the source or target values cannot be converted to floats.

    Notes:
        - If the `differences_data` DataFrame is empty, it initializes it with the new metadata row.

    """
    LOGGER.debug(
        "Validating numeric difference for %s.%s.%s with tolerance %f: source=%s, target=%s",
        object_name,
        column_name,
        metric,
        tolerance,
        source_value,
        target_value,
    )
    # WIP: This is a temporary solution to handle the case when the value is a string representation of a number.
    target_value = float(target_value)
    source_value = float(source_value)
    if abs(target_value - source_value) > tolerance:
        new_row = _create_validation_row(
            validation_type=ValidationLevel.METRICS_VALIDATION.value,
            table_name=object_name,
            column_validated=column_name,
            evaluation_criteria=metric,
            source_value=source_value,
            snowflake_value=target_value,
            status="FAILURE",
            comments=f"Values differ ({source_value} != {target_value}) beyond tolerance.",
        )
        if not new_row.empty:
            differences_data = (
                pd.concat([differences_data, new_row], ignore_index=True)
                if not differences_data.empty
                else new_row
            )
    else:
        context.output_handler.handle_message(
            header="Disregarding numeric difference.",
            message=(
                f"Source value: {source_value} and Target value: {target_value} "
                f"do not differ beyond tolerance. {tolerance}"
            ),
            level=OutputMessageLevel.WARNING,
        )
    return differences_data, source_value, target_value
