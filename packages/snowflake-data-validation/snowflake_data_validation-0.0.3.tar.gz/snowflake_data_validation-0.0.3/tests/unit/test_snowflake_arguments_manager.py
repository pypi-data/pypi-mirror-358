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

"""Tests for SnowflakeArgumentsManager."""

import pytest
from unittest.mock import Mock, patch, MagicMock

import typer

from snowflake.snowflake_data_validation.configuration.model.configuration_model import (
    ConfigurationModel,
)
from snowflake.snowflake_data_validation.snowflake.snowflake_arguments_manager import (
    SnowflakeArgumentsManager,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CREDENTIALS_CONNECTION_MODE,
    DEFAULT_CONNECTION_MODE,
    NAME_CONNECTION_MODE,
    TOML_CONNECTION_MODE,
    Platform,
)


class TestSnowflakeArgumentsManager:
    """Test cases for SnowflakeArgumentsManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.args_manager = SnowflakeArgumentsManager()

    def test_init_and_properties(self):
        """Test SnowflakeArgumentsManager initialization and basic properties."""
        assert self.args_manager.source_platform == Platform.SNOWFLAKE
        assert self.args_manager.target_platform == Platform.SNOWFLAKE

        # Test paths
        assert self.args_manager.get_source_templates_path() is not None
        assert self.args_manager.get_target_templates_path() is not None

    @patch(
        "snowflake.snowflake_data_validation.snowflake.snowflake_arguments_manager.ConnectorSnowflake"
    )
    def test_setup_source_connection_success(self, mock_snowflake_connector):
        """Test successful setup of Snowflake source connection."""
        mock_connector = MagicMock()
        mock_snowflake_connector.return_value = mock_connector

        result = self.args_manager.setup_source_connection(
            snowflake_conn_mode=DEFAULT_CONNECTION_MODE,
        )

        assert result == mock_connector
        mock_snowflake_connector.assert_called_once()

    def test_setup_snowflake_connection_toml_mode_error(self):
        """Test that TOML connection mode raises error."""
        with pytest.raises(typer.BadParameter) as exc_info:
            self.args_manager._setup_snowflake_connection(
                conn_mode=TOML_CONNECTION_MODE,
                snowflake_conn_file=None,
            )

        assert "Invalid connection mode or missing configuration" in str(exc_info.value)

    def test_setup_from_config_missing_connection(self):
        """Test setup from config with missing connections."""
        mock_config = Mock(spec=ConfigurationModel)
        mock_config.source_connection = None

        with pytest.raises(typer.BadParameter) as exc_info:
            self.args_manager._setup_source_from_config(mock_config)

        assert "No source connection configured in YAML file" in str(exc_info.value)

    def test_setup_source_from_config_unsupported_mode(self):
        """Test setup from config with unsupported connection mode."""
        mock_config = Mock(spec=ConfigurationModel)
        mock_source_conn = Mock()
        mock_source_conn.mode = "unsupported_mode"
        mock_config.source_connection = mock_source_conn

        with pytest.raises(typer.BadParameter) as exc_info:
            self.args_manager._setup_source_from_config(mock_config)

        assert "Unsupported source connection mode for Snowflake" in str(exc_info.value)
