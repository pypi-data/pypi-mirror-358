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
from snowflake.snowflake_data_validation.sqlserver.extractor.sqlserver_cte_generator import (
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
from snowflake.snowflake_data_validation.utils.helpers import (
    NEWLINE,
)
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext


LOGGER = logging.getLogger(__name__)


class QueryGeneratorSqlServer(QueryGeneratorBase):

    """SQL Server-specific implementation of query generator."""

    def generate_schema_query(self, table_context: TableContext) -> str:
        """Generate the SQL query to extract metadata for a specific table in SQL Server.

        This implementation will delegate to the existing template-based query generation
        or implement SQL Server-specific query logic.

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
        """Generate the SQL query to extract metadata for specific columns in a table in SQL Server.

        Args:
            table_context (TableConfiguration): Configuration object containing table properties.
            metrics_templates (pd.DataFrame): DataFrame containing metrics templates to be applied.
            output_handler (OutputHandlerBase): Handler for output messages and progress reporting.
            connector (ConnectorBase): Database connector instance for executing queries.

        Returns:
            str: SQL query string to extract column metadata for the specified columns.

        """
        # JIRA: https://snowflakecomputing.atlassian.net/browse/SNOW-2128667
        # TODO: This should be done in L0
        col_types_query = f"""
        SELECT
            COLUMN_NAME,
            DATA_TYPE
        FROM
            INFORMATION_SCHEMA.COLUMNS
        WHERE
            TABLE_CATALOG = '{table_context.database_name}'
            AND TABLE_SCHEMA = '{table_context.schema_name}'
            AND TABLE_NAME = '{table_context.table_name}';
        """

        try:
            result = connector.execute_query(col_types_query)
        except Exception as e:
            error_message = f"Failed to retrieve column information for {table_context.fully_qualified_name}: {str(e)}"
            LOGGER.error(error_message)
            raise Exception(error_message) from e

        if not result or not result[1]:
            error_message = (
                f"No columns found for table: {table_context.fully_qualified_name}."
            )
            raise Exception(error_message)

        _, result_values = result

        cte_queries = []
        cte_names = []
        metrics = []

        columns_to_validate_upper = (
            [col.upper() for col in table_context.column_selection_list]
            if table_context.column_selection_list
            else []
        )

        for col_name, col_type in result_values:
            col_name_upper = col_name.upper()

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
                f"{table_context.fully_qualified_name}"
            )
            LOGGER.error(error_message)
            raise Exception(error_message)

        outer_query = generate_outer_query(cte_names, metrics)
        final_query = (
            "WITH " + ", ".join(cte_queries) + NEWLINE + outer_query
        )  # TODO: This should be a template
        return final_query

    def generate_row_md5_query(
        self, table_context: TableConfiguration, context: Context
    ) -> str:
        """Generate the SQL query to extract the MD5 checksum for a given table in SQL Server.

        Args:
            table_context (TableConfiguration): Configuration object containing table properties.
            context (Context): The execution context containing relevant configuration and runtime information.

        Returns:
            str: SQL query string to extract MD5 checksum information.

        """
        return context.sql_generator.generate_table_metadata_sql(
            fully_qualified_name=table_context.fully_qualified_name,
            table_context=table_context,
            platform=Platform.SQLSERVER.value,
        )

    def generate_table_column_metadata_query(
        self, table_configuration: TableConfiguration, context: Context
    ) -> str:
        """Generate the SQL query to extract column information metadata for a given table in SQL Server.

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
            platform=Platform.SQLSERVER.value,
        )

        return query
