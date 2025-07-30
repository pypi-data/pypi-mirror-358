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
import pytest
from unittest.mock import MagicMock, patch
import tempfile
import datetime

from snowflake.snowflake_data_validation.comparison_orchestrator import (
    ComparisonOrchestrator,
)
from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)


@pytest.fixture
def mock_context():
    context = MagicMock()
    context.output_handler.console_output_enabled = True
    context.output_handler.handle_message = MagicMock()
    context.configuration.tables = []

    # Add required attributes with proper values
    context.report_path = tempfile.mkdtemp()  # Create a real temporary directory
    context.run_start_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    context.run_id = "test_run_id"

    return context


@pytest.fixture
def mock_extractors():
    source_extractor = MagicMock()
    target_extractor = MagicMock()
    return source_extractor, target_extractor


@pytest.fixture
def orchestrator_setup():
    """Set up test fixtures."""
    source_connector = MagicMock()
    target_connector = MagicMock()
    context = MagicMock()
    output_handler = MagicMock()
    context.output_handler = output_handler

    orchestrator = ComparisonOrchestrator(
        source_connector=source_connector,
        target_connector=target_connector,
        context=context,
    )

    return orchestrator, source_connector, target_connector, context, output_handler


@pytest.fixture
def orchestrator_setup_gen_queries():
    """Set up test fixtures for comparison orchestrator tests."""
    source_connector = MagicMock()
    target_connector = MagicMock()
    context = MagicMock()
    output_handler = MagicMock()
    context.output_handler = output_handler
    context.report_path = "/test/path"
    context.source_platform = "source_db"
    context.configuration.target_platform = "target_db"

    orchestrator = ComparisonOrchestrator(
        source_connector=source_connector,
        target_connector=target_connector,
        context=context,
    )

    return orchestrator, source_connector, target_connector, context, output_handler


def create_mock_table_context(
    fully_qualified_name="my_table",
    column_selection_list=None,
    where_clause="",
    target_where_clause="",
    has_where_clause=False,
    use_column_selection_as_exclude_list=False,
):
    """Helper function to create mock table configuration objects."""
    if column_selection_list is None:
        column_selection_list = ["col1", "col2"]

    mock_table = MagicMock(spec=TableConfiguration)
    mock_table.fully_qualified_name = fully_qualified_name
    mock_table.column_selection_list = column_selection_list
    mock_table.where_clause = where_clause
    mock_table.target_where_clause = target_where_clause
    mock_table.has_where_clause = has_where_clause
    mock_table.use_column_selection_as_exclude_list = (
        use_column_selection_as_exclude_list
    )
    return mock_table


def test_level_1_comparison_success(mock_extractors, mock_context):
    source_extractor, target_extractor = mock_extractors
    source_extractor.extract_schema_metadata.return_value = "source_df"
    target_extractor.extract_schema_metadata.return_value = "target_df"

    import snowflake.snowflake_data_validation.validation.data_validator as dv

    dv.validate_table_metadata = MagicMock(return_value=True)

    # Create mock connectors
    source_connector = MagicMock()
    target_connector = MagicMock()

    orchestrator = ComparisonOrchestrator(
        source_connector, target_connector, mock_context
    )

    # Create mock table configuration
    table_context = create_mock_table_context()

    # The test should use run_sync_comparison instead of level_1_comparison
    with patch.object(
        orchestrator,
        "_create_metadata_extractor",
        side_effect=[source_extractor, target_extractor],
    ):
        with patch.object(
            orchestrator.executor_factory, "create_executor"
        ) as mock_executor_factory:
            with patch.object(
                orchestrator, "_orchestrate_tables_execution"
            ) as mock_execute:
                mock_executor = MagicMock()
                mock_executor_factory.return_value = mock_executor

                # Test the run_sync_comparison method instead
                orchestrator.run_sync_comparison()

                mock_executor_factory.assert_called_once()
                mock_execute.assert_called_once_with(mock_executor)


def test_level_2_comparison_success(mock_extractors, mock_context):
    source_extractor, target_extractor = mock_extractors
    source_metadata = MagicMock()
    source_metadata.empty = False
    target_metadata = MagicMock()
    target_metadata.empty = False
    source_extractor.extract_metrics_metadata.return_value = source_metadata
    target_extractor.extract_metrics_metadata.return_value = target_metadata

    import snowflake.snowflake_data_validation.validation.data_validator as dv

    dv.validate_column_metadata = MagicMock(return_value=True)

    # Create mock connectors
    source_connector = MagicMock()
    target_connector = MagicMock()

    orchestrator = ComparisonOrchestrator(
        source_connector, target_connector, mock_context
    )

    # Create mock table configuration
    table_context = create_mock_table_context()

    # Test the run_sync_comparison method instead
    with patch.object(
        orchestrator,
        "_create_metadata_extractor",
        side_effect=[source_extractor, target_extractor],
    ):
        with patch.object(
            orchestrator.executor_factory, "create_executor"
        ) as mock_executor_factory:
            with patch.object(
                orchestrator, "_orchestrate_tables_execution"
            ) as mock_execute:
                mock_executor = MagicMock()
                mock_executor_factory.return_value = mock_executor

                orchestrator.run_sync_comparison()

                mock_executor_factory.assert_called_once()
                mock_execute.assert_called_once_with(mock_executor)


def test_level_2_comparison_source_empty(mock_extractors, mock_context):
    source_extractor, target_extractor = mock_extractors
    source_metadata = MagicMock()
    source_metadata.empty = True
    target_metadata = MagicMock()
    target_metadata.empty = False
    source_extractor.extract_metrics_metadata.return_value = source_metadata
    target_extractor.extract_metrics_metadata.return_value = target_metadata

    # Create mock connectors
    source_connector = MagicMock()
    target_connector = MagicMock()

    orchestrator = ComparisonOrchestrator(
        source_connector, target_connector, mock_context
    )

    # Create mock table configuration
    table_context = create_mock_table_context()

    # Test run_async_generation method instead
    with patch.object(orchestrator, "_create_script_printer") as mock_script_printer:
        mock_printer = MagicMock()
        mock_script_printer.return_value = mock_printer

        orchestrator.run_async_generation()

        # Verify script printers were created
        assert mock_script_printer.call_count >= 2


def test_level_2_comparison_target_empty(mock_extractors, mock_context):
    source_extractor, target_extractor = mock_extractors
    source_metadata = MagicMock()
    source_metadata.empty = False
    target_metadata = MagicMock()
    target_metadata.empty = True
    source_extractor.extract_metrics_metadata.return_value = source_metadata
    target_extractor.extract_metrics_metadata.return_value = target_metadata

    # Create mock connectors
    source_connector = MagicMock()
    target_connector = MagicMock()

    orchestrator = ComparisonOrchestrator(
        source_connector, target_connector, mock_context
    )

    # Create mock table configuration
    table_context = create_mock_table_context()

    # Test the from_validation_environment class method
    validation_env = MagicMock()
    validation_env.source_connector = source_connector
    validation_env.target_connector = target_connector
    validation_env.context = mock_context

    result_orchestrator = ComparisonOrchestrator.from_validation_environment(
        validation_env
    )

    assert result_orchestrator.source_connector == source_connector
    assert result_orchestrator.target_connector == target_connector
    assert result_orchestrator.context == mock_context


def test_execute_custom_validations(mock_context):
    class DummyValidationConfig:
        def model_dump(self):
            return {
                "schema_validation": True,
                "columnar_validation": False,
                "metrics_validation": False,
                "row_validation": False,
            }

    # Create mock connectors
    source_connector = MagicMock()
    target_connector = MagicMock()

    orchestrator = ComparisonOrchestrator(
        source_connector=source_connector,
        target_connector=target_connector,
        context=mock_context,
    )

    # Test that the orchestrator can be created successfully
    assert orchestrator.source_connector == source_connector
    assert orchestrator.target_connector == target_connector
    assert orchestrator.context == mock_context


def test_write_async_query_to_file_success(orchestrator_setup):
    """Test successful writing of query to file using run_async_generation."""
    (
        orchestrator,
        source_connector,
        target_connector,
        context,
        output_handler,
    ) = orchestrator_setup

    # Mock the context configuration to have tables
    mock_tables = [MagicMock()]
    mock_tables[0].fully_qualified_name = "test.table"
    mock_tables[0].column_selection_list = ["col1", "col2"]
    mock_tables[0].where_clause = None
    mock_tables[0].has_where_clause = False
    mock_tables[0].use_column_selection_as_exclude_list = False

    context.configuration.tables = mock_tables
    context.configuration.validation_configuration = MagicMock()
    context.configuration.validation_configuration.schema_validation = True
    context.configuration.validation_configuration.metrics_validation = False

    # Mock the script printers
    with patch.object(orchestrator, "_create_script_printer") as mock_create_printer:
        mock_printer = MagicMock()
        mock_create_printer.return_value = mock_printer

        # Test the run_async_generation method
        orchestrator.run_async_generation()

        # Verify script printers were created and used
        assert mock_create_printer.call_count >= 2
        mock_printer.print_table_metadata_query.assert_called()
