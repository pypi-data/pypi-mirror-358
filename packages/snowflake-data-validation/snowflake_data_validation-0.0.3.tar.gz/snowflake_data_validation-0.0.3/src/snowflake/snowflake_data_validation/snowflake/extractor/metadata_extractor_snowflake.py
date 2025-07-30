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

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.extractor.metadata_extractor_base import (
    MetadataExtractorBase,
)
from snowflake.snowflake_data_validation.query.query_generator_base import (
    QueryGeneratorBase,
)

# WIP check what needs to be generalized and what not in the template generator
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
    OutputMessageLevel,
)
from snowflake.snowflake_data_validation.utils.constants import (
    COLUMN_VALIDATED,
    Platform,
)

# WIP check what needs to be generalized and what not in the template generator
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext
from snowflake.snowflake_data_validation.utils.progress_reporter import (
    ProgressMetadata,
    report_progress,
)


LOGGER = logging.getLogger(__name__)


class MetadataExtractorSnowflake(MetadataExtractorBase):

    """Implement methods to extract metadata from Snowflake database tables."""

    @log
    def __init__(
        self,
        connector: ConnectorBase,
        query_generator: QueryGeneratorBase,
        report_path: str = "",
    ):
        """Initialize the Snowflake metadata extractor with a Snowflake connector and query generator.

        Args:
            connector (ConnectorSnowflake): Snowflake database connector instance.
            query_generator (QueryGeneratorBase): Query generator instance.
            report_path (str): Optional path for output reports.

        """
        LOGGER.debug("Initializing MetadataExtractorSnowflake")
        super().__init__(connector, query_generator, report_path)
        LOGGER.debug("MetadataExtractorSnowflake initialized successfully")

    @log
    def extract_schema_metadata(
        self,
        table_context: TableContext,
        output_handler: OutputHandlerBase,
    ) -> pd.DataFrame:
        """Extract metadata for a specified table from a Snowflake database.

        Args:
            table_context (TableConfiguration): Configuration object containing table properties.
            output_handler (OutputHandlerBase): Output handler for logging and reporting messages.

        Returns:
            pd.DataFrame: A DataFrame containing the metadata information of the specified table.

        Raises:
            ValueError: If the fully qualified name is not in the correct format.
            DatabaseError: If there is an error executing the SQL query.

        """
        LOGGER.info(
            "Extracting schema metadata for table: %s",
            table_context.fully_qualified_name,
        )
        query = self.query_generator.generate_schema_query(table_context=table_context)

        LOGGER.debug(
            "Generated schema query for table: %s",
            table_context.fully_qualified_name,
        )

        try:
            result = self.connector.execute_query(query)
        except Exception:
            error_message = (
                "[Snowflake] Schema validation query failed for table: %s.",
                table_context.fully_qualified_name,
            )
            LOGGER.critical(error_message)
            if not output_handler.console_output_enabled:
                report_progress(
                    ProgressMetadata(
                        table=table_context.fully_qualified_name,
                        columns=table_context.column_selection_list,
                        run_id=table_context.run_id,
                        run_start_time=table_context.run_start_time,
                        errorMessage=error_message,
                    )
                )
            raise

        if not result:
            LOGGER.warning(
                "No schema metadata found for table: %s",
                table_context.fully_qualified_name,
            )
            output_handler.handle_message(
                message=f"No metadata found for table: {table_context.fully_qualified_name}",
                level=OutputMessageLevel.WARNING,
            )
            return pd.DataFrame()

        df = pd.DataFrame(result)
        LOGGER.info(
            "Successfully extracted schema metadata for table: %s (%d rows)",
            table_context.fully_qualified_name,
            len(df),
        )
        output_handler.handle_message(
            header="Snowflake metadata info:",
            dataframe=df,
            level=OutputMessageLevel.TARGET_RESULT,
        )
        return df

    @log
    def extract_metrics_metadata(
        self,
        table_context: TableContext,
        output_handler: OutputHandlerBase,
    ) -> pd.DataFrame:
        """Extract column-level metadata for a specified table from a Snowflake database.

        Args:
            table_context (TableContext): Configuration object containing table properties.
            output_handler (OutputHandlerBase): Output handler for logging and reporting messages.

        Returns:
            pd.DataFrame: A DataFrame containing the column metadata information of the specified table.

        Raises:
            ValueError: If the fully qualified name is not in the correct format.
            DatabaseError: If there is an error executing the SQL query.

        """
        LOGGER.info(
            "Extracting metrics metadata for table: %s",
            table_context.fully_qualified_name,
        )

        query = self.query_generator.generate_metrics_query(
            table_context=table_context,
            output_handler=output_handler,
            connector=self.connector,
        )
        if not query:
            LOGGER.warning(
                "No metrics query generated for table: %s",
                table_context.fully_qualified_name,
            )
            columns_names = [COLUMN_VALIDATED]
            return pd.DataFrame(columns=columns_names)

        LOGGER.debug(
            "Generated metrics query for table: %s", table_context.fully_qualified_name
        )
        try:
            result = self.connector.execute_query(query)
        except Exception:
            error_message = (
                "[Snowflake] Metrics validation query failed for table: %s.",
                table_context.fully_qualified_name,
            )
            LOGGER.critical(error_message)
            if not output_handler.console_output_enabled:
                report_progress(
                    ProgressMetadata(
                        table=table_context.fully_qualified_name,
                        columns=table_context.column_selection_list,
                        run_id=table_context.run_id,
                        run_start_time=table_context.run_start_time,
                        errorMessage=error_message,
                    )
                )
            raise

        if not result:
            LOGGER.warning(
                "No metrics metadata found for table: %s",
                table_context.fully_qualified_name,
            )
            output_handler.handle_message(
                message=f"No metadata found for table: {table_context.fully_qualified_name}",
                level=OutputMessageLevel.WARNING,
            )
            return pd.DataFrame()

        df = pd.DataFrame(result)
        LOGGER.info(
            "Successfully extracted metrics metadata for table: %s (%d rows)",
            table_context.fully_qualified_name,
            len(df),
        )
        output_handler.handle_message(
            header="Snowflake metadata info:",
            dataframe=df,
            level=OutputMessageLevel.TARGET_RESULT,
        )

        return df

    @log
    def extract_md5_checksum(
        self, fully_qualified_name: str, context: Context
    ) -> pd.DataFrame:
        """Extract MD5 checksum for a specified table from a Snowflake database.

        Args:
            fully_qualified_name (str): Fully qualified table name in format 'database.schema.table'.
            context (Context): The execution context containing relevant configuration and runtime information.

        Returns:
            pd.DataFrame: A DataFrame containing the MD5 checksum of the specified table.

        Raises:
            ValueError: If the fully qualified name is not in the correct format.
            DatabaseError: If there is an error executing the SQL query.

        """
        LOGGER.info("Extracting MD5 checksum for table: %s", fully_qualified_name)
        context.output_handler.handle_message(
            message=f"Extracting MD5 checksum for: {fully_qualified_name} on {Platform.SNOWFLAKE.value}",
            level=OutputMessageLevel.INFO,
        )

        # Create a TableConfiguration for the MD5 checksum query
        table_context = TableConfiguration(
            fully_qualified_name=fully_qualified_name,
            column_selection_list=[],
            use_column_selection_as_exclude_list=False,
            where_clause="",
            target_where_clause="",
            has_where_clause=False,
        )

        query = self.query_generator.generate_row_md5_query(table_context, context)
        LOGGER.debug("Generated MD5 checksum query for table: %s", fully_qualified_name)
        try:
            result = self.connector.execute_query(query)
        except Exception:
            error_message = (
                "[Snowflake] Row validation query failed for table: %s.",
                table_context.fully_qualified_name,
            )
            LOGGER.critical(error_message)
            if not context.output_handler.console_output_enabled:
                report_progress(
                    ProgressMetadata(
                        table=table_context.fully_qualified_name,
                        columns=table_context.column_selection_list,
                        run_id=context.run_id,
                        run_start_time=context.run_start_time,
                        errorMessage=error_message,
                    )
                )
            raise

        if not result:
            LOGGER.warning(
                "No MD5 checksum data found for table: %s", fully_qualified_name
            )
            context.output_handler.handle_message(
                message=f"No metadata found for table: {fully_qualified_name}",
                level=OutputMessageLevel.WARNING,
            )
            return pd.DataFrame()

        df = pd.DataFrame(result)
        LOGGER.info(
            "Successfully extracted MD5 checksum for table: %s", fully_qualified_name
        )
        context.output_handler.handle_message(
            header="Snowflake metadata info:",
            dataframe=df,
            level=OutputMessageLevel.TARGET_RESULT,
        )
        return df

    @log
    def extract_table_column_metadata(
        self,
        table_context: TableConfiguration,
        context: Context,
    ) -> pd.DataFrame:
        LOGGER.debug(
            "Extracting table column metadata for: %s",
            table_context.target_fully_qualified_name,
        )
        # Intentional return an empty DataFrame.
        LOGGER.debug(
            "Returning empty DataFrame for table column metadata (intentional)"
        )
        return pd.DataFrame()
