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


import os

import jinja2

from snowflake.snowflake_data_validation.utils.constants import (
    ERROR_GENERATING_TEMPLATE,
    TABLE_METADATA_QUERY,
    TEMPLATE_NOT_FOUND,
)


class SQLQueriesTemplateGenerator:
    def __init__(self, jinja_templates_folder_path: str):
        """Initialize the SQLQueriesTemplateGenerator.

        Set up the template directory and initialize the Jinja2 environment
        with a file system loader pointing to the template directory.

        Attributes:
            template_dir (str): The directory where Jinja2 templates are stored.
            env (jinja2.Environment): The Jinja2 environment for loading templates.

        """
        self.template_dir = os.path.join(jinja_templates_folder_path)
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.template_dir))

    def generate_table_metadata_sql(
        self,
        platform: str,
        table_name: str,
        schema_name: str,
        fully_qualified_name: str,
        where_clause: str,
        has_where_clause: bool,
        column_selection_list: list[str],
        use_as_exclude_list: bool,
    ):
        """Generate SQL query for table metadata based on the provided table configuration and platform.

        Args:
            platform (str): The platform identifier (e.g., Platform.SNOWFLAKE.value, Platform.SQLSERVER.value).
            table_name (str): The name of the table for which the SQL query is being generated.
            schema_name (str): The name of the schema containing the table.
            fully_qualified_name (str): The fully qualified name of the table.
            where_clause (str): Optional WHERE clause to filter results.
            has_where_clause (bool): Indicates if a WHERE clause is present.
            column_selection_list (list[str]): List of columns to include in the query.
            use_as_exclude_list (bool): Flag to indicate if columns should be treated as an exclude list.

        Returns:
            str: The generated SQL query.

        Raises:
            ValueError: If the template file for the specified platform is not found.
            Exception: If there is an error generating the template.

        """
        template_file = TABLE_METADATA_QUERY.format(platform=platform)
        try:
            template = self.env.get_template(template_file)
            sql = template.render(
                object_name=table_name,
                object_schema=schema_name,
                fully_qualified_name=fully_qualified_name,
                where_clause=where_clause,
                has_where_clause=has_where_clause,
                columns=column_selection_list,
                use_as_exclude_list=use_as_exclude_list,
            )
            return sql
        except jinja2.exceptions.TemplateNotFound:
            raise ValueError(
                TEMPLATE_NOT_FOUND.format(
                    platform=platform,
                    template_file=template_file,
                    template_dir=self.template_dir,
                )
            ) from None
        except Exception as e:
            raise Exception(ERROR_GENERATING_TEMPLATE.format(exception=e)) from e

    def generate_columns_metrics_metadata_sql(
        self, table_name: str, column_names: list[str], platform: str
    ):
        """Generate an SQL query for column metrics metadata using a Jinja2 template.

        Args:
            table_name (str): The name of the table for which the SQL query is being generated.
            column_names (list[str]): A list of column names to include in the query.
            platform (str): The platform identifier (e.g., Platform.SNOWFLAKE.value, Platform.SQLSERVER.value)

        Returns:
            str: The rendered SQL query as a string.

        Raises:
            ValueError: If the template file for the specified platform is not found.
            Exception: If an error occurs during template rendering.

        """
        template_file = f"{platform}_columns_metrics_query.sql.j2"  # Naming convention: platform.sql.j2
        try:
            template = self.env.get_template(template_file)
            sql = template.render(table_name=table_name, column_names=column_names)
            return sql
        except jinja2.exceptions.TemplateNotFound:
            raise ValueError(
                f"Template not found for platform: {platform}. Please create {template_file} "
                f"in the {self.template_dir} directory."
            ) from None
        except Exception as e:
            raise Exception(f"Error generating template: {e}") from e

    def extract_table_column_metadata(
        self, database_name: str, schema_name: str, table_name: str, platform: str
    ) -> str:
        """Generate a SQL query to extract table column metadata.

        Args:
            database_name (str): The name of the database containing the table.
            schema_name (str): The name of the schema containing the table.
            table_name (str): The name of the table for which metadata is to be extracted.
            platform (str): The platform identifier (e.g., Platform.SNOWFLAKE.value, Platform.SQLSERVER.value)

        Returns:
            str: The SQL query string to extract table metadata.

        Raises:
            ValueError: If the template file for the specified platform is not found.
            Exception: If an error occurs during template rendering.

        """
        template_file = f"{platform}_get_columns_metadata.sql.j2"
        try:
            template = self.env.get_template(template_file)
            sql = template.render(
                database_name=database_name,
                schema_name=schema_name,
                table_name=table_name,
            )
            return sql
        except jinja2.exceptions.TemplateNotFound:
            raise ValueError(
                f"Template not found for platform: {platform}. Please create {template_file} "
                f"in the {self.template_dir} directory."
            ) from None
        except Exception as e:
            raise Exception(f"Error generating template: {e}") from e
