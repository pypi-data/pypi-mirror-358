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

from typing import Optional

import pandas as pd

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.configuration.model.validation_configuration import (
    ValidationConfiguration,
)
from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.executer import (
    ExecutorFactory,
)
from snowflake.snowflake_data_validation.executer.base_validation_executor import (
    BaseValidationExecutor,
)
from snowflake.snowflake_data_validation.executer.extractor_types import (
    ExtractorType,
)
from snowflake.snowflake_data_validation.extractor.metadata_extractor_base import (
    MetadataExtractorBase,
)
from snowflake.snowflake_data_validation.script_writer.script_writer_base import (
    ScriptWriterBase,
)
from snowflake.snowflake_data_validation.utils.arguments_manager_base import (
    ValidationEnvironmentObject,
)
from snowflake.snowflake_data_validation.utils.constants import (
    COLUMN_DATATYPE,
    DATABASE_NAME_KEY,
    SCHEMA_NAME_KEY,
    TABLE_NAME_KEY,
    ExecutionMode,
    Platform,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.utils.model.table_column_metadata import (
    TableColumnMetadata,
)
from snowflake.snowflake_data_validation.utils.progress_reporter import (
    ProgressMetadata,
    report_progress,
)
from snowflake.snowflake_data_validation.utils.telemetry import (
    report_telemetry,
)
from snowflake.snowflake_data_validation.validation.validation_report_buffer import (
    ValidationReportBuffer,
)


LOGGER = logging.getLogger(__name__)


class ComparisonOrchestrator:

    """Orchestrator for validation operations that creates appropriate components based on command type."""

    @log
    def __init__(
        self,
        source_connector: ConnectorBase,
        target_connector: ConnectorBase,
        context: Context,
    ):
        """Initialize the orchestrator.

        Args:
            source_connector: Source database connector
            target_connector: Target database connector
            context: Validation context containing configuration and runtime info

        """
        LOGGER.debug("Initializing ComparisonOrchestrator")
        self.source_connector = source_connector
        self.target_connector = target_connector
        self.context = context
        self.executor_factory = ExecutorFactory()
        LOGGER.debug("ComparisonOrchestrator initialized successfully")

    @classmethod
    @log
    def from_validation_environment(
        cls, validation_env: ValidationEnvironmentObject
    ) -> "ComparisonOrchestrator":
        """Create a ComparisonOrchestrator from a ValidationEnvironmentObject.

        Args:
            validation_env: ValidationEnvironmentObject instance containing all required components

        Returns:
            ComparisonOrchestrator: Configured orchestrator ready to run validation

        """
        LOGGER.debug("Creating ComparisonOrchestrator from validation environment")
        return cls(
            source_connector=validation_env.source_connector,
            target_connector=validation_env.target_connector,
            context=validation_env.context,
        )

    @log
    @report_telemetry()
    def run_sync_comparison(self) -> None:
        """Run the complete synchronous validation comparison process.

        Uses the sync validation executor with metadata extractors for real-time validation.
        """
        LOGGER.info("Starting synchronous validation comparison")
        # Create metadata extractors for validation command
        source_extractor = self._create_metadata_extractor(
            self.source_connector, self.context.source_platform
        )
        target_extractor = self._create_metadata_extractor(
            self.target_connector, self.context.target_platform
        )

        executor = self.executor_factory.create_executor(
            ExecutionMode.SYNC_VALIDATION,
            source_extractor=source_extractor,
            target_extractor=target_extractor,
            context=self.context,
        )

        self._orchestrate_tables_execution(executor)
        LOGGER.info("Synchronous validation comparison completed")

    @log
    @report_telemetry()
    def run_async_generation(self) -> None:
        """Generate validation scripts for all tables defined in the configuration.

        Uses script printers to write SQL queries to files.
        """
        LOGGER.info("Starting async script generation")
        # Create script printers for script generation command
        source_printer = self._create_script_printer(
            self.source_connector, self.context.source_platform
        )
        target_printer = self._create_script_printer(
            self.target_connector, self.context.target_platform
        )

        executor = self.executor_factory.create_executor(
            ExecutionMode.ASYNC_GENERATION,
            source_extractor=source_printer,
            target_extractor=target_printer,
            context=self.context,
        )

        self._orchestrate_tables_execution(executor)
        LOGGER.info("Async script generation completed")

    @log
    @report_telemetry()
    def run_async_comparison(self) -> None:
        """Run the asynchronous validation comparison process.

        Uses the async validation executor with metadata extractors for deferred validation.
        """
        LOGGER.info("Starting asynchronous validation comparison")
        # Create metadata extractors for async validation command
        source_extractor = self._create_metadata_extractor(
            self.source_connector, self.context.source_platform
        )
        target_extractor = self._create_metadata_extractor(
            self.target_connector, self.context.configuration.target_platform
        )

        executor = self.executor_factory.create_executor(
            ExecutionMode.ASYNC_VALIDATION,
            source_extractor=source_extractor,
            target_extractor=target_extractor,
            context=self.context,
        )

        self._orchestrate_tables_execution(executor)
        LOGGER.info("Asynchronous validation comparison completed")

    @log
    def _create_metadata_extractor(
        self, connector: ConnectorBase, platform: Platform
    ) -> MetadataExtractorBase:
        """Create the appropriate metadata extractor based on platform.

        Args:
            connector: Database connector instance
            platform: Platform enum (e.g., Platform.SNOWFLAKE, Platform.SQLSERVER)

        Returns:
            MetadataExtractorBase: Platform-specific metadata extractor

        """
        LOGGER.debug("Creating metadata extractor for platform: %s", platform)
        return self.executor_factory.create_extractor_from_connector(
            connector=connector,
            extractor_type=ExtractorType.METADATA_EXTRACTOR,
            platform=platform,
            report_path=self.context.report_path,
        )

    @log
    def _create_script_printer(
        self, connector: ConnectorBase, platform: Platform
    ) -> ScriptWriterBase:
        """Create the appropriate script printer based on platform.

        Args:
            connector: Database connector instance
            platform: Platform enum (e.g., Platform.SNOWFLAKE, Platform.SQLSERVER)

        Returns:
            ScriptWriterBase: Platform-specific script printer

        """
        LOGGER.debug("Creating script printer for platform: %s", platform)
        return self.executor_factory.create_extractor_from_connector(
            connector=connector,
            extractor_type=ExtractorType.SCRIPT_WRITER,
            platform=platform,
            report_path=self.context.report_path,
        )

    @log
    def _orchestrate_tables_execution(self, executor: BaseValidationExecutor) -> None:
        """Execute validation for all tables using the provided executor.

        Args:
            executor: The validation executor to use for processing tables

        """
        tables = self.context.configuration.tables
        default_configuration = self.context.configuration.validation_configuration

        LOGGER.info("Starting validation execution for %d tables", len(tables))

        # Process all tables
        for table_configuration in tables:
            LOGGER.info(
                "Processing table: %s", table_configuration.fully_qualified_name
            )
            self._report_progress_for_table(
                table_configuration.fully_qualified_name,
                table_configuration.column_selection_list,
            )

            validation_config = self._get_validation_configuration(
                table_configuration, default_configuration
            )

            (
                source_table_column_metadata,
                target_table_column_metadata,
            ) = self._generate_table_column_metadata(
                table_configuration=table_configuration,
                extractor=executor.source_extractor,
            )

            executor.execute_validation_levels(
                validation_config,
                table_configuration,
                source_table_column_metadata,
                target_table_column_metadata,
            )

            LOGGER.info(
                "Completed processing table: %s",
                table_configuration.fully_qualified_name,
            )

        LOGGER.info("Completed validation execution for all tables")

        # Flush all buffered validation data to file after processing all tables
        self._flush_validation_reports()

    @log
    def _flush_validation_reports(self) -> None:
        """Flush all buffered validation data to the report file.

        This method is called after all tables have been processed to write
        all accumulated validation results to the CSV report file.
        """
        buffer = ValidationReportBuffer()

        if buffer.has_data():
            report_file_path = buffer.flush_to_file(self.context)
            LOGGER.info(
                "Successfully flushed validation report buffer to: %s", report_file_path
            )
        else:
            LOGGER.info("No validation data to flush - buffer is empty")

    @log
    def _get_validation_configuration(
        self,
        table: TableConfiguration,
        default_configuration: Optional[ValidationConfiguration],
    ) -> ValidationConfiguration:
        """Get the validation configuration for a table.

        Args:
            table: Table configuration object
            default_configuration: Default validation configuration

        Returns:
            ValidationConfiguration: The configuration to use for this table

        """
        if table.validation_configuration:
            LOGGER.debug(
                "Using table-specific validation configuration for %s",
                table.fully_qualified_name,
            )
            return table.validation_configuration
        elif default_configuration:
            LOGGER.debug(
                "Using default validation configuration for %s",
                table.fully_qualified_name,
            )
            return default_configuration
        else:
            LOGGER.debug(
                "Using empty validation configuration for %s",
                table.fully_qualified_name,
            )
            return ValidationConfiguration()

    def _report_progress_for_table(
        self, object_name: str, columns_to_validate: list[str]
    ) -> None:
        """Report progress for table validation.

        Args:
            object_name: The fully qualified name of the database object
            columns_to_validate: List of columns being validated

        """
        if not self.context.output_handler.console_output_enabled:
            LOGGER.debug(
                "Reporting progress for table: %s with %d columns",
                object_name,
                len(columns_to_validate),
            )
            report_progress(
                ProgressMetadata(
                    table=object_name,
                    columns=columns_to_validate,
                    run_id=self.context.run_id,
                    run_start_time=self.context.run_start_time,
                )
            )

    @log
    def _generate_table_column_metadata(
        self, table_configuration: TableConfiguration, extractor: ConnectorBase
    ) -> tuple[TableColumnMetadata, TableColumnMetadata]:
        """Generate metadata for source and target tables.

        Args:
            table_configuration: Table configuration containing all necessary metadata.
            extractor: The extractor to use for extracting metadata.

        Returns:
            tuple[TableColumnMetadata, TableColumnMetadata]: Tuple containing source and target
            table column metadata models.

        """
        LOGGER.info(
            "Loading table column metadata model for: %s",
            table_configuration.fully_qualified_name,
        )

        table_column_metadata_from_source_df = (
            self._extract_table_column_metadata_from_source(
                table_configuration=table_configuration, extractor=extractor
            )
        )

        LOGGER.debug("Generating source table column metadata model")

        source_table_column_metadata = self._generate_source_table_column_metadata(
            table_column_metadata_from_source_df=table_column_metadata_from_source_df
        )

        LOGGER.debug("Successfully generated source table column metadata model")

        LOGGER.debug("Generating target table column metadata model")

        target_table_column_metadata = self._generate_target_table_column_metadata(
            table_column_metadata_from_source_df=table_column_metadata_from_source_df,
            table_configuration=table_configuration,
            datatypes_mappings=self.context.datatypes_mappings,
        )

        LOGGER.debug("Successfully generated target table column metadata model")

        LOGGER.info(
            "Successfully loaded table column metadata model for: %s",
            table_configuration.fully_qualified_name,
        )

        return source_table_column_metadata, target_table_column_metadata

    def _generate_source_table_column_metadata(
        self, table_column_metadata_from_source_df: pd.DataFrame
    ) -> TableColumnMetadata:
        try:
            table_column_metadata_model = TableColumnMetadata(
                table_column_metadata_from_source_df
            )

            return table_column_metadata_model

        except Exception as e:
            LOGGER.error(
                "Error generating source table column metadata model: %s", str(e)
            )
            raise ValueError(
                "Failed to generate source table column metadata model"
            ) from e

    def _extract_table_column_metadata_from_source(
        self,
        table_configuration: TableConfiguration,
        extractor: ConnectorBase,
    ) -> pd.DataFrame:
        """Extract table column metadata from the source.

        Args:
            table_configuration: Table configuration containing all necessary metadata.
            extractor: The extractor to use for extracting metadata.

        Returns:
            pd.DataFrame: DataFrame containing the table column metadata.

        """
        table_column_metadata_df = extractor.extract_table_column_metadata(
            table_configuration=table_configuration,
            context=self.context,
        )

        return table_column_metadata_df

    def _generate_target_table_column_metadata(
        self,
        table_column_metadata_from_source_df: pd.DataFrame,
        table_configuration: TableConfiguration,
        datatypes_mappings: dict[str, str],
    ) -> TableColumnMetadata:
        try:
            local_df = table_column_metadata_from_source_df.copy()
            local_df[DATABASE_NAME_KEY] = table_configuration.target_database
            local_df[SCHEMA_NAME_KEY] = table_configuration.target_schema
            local_df[TABLE_NAME_KEY] = table_configuration.target_name
            local_df[COLUMN_DATATYPE] = local_df[COLUMN_DATATYPE].apply(
                lambda datatype_key: datatypes_mappings[datatype_key]
            )
            table_column_metadata_model = TableColumnMetadata(local_df)
            return table_column_metadata_model

        except Exception as e:
            LOGGER.error(
                "Error generating source table column metadata model: %s", str(e)
            )
            raise ValueError(
                "Failed to generate source table column metadata model"
            ) from e
