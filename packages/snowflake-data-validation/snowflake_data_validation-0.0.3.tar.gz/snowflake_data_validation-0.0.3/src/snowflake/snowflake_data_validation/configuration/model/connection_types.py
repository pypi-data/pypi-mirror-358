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

"""Connection type definitions for YAML configuration.

This file imports connection models from the connections module and creates
the union types used by the main configuration model for both source and
target connections.
"""

from typing import Union

# Import connection models from the dedicated connections module
from snowflake.snowflake_data_validation.configuration.model.connections import (
    SnowflakeDefaultConnection,
    SnowflakeNamedConnection,
    SqlServerCredentialsConnection,
)


# Union type for YAML configuration
# Note: This is used for both source_connection and target_connection fields
# SnowflakeCredentialsConnection is not included as it's only used for IPC commands
Connection = Union[
    # Snowflake connections for YAML (name and default modes only)
    SnowflakeNamedConnection,
    SnowflakeDefaultConnection,
    # SQL Server connections
    SqlServerCredentialsConnection,
]
