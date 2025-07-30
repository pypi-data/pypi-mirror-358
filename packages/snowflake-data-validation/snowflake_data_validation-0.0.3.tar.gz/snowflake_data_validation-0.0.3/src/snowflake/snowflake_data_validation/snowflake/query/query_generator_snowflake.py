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

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.connector.connector_base import ConnectorBase
from snowflake.snowflake_data_validation.query.query_generator_base import (
    QueryGeneratorBase,
)
from snowflake.snowflake_data_validation.snowflake.extractor.snowflake_cte_generator import (
    generate_cte_query,
    generate_outer_query,
)
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
)
from snowflake.snowflake_data_validation.utils.constants import (
    Platform,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext
from snowflake.snowflake_data_validation.utils.progress_reporter import (
    ProgressMetadata,
    report_progress,
)


LOGGER = logging.getLogger(__name__)


class QueryGeneratorSnowflake(QueryGeneratorBase):

    """Snowflake-specific implementation of query generator."""

    def generate_schema_query(self, table_context: TableContext) -> str:
        """Generate the SQL query to extract metadata for a specific table in Snowflake.

        This implementation will delegate to the existing template-based query generation
        or implement Snowflake-specific query logic.

        Args:
            table_context (TableContext): Configuration object containing table properties.

        Returns:
            str: SQL query string to extract metadata for the specified table.

        """
        query = table_context.sql_generator.generate_table_metadata_sql(
            platform=table_context.platform.value,
            table_name=table_context.table_name,
            schema_name=table_context.schema_name,
            fully_qualified_name=table_context.fully_qualified_name,
            where_clause=table_context.where_clause,
            has_where_clause=table_context.has_where_clause,
            column_selection_list=table_context.column_selection_list,
            use_as_exclude_list=table_context.use_as_exclude_list,
        )

        return query

    def generate_metrics_query(
        self,
        table_context: TableContext,
        output_handler: OutputHandlerBase,
        connector: ConnectorBase,
    ) -> str:
        """Generate the SQL query to extract metadata for specific columns in a table in Snowflake.

        Args:
            table_context (TableConfiguration): Configuration object containing table properties.
            output_handler (OutputHandlerBase): Handler for output messages and progress reporting.
            connector (ConnectorBase): Database connector instance for executing queries.

        Returns:
            str: SQL query string to extract column metadata for the specified columns.

        """
        # Get column data types
        # TODO: This should be done in L0
        # JIRA: https://snowflakecomputing.atlassian.net/browse/SNOW-2128667
        col_types_query = f"""
        SELECT
            COLUMN_NAME,
            DATA_TYPE
        FROM
            INFORMATION_SCHEMA.COLUMNS
        WHERE
            TABLE_CATALOG = '{table_context.database_name.upper()}'
            AND TABLE_SCHEMA = '{table_context.schema_name.upper()}'
            AND TABLE_NAME = '{table_context.table_name.upper()}';
        """
        try:
            columns_types = connector.execute_query(col_types_query)
        except Exception as e:
            error_message = (
                "Failed to retrieve column information for %s.",
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
            raise Exception(error_message) from e

        if not columns_types:
            error_message = (
                f"No columns found for {table_context.fully_qualified_name}."
            )
            LOGGER.error(error_message)
            raise Exception(error_message)

        cte_queries = []
        cte_names = []
        metrics = []

        columns_to_validate_upper = (
            [col.upper() for col in table_context.column_selection_list]
            if table_context.column_selection_list
            else []
        )

        for row in columns_types:
            col_name = row.COLUMN_NAME
            col_type = row.DATA_TYPE

            # This is a temporary fix for current issue displaying "TEXT" instead of "VARCHAR" in the data_type column
            # TODO: Remove this once the issue is fixed
            if col_type == "TEXT":
                col_type = "VARCHAR"

            col_name_upper = col_name.upper()

            if columns_to_validate_upper:
                if table_context.use_as_exclude_list:
                    if col_name_upper in columns_to_validate_upper:
                        LOGGER.debug(
                            "Skip %s, because column is in the exclusion list.",
                            col_name_upper,
                        )
                        continue
                else:
                    if col_name_upper not in columns_to_validate_upper:
                        LOGGER.warning(
                            "Skip %s in conf.yaml, because does not exist in %s.",
                            col_name_upper,
                            table_context.fully_qualified_name,
                        )
                        continue

            cte_query, cte_name, metric_list = generate_cte_query(
                metrics_templates=table_context.templates_loader_manager.metrics_templates,
                col_name=col_name,
                col_type=col_type,
                fully_qualified_name=table_context.fully_qualified_name,
                where_clause=table_context.where_clause,
                has_where_clause=table_context.has_where_clause,
                sql_generator=table_context.sql_generator,
            )
            if cte_query is None:
                continue
            cte_queries.append(cte_query)
            cte_names.append(cte_name)
            metrics.append(metric_list)

        if not cte_queries:
            error_message = (
                f"Metrics templates are missing for the column data types in "
                f"{table_context.fully_qualified_name}."
            )
            LOGGER.error(error_message)
            raise Exception(error_message)

        outer_query = generate_outer_query(cte_names, metrics)
        final_query = "WITH " + ", ".join(cte_queries) + "\n" + outer_query
        return final_query

    def generate_row_md5_query(
        self, table_context: TableConfiguration, context: Context
    ) -> str:
        """Generate the SQL query to extract the MD5 checksum for a given table in Snowflake.

        Args:
            table_context (TableConfiguration): Configuration object containing table properties.
            context (Context): The execution context containing relevant configuration and runtime information.

        Returns:
            str: SQL query string to extract MD5 checksum information.

        """
        return "SELECT 1;"

    def generate_table_column_metadata_query(
        self, table_configuration: TableConfiguration, context: Context
    ) -> str:
        """Generate the SQL query to extract column information metadata for a given table in Snowflake.

        Args:
            table_configuration (TableConfiguration): Configuration object containing table properties.
            context (Context): The execution context containing relevant configuration and runtime information.

        Returns:
            str: SQL query string to extract column information metadata.

        """
        query = context.sql_generator.extract_table_column_metadata(
            database_name=table_configuration.source_database,
            schema_name=table_configuration.source_schema,
            table_name=table_configuration.source_table,
            platform=Platform.SNOWFLAKE.value,
        )

        return query
