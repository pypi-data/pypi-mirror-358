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

from snowflake.snowflake_data_validation.configuration.model.configuration_model import (
    ConfigurationModel,
)
from snowflake.snowflake_data_validation.extractor.sql_queries_template_generator import (
    SQLQueriesTemplateGenerator,
)
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
)
from snowflake.snowflake_data_validation.utils.constants import Platform
from snowflake.snowflake_data_validation.utils.model.templates_loader_manager import (
    TemplatesLoaderManager,
)


class Context:

    """Context class encapsulates the runtime environment and configuration for data validation processes.

    Attributes:
        configuration (ConfigurationModel): The configuration model containing validation settings.
        report_path (str): Path to the directory where reports and logs will be stored.
        templates_path (str): Path to the directory containing SQL templates.
        source_platform (Platform): The source data platform enum.
        target_platform (Platform): The target data platform enum.
        sql_generator (SQLQueriesTemplateGenerator): Utility for generating SQL queries from templates.
        output_handler (OutputHandlerBase): Custom handler for outputting validation results.
        datatypes_mappings (Optional[dict[str, str]]): Optional mapping of source to target data types.
        run_id (str): Unique identifier for the current validation run.
        run_start_time (str): Timestamp marking the start of the validation run.
        source_templates (TemplatesLoaderManager): Manager for loading source platform templates.
        target_templates (TemplatesLoaderManager): Manager for loading target platform templates.

    """

    def __init__(
        self,
        configuration: ConfigurationModel,
        report_path: str,
        templates_dir_path: str,
        source_platform: Platform,
        target_platform: Platform,
        custom_output_handler: OutputHandlerBase,
        run_id: str,
        run_start_time: str,
        source_templates: TemplatesLoaderManager,
        target_templates: TemplatesLoaderManager,
        datatypes_mappings: Optional[dict[str, str]] = None,
    ):
        self.configuration = configuration
        self.report_path = report_path
        self.templates_path = templates_dir_path
        self.source_platform = source_platform
        self.target_platform = target_platform
        self.sql_generator = SQLQueriesTemplateGenerator(templates_dir_path)
        self.output_handler = custom_output_handler
        self.datatypes_mappings = datatypes_mappings
        self.run_id = run_id
        self.run_start_time = run_start_time
        self.source_templates = source_templates
        self.target_templates = target_templates
