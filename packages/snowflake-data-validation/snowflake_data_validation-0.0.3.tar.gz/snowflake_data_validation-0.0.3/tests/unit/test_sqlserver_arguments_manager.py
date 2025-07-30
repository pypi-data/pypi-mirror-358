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

"""Tests for SqlServerArgumentsManager."""

import pytest
from unittest.mock import Mock, patch, MagicMock

import typer

from snowflake.snowflake_data_validation.configuration.model.configuration_model import (
    ConfigurationModel,
)
from snowflake.snowflake_data_validation.sqlserver.sqlserver_arguments_manager import (
    SqlServerArgumentsManager,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CREDENTIALS_CONNECTION_MODE,
    Platform,
)


class TestSqlServerArgumentsManager:
    """Test cases for SqlServerArgumentsManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.args_manager = SqlServerArgumentsManager()

    def test_init_and_properties(self):
        """Test SqlServerArgumentsManager initialization and basic properties."""
        assert self.args_manager.source_platform == Platform.SQLSERVER
        assert self.args_manager.target_platform == Platform.SNOWFLAKE

        # Test paths
        assert self.args_manager.get_source_templates_path() is not None
        assert self.args_manager.get_target_templates_path() is not None

    @patch(
        "snowflake.snowflake_data_validation.sqlserver.sqlserver_arguments_manager.ConnectorSqlServer"
    )
    def test_setup_source_connection_success(self, mock_sqlserver_connector):
        """Test successful setup of SQL Server source connection."""
        mock_connector = MagicMock()
        mock_sqlserver_connector.return_value = mock_connector

        result = self.args_manager.setup_source_connection(
            source_host="localhost",
            source_port=1433,
            source_username="sa",
            source_password="password",
            source_database="testdb",
        )

        assert result == mock_connector
        mock_sqlserver_connector.assert_called_once()

    def test_setup_source_connection_missing_credentials(self):
        """Test source connection setup with missing credentials."""
        with pytest.raises(typer.BadParameter) as exc_info:
            self.args_manager.setup_source_connection(
                source_conn_mode=CREDENTIALS_CONNECTION_MODE,
                sqlserver_credential_object=None,
            )

        assert "SQL Server connection credentials are required" in str(exc_info.value)

    def test_setup_from_config_missing_connection(self):
        """Test setup from config with missing connections."""
        mock_config = Mock(spec=ConfigurationModel)
        mock_config.source_connection = None

        with pytest.raises(typer.BadParameter) as exc_info:
            self.args_manager._setup_source_from_config(mock_config)

        assert "No source connection configured in YAML file" in str(exc_info.value)

    def test_setup_target_from_config_unsupported_platform(self):
        """Test target setup with unsupported platform."""
        mock_config = Mock(spec=ConfigurationModel)
        mock_config.target_connection = Mock()
        mock_config.target_platform = "Oracle"

        with pytest.raises(typer.BadParameter) as exc_info:
            self.args_manager._setup_target_from_config(mock_config)

        assert "Unsupported target platform: Oracle" in str(exc_info.value)
