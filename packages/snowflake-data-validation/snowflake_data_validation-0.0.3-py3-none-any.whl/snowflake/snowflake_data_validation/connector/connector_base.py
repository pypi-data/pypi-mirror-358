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


from abc import ABC, abstractmethod
from typing import Optional

from snowflake.snowflake_data_validation.utils.constants import (
    DEFAULT_CONNECTION_MODE,
)


class ConnectorBase(ABC):

    """Abstract base class for database connectors."""

    def __init__(self, output_path: Optional[str] = None):
        self.connection: Optional[object] = None
        self.output_path = output_path

    @abstractmethod
    def connect(
        self, mode: str = DEFAULT_CONNECTION_MODE, connection_name: str = ""
    ) -> None:
        """Establish a connection to the database."""
        pass

    @abstractmethod
    def execute_query(self, query: str) -> list[tuple]:
        """Execute a query on the database."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the connection to the database."""
        pass


class NullConnector(ConnectorBase):

    """A connector that does nothing. Used as a null object for async validation scenarios."""

    def connect(
        self, mode: str = DEFAULT_CONNECTION_MODE, connection_name: str = ""
    ) -> None:
        pass

    def execute_query(self, query: str) -> list[tuple]:
        return []

    def close(self) -> None:
        pass
