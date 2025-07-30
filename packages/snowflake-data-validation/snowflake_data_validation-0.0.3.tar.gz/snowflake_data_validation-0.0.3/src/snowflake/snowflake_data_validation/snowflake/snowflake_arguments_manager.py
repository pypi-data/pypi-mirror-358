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

from typing import Optional

import typer

from snowflake.snowflake_data_validation.configuration.model.configuration_model import (
    ConfigurationModel,
)
from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
    NullConnector,
)
from snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake import (
    ConnectorSnowflake,
)
from snowflake.snowflake_data_validation.utils.arguments_manager_base import (
    ArgumentsManagerBase,
)
from snowflake.snowflake_data_validation.utils.console_output_handler import (
    ConsoleOutputHandler,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CREDENTIALS_CONNECTION_MODE,
    DEFAULT_CONNECTION_MODE,
    NAME_CONNECTION_MODE,
    ExecutionMode,
    Platform,
)


class SnowflakeArgumentsManager(ArgumentsManagerBase):

    """Arguments manager for Snowflake-to-Snowflake connections and configuration."""

    def __init__(self):
        """Initialize the Snowflake arguments manager."""
        super().__init__(Platform.SNOWFLAKE, Platform.SNOWFLAKE)

    @property
    def is_snowflake_to_snowflake(self) -> bool:
        """Check if this is a Snowflake-to-Snowflake validation scenario.

        Returns:
            bool: True if both source and target are Snowflake

        """
        return True  # This manager is only used for Snowflake-to-Snowflake

    def create_validation_environment_from_config(
        self,
        config_model: ConfigurationModel,
        data_validation_config_file: str,
        execution_mode: ExecutionMode,
        output_handler: Optional[ConsoleOutputHandler] = None,
    ):
        """Create a complete validation environment from configuration model.

        Args:
            config_model: The loaded configuration model
            data_validation_config_file: Path to the config file
            execution_mode: Execution mode (required, e.g., ExecutionMode.SYNC_VALIDATION)
            output_handler: Optional output handler

        Returns:
            Validation environment ready to run

        Raises:
            typer.BadParameter: If configuration is invalid
            ValueError: If required connections are missing

        """
        if execution_mode == ExecutionMode.ASYNC_VALIDATION:
            # For async validation, use NullConnector for both source and target
            source_connector = NullConnector()
            target_connector = NullConnector()
        else:
            # Set up connections
            source_connector = self._setup_source_from_config(config_model)
            target_connector = self._setup_target_from_config(config_model)

        # Create validation environment using output_directory_path from config
        return self.setup_validation_environment(
            source_connector=source_connector,
            target_connector=target_connector,
            data_validation_config_file=data_validation_config_file,
            output_directory_path=config_model.output_directory_path,
            output_handler=output_handler or ConsoleOutputHandler(),
        )

    def _setup_source_from_config(
        self, config_model: ConfigurationModel
    ) -> ConnectorBase:
        """Set up Snowflake source connection from configuration model."""
        if not config_model.source_connection:
            raise typer.BadParameter(
                message="No source connection configured in YAML file. "
                "Please add a source_connection section to your configuration file."
            )

        source_conn = config_model.source_connection

        mode = getattr(source_conn, "mode", NAME_CONNECTION_MODE)
        if mode == NAME_CONNECTION_MODE:
            return self.setup_source_connection(
                source_conn_mode=NAME_CONNECTION_MODE,
                snowflake_conn_file=getattr(source_conn, "name", None),
            )
        elif mode == DEFAULT_CONNECTION_MODE:
            return self.setup_source_connection(
                source_conn_mode=DEFAULT_CONNECTION_MODE,
            )
        else:
            raise typer.BadParameter(
                message=f"Unsupported source connection mode for Snowflake: {mode}. "
                "Supported modes are 'name' and 'default'. Use IPC commands for credentials mode."
            )

    def _setup_target_from_config(
        self, config_model: ConfigurationModel
    ) -> ConnectorBase:
        """Set up Snowflake target connection from configuration model."""
        if not config_model.target_connection:
            raise typer.BadParameter(
                message="No target connection configured in YAML file. "
                "Please add a target_connection section to your configuration file."
            )

        target_conn = config_model.target_connection

        mode = getattr(target_conn, "mode", NAME_CONNECTION_MODE)
        if mode == NAME_CONNECTION_MODE:
            return self.setup_target_connection(
                target_conn_mode=NAME_CONNECTION_MODE,
                target_connection_name=getattr(target_conn, "name", None),
            )
        elif mode == DEFAULT_CONNECTION_MODE:
            return self.setup_target_connection(
                target_conn_mode=DEFAULT_CONNECTION_MODE,
            )
        else:
            raise typer.BadParameter(
                message=f"Unsupported target connection mode for Snowflake: {mode}. "
                "Supported modes are 'name' and 'default'. Use IPC commands for credentials mode."
            )

    def setup_source_connection(
        self,
        source_conn_mode: str = DEFAULT_CONNECTION_MODE,
        snowflake_conn_file: Optional[str] = None,
        snowflake_credential_object: Optional[dict[str, str]] = None,
        # Direct connection parameters for IPC mode
        snow_account: Optional[str] = None,
        snow_username: Optional[str] = None,
        snow_database: Optional[str] = None,
        snow_schema: Optional[str] = None,
        snow_warehouse: Optional[str] = None,
        snow_role: Optional[str] = None,
        snow_authenticator: Optional[str] = None,
        snow_password: Optional[str] = None,
        **kwargs,
    ) -> ConnectorBase:
        """Set up Snowflake source connection based on connection mode.

        For Snowflake-to-Snowflake scenarios, source connections use the same
        connection modes as target connections (default or name) instead of
        toml or credentials.

        Args:
            source_conn_mode: Connection mode (default, name, credentials for IPC)
            snowflake_conn_file: Connection name for named connections
            snowflake_credential_object: Credentials dictionary
            snow_account: Direct account parameter (for IPC)
            snow_username: Direct username parameter (for IPC)
            snow_database: Direct database parameter (for IPC)
            snow_schema: Direct schema parameter (for IPC)
            snow_warehouse: Direct warehouse parameter (for IPC)
            snow_role: Direct role parameter (for IPC)
            snow_authenticator: Direct authenticator parameter (for IPC)
            snow_password: Direct password parameter (for IPC)
            **kwargs: Additional parameters

        Returns:
            ConnectorBase: Configured Snowflake connector

        """
        if (
            snow_account
            and snow_username
            and snow_database
            and snow_schema
            and snow_warehouse
        ):
            snowflake_credential_object = {
                "account": snow_account,
                "username": snow_username,
                "database": snow_database,
                "schema": snow_schema,
                "warehouse": snow_warehouse,
            }

            if snow_role:
                snowflake_credential_object["role"] = snow_role
            if snow_authenticator:
                snowflake_credential_object["authenticator"] = snow_authenticator
            if snow_password:
                snowflake_credential_object["password"] = snow_password

            source_conn_mode = CREDENTIALS_CONNECTION_MODE

        return self._setup_snowflake_connection(
            source_conn_mode, snowflake_conn_file, snowflake_credential_object
        )

    def setup_target_connection(
        self,
        target_conn_mode: str = DEFAULT_CONNECTION_MODE,
        target_connection_name: Optional[str] = None,
        target_credential_object: Optional[dict[str, str]] = None,
        # For Snowflake-to-Snowflake
        target_snow_account: Optional[str] = None,
        target_snow_username: Optional[str] = None,
        target_snow_database: Optional[str] = None,
        target_snow_schema: Optional[str] = None,
        target_snow_warehouse: Optional[str] = None,
        target_snow_role: Optional[str] = None,
        target_snow_authenticator: Optional[str] = None,
        target_snow_password: Optional[str] = None,
        **kwargs,
    ) -> ConnectorBase:
        """Set up Snowflake target connection for Snowflake-to-Snowflake validation.

        Args:
            target_conn_mode: Connection mode for target Snowflake
            target_connection_name: Connection name for named connections
            target_credential_object: Target Snowflake credentials dictionary
            target_snow_account: Direct target account parameter (for IPC)
            target_snow_username: Direct target username parameter (for IPC)
            target_snow_database: Direct target database parameter (for IPC)
            target_snow_schema: Direct target schema parameter (for IPC)
            target_snow_warehouse: Direct target warehouse parameter (for IPC)
            target_snow_role: Direct target role parameter (for IPC)
            target_snow_authenticator: Direct target authenticator parameter (for IPC)
            target_snow_password: Direct target password parameter (for IPC)
            **kwargs: Additional parameters

        Returns:
            ConnectorBase: Configured Snowflake target connector

        """
        if (
            target_snow_account
            and target_snow_username
            and target_snow_database
            and target_snow_schema
            and target_snow_warehouse
        ):
            target_credential_object = {
                "account": target_snow_account,
                "username": target_snow_username,
                "database": target_snow_database,
                "schema": target_snow_schema,
                "warehouse": target_snow_warehouse,
            }

            if target_snow_role:
                target_credential_object["role"] = target_snow_role
            if target_snow_authenticator:
                target_credential_object["authenticator"] = target_snow_authenticator
            if target_snow_password:
                target_credential_object["password"] = target_snow_password

            target_conn_mode = CREDENTIALS_CONNECTION_MODE

        return self._setup_snowflake_connection(
            target_conn_mode, target_connection_name, target_credential_object
        )

    def get_source_templates_path(self) -> str:
        """Get Snowflake templates path."""
        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, "extractor", "templates")

    def get_target_templates_path(self) -> str:
        """Get Snowflake target templates path (same as source for Snowflake-to-Snowflake)."""
        return self.get_source_templates_path()

    def _setup_snowflake_connection(
        self,
        conn_mode: str,
        snowflake_conn_file: Optional[str],
        snowflake_credential_object: Optional[dict[str, str]] = None,
    ) -> ConnectorSnowflake:
        """Set up Snowflake connector based on connection mode."""
        try:
            connector_snowflake = ConnectorSnowflake()

            connection_params: dict[str, str] = {"mode": conn_mode}

            if conn_mode == NAME_CONNECTION_MODE:
                connection_params["connection_name"] = snowflake_conn_file

            if snowflake_credential_object:
                # Validate required parameters for credentials mode
                if conn_mode == CREDENTIALS_CONNECTION_MODE:
                    required_params = [
                        "account",
                        "username",
                        "database",
                        "schema",
                        "warehouse",
                    ]
                    missing_params = [
                        param
                        for param in required_params
                        if not snowflake_credential_object.get(param)
                    ]
                    if missing_params:
                        raise typer.BadParameter(
                            message=f"Missing required Snowflake connection parameters: {', '.join(missing_params)}"
                        )

                connection_params.update(snowflake_credential_object)

            try:
                connector_snowflake.connect(**connection_params)
            except ConnectionError as e:
                raise ConnectionError(
                    f"Failed to establish Snowflake connection: {e}"
                ) from e
            except ImportError as e:
                raise ImportError(f"Snowflake dependencies not available: {e}") from e
            except typer.BadParameter:
                raise  # Re-raise parameter errors as-is

            return connector_snowflake

        except (typer.BadParameter, ConnectionError, ImportError):
            raise  # Re-raise these as-is
        except Exception as e:
            raise RuntimeError(
                f"Unexpected error setting up Snowflake connection: {e}"
            ) from e
