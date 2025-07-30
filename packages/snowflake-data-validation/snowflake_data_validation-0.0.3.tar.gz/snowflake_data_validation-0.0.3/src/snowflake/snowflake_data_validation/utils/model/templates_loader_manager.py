from pathlib import Path

import pandas as pd

from snowflake.snowflake_data_validation.utils.constants import (
    COLUMN_DATATYPES_NORMALIZATION_TEMPLATES_NAME_FORMAT,
    COLUMN_METRICS_TEMPLATE_NAME_FORMAT,
    Platform,
)
from snowflake.snowflake_data_validation.utils.helpers import (
    load_datatypes_normalization_templates_from_yaml,
    load_metrics_templates_from_yaml,
)


class TemplatesLoaderManager:

    """A class to manage the loading of templates from a specified directory."""

    def __init__(self, templates_directory_path: Path, platform: Platform):
        """Initialize the TemplatesLoaderManager with the directory path and platform.

        Args:
            templates_directory_path (Path): The path to the directory containing the templates.
            platform (Platform): The platform for which the templates are being loaded.

        """
        self.templates_directory_path: Path = templates_directory_path
        self.platform: Platform = platform
        self.datatypes_normalization_templates: dict[
            str, str
        ] = self._load_datatypes_normalization_templates()
        self.metrics_templates: pd.DataFrame = self._load_metrics_templates()

    def _load_datatypes_normalization_templates(self) -> dict[str, str]:
        """Load the datatypes normalization templates from the specified directory.

        Returns:
            dict[str, str]: A dictionary containing the datatypes normalization templates.

        """
        normalization_templates_file_name = (
            COLUMN_DATATYPES_NORMALIZATION_TEMPLATES_NAME_FORMAT.format(
                platform=self.platform.value
            )
        )

        normalization_templates_file_path = self.templates_directory_path.joinpath(
            normalization_templates_file_name
        )

        data_dict = load_datatypes_normalization_templates_from_yaml(
            yaml_path=normalization_templates_file_path
        )

        return data_dict

    def _load_metrics_templates(self) -> pd.DataFrame:
        """Load the metrics templates from the specified directory.

        Returns:
            pd.DataFrame: A DataFrame containing the metrics templates.

        """
        normalization_template_file_name = COLUMN_METRICS_TEMPLATE_NAME_FORMAT.format(
            platform=self.platform.value
        )

        normalization_template_file_path = self.templates_directory_path.joinpath(
            normalization_template_file_name
        )

        df = load_metrics_templates_from_yaml(
            yaml_path=normalization_template_file_path,
            datatypes_normalization_templates=self.datatypes_normalization_templates,
        )

        return df
