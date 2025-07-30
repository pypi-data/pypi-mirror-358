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

import typer

from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase as BaseConnector,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CONNECTION_NOT_ESTABLISHED,
    CREDENTIALS_CONNECTION_MODE,
    DEFAULT_CONNECTION_MODE,
    FAILED_TO_EXECUTE_QUERY,
    INVALID_CONNECTION_MODE,
    NAME_CONNECTION_MODE,
)
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowpark import Session


LOGGER = logging.getLogger(__name__)


class ConnectorSnowflake(BaseConnector):

    """A class to manage connections and queries to a Snowflake database."""

    @log
    def __init__(self) -> None:
        """Initialize the SnowflakeConnector class."""
        super().__init__()
        self.connection: Optional[Session] = None

    @log
    def connect(
        self,
        mode: str = DEFAULT_CONNECTION_MODE,
        connection_name: str = "",
        account: str = "",
        username: str = "",
        database: str = "",
        schema: str = "",
        warehouse: str = "",
        role: str = "",
        password: str = "",
        authenticator: str = "",
    ) -> None:
        """Establish a connection to the Snowflake database.

        Args:
            mode (str): The mode of connection. Defaults to "default".
                        - "default": Connects using the default session configuration.
                        - "name": Connects using a named connection configuration.
                        - "credentials": Connects using the provided credentials.
            connection_name (str): The name of the connection configuration to use
                when mode is "name". Defaults to an empty string.
            account (str): The Snowflake account name.
            username (str): The username for the Snowflake account.
            database (str): The name of the database to connect to.
            schema (str): The schema within the database to use.
            warehouse (str): The name of the warehouse to use.
            role (str): The role to assume for the session.
            password (str): The password for the Snowflake account.
            authenticator (str): The authenticator to use for the Snowflake connection.

        Returns:
            None: Returns a Snowflake session object.

        Raises:
            ConnectionError: If the connection cannot be established.
            typer.BadParameter: If invalid parameters are provided.
            ImportError: If Snowflake connector dependencies are missing.

        """
        try:
            if mode == DEFAULT_CONNECTION_MODE:
                # Use the current Snowflake session
                self.connection = Session.builder.getOrCreate()

            elif mode == NAME_CONNECTION_MODE:
                if not connection_name:
                    raise typer.BadParameter(
                        "Connection name is required for 'name' mode"
                    )
                # Use named connection
                self.connection = Session.builder.config(
                    "connection_name", connection_name
                ).getOrCreate()

            elif mode == CREDENTIALS_CONNECTION_MODE:
                if not all([account, username, database, warehouse]):
                    raise typer.BadParameter(
                        "Account, username, database, and warehouse are required for 'credentials' mode"
                    )

                # Build connection configuration
                connection_config = {
                    "account": account,
                    "user": username,
                    "database": database,
                    "warehouse": warehouse,
                }

                if schema:
                    connection_config["schema"] = schema
                if role:
                    connection_config["role"] = role
                if password:
                    connection_config["password"] = password
                if authenticator:
                    connection_config["authenticator"] = authenticator

                # Create session with credentials
                self.connection = Session.builder.configs(connection_config).create()

            else:
                raise typer.BadParameter(
                    message=f"{INVALID_CONNECTION_MODE}. Selected mode: {mode}. "
                    f"Valid modes are 'default', 'name', or 'credentials'."
                )

            # Test the connection by executing a simple query
            try:
                self.connection.sql("SELECT 1").collect()
                LOGGER.info("Successfully connected to Snowflake")
            except Exception as e:
                self.connection = None
                LOGGER.error("Failed to verify Snowflake connection: %s", str(e))
                raise ConnectionError(
                    f"Failed to verify Snowflake connection: {e}"
                ) from e

        except ImportError as e:
            LOGGER.error("Failed to import Snowflake dependencies: %s", str(e))
            raise ImportError(
                f"Failed to import Snowflake dependencies: {e}. "
                "Please ensure snowflake-snowpark-python is installed."
            ) from e
        except typer.BadParameter:
            raise  # Re-raise parameter errors as-is
        except ConnectionError:
            raise  # Re-raise connection errors as-is
        except Exception as e:
            LOGGER.error("Failed to establish Snowflake connection: %s", str(e))
            raise ConnectionError(
                f"Failed to establish Snowflake connection: {e}"
            ) from e

    @log
    def execute_query(self, query: str) -> list[tuple]:
        """Execute a given SQL query using the Snowflake connector and return the results.

        Args:
            query (str): The SQL query to be executed.

        Returns:
            list[tuple]: A list of tuples containing the query results.

        Raises:
            Exception: If the connector is not established or if the query execution fails.

        """
        if self.connection is None:
            LOGGER.error("Database connection not established")
            raise Exception(CONNECTION_NOT_ESTABLISHED)
        try:
            results = self.connection.sql(query).collect()
            LOGGER.debug("Query executed successfully, returned %d rows", len(results))
            return results
        except Exception as e:
            LOGGER.error("Failed to execute query: %s", str(e))
            raise Exception(FAILED_TO_EXECUTE_QUERY.format(query=query)) from e

    @log
    def close(self) -> None:
        """Close the connection to the Snowflake database."""
        if self.connection:
            self.connection.close()
            LOGGER.info("Snowflake connection closed successfully")
        else:
            LOGGER.debug("No active connection to close")
