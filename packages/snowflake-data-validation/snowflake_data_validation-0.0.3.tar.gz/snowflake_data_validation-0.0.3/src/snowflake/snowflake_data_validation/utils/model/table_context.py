from snowflake.snowflake_data_validation.extractor.sql_queries_template_generator import (
    SQLQueriesTemplateGenerator,
)
from snowflake.snowflake_data_validation.utils.constants import Origin, Platform
from snowflake.snowflake_data_validation.utils.model.column_metadata import (
    ColumnMetadata,
)
from snowflake.snowflake_data_validation.utils.model.templates_loader_manager import (
    TemplatesLoaderManager,
)


class TableContext:

    """Context for a table in the data validation process.

    Attributes:
        platform (Platform): The platform where the table resides.
        origin (Origin): The origin of the table data.
        fully_qualified_name (str): The fully qualified name of the table.
        table_name (str): The name of the table.
        schema_name (str): The schema name of the table.
        database_name (str): The database name of the table.
        columns (list[ColumnMetadata]): List of column metadata for the table.
        run_id (str): Unique identifier for the validation run.
        run_start_time (str): Start time of the validation run.
        where_clause (str): The WHERE clause for filtering data.
        has_where_clause (bool): Indicates if a WHERE clause is present.
        use_as_exclude_list (bool): Indicates if the table is used as an exclude list
                                    for validation.
        column_selection_list (list[str]): List of columns to be selected for validation.
        templates_loader_manager (TemplatesLoaderManager): Manager for loading SQL templates.
        sql_generator (SQLQueriesTemplateGenerator): Generator for SQL queries.

    """

    def __init__(
        self,
        platform: Platform,
        origin: Origin,
        fully_qualified_name: str,
        table_name: str,
        schema_name: str,
        database_name: str,
        columns: list[ColumnMetadata],
        run_id: str,
        run_start_time: str,
        where_clause: str,
        has_where_clause: bool,
        use_as_exclude_list: bool,
        column_selection_list: list[str],
        templates_loader_manager: TemplatesLoaderManager,
        sql_generator: SQLQueriesTemplateGenerator,
    ):
        self.platform = platform
        self.origin = origin
        self.fully_qualified_name = fully_qualified_name
        self.database_name = database_name
        self.schema_name = schema_name
        self.table_name = table_name
        self.columns = columns
        self.where_clause = (where_clause,)
        self.has_where_clause = has_where_clause
        self.use_as_exclude_list = use_as_exclude_list
        self.column_selection_list = column_selection_list
        self.run_id = run_id
        self.run_start_time = run_start_time
        self.templates_loader_manager = templates_loader_manager
        self.sql_generator = sql_generator
