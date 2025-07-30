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

from typing import Optional

from pydantic import BaseModel, model_validator


class ValidationConfiguration(BaseModel):

    """Class representing the validation levels to be applied to a table."""

    schema_validation: Optional[bool] = False
    metrics_validation: Optional[bool] = False
    columnar_validation: Optional[bool] = False
    row_validation: Optional[bool] = False

    @model_validator(mode="after")
    def validate_configuration(self) -> "ValidationConfiguration":
        """Validate the configuration after initialization.

        This method checks if at least one validation type is enabled.

        Raises:
            ValueError: If no validation type is enabled.

        """
        if not self.model_dump(exclude_none=True):
            raise ValueError(
                "At least one validation type must be enabled in case of adding the property."
            )
        return self
