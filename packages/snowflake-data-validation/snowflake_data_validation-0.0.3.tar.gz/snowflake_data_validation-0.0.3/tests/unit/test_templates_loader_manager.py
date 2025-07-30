from pathlib import Path

from deepdiff import DeepDiff
import pandas as pd


from snowflake.snowflake_data_validation.utils.constants import Platform
from snowflake.snowflake_data_validation.utils.model.templates_loader_manager import (
    TemplatesLoaderManager,
)

ASSETS_DIRECTORY_NAME = "assets"
TEST_TEMPLATES_LOADER_MANAGER_DIRECTORY_NAME = "test_templates_loader_manager"


def test_template_loader_manager_generation():

    templates_directory_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_TEMPLATES_LOADER_MANAGER_DIRECTORY_NAME)
    )
    platform = Platform.SNOWFLAKE

    templates_loader_manager = TemplatesLoaderManager(
        templates_directory_path=templates_directory_path, platform=platform
    )

    assert templates_loader_manager is not None
    assert templates_loader_manager.templates_directory_path == templates_directory_path
    assert templates_loader_manager.platform == platform

    expected_datatypes_normalization_templates = {
        "TYPE1": r"""TO_CHAR("{{ col_name }}")""",
        "TYPE2": r"""TO_CHAR("{{ col_name }}", 'YYYY-MM-DD')""",
        "TYPE3": r"""TO_CHAR("{{ col_name }}", '{{ column_numeric_format }}')""",
        "TYPE4": r"""TO_CHAR("{{ col_name }}")""",
    }

    datatypes_normalization_templates_diff = DeepDiff(
        expected_datatypes_normalization_templates,
        templates_loader_manager.datatypes_normalization_templates,
        ignore_order=True,
    )

    assert datatypes_normalization_templates_diff == {}

    expected_metrics_templates = pd.DataFrame(
        {
            "type": ["TYPE1", "TYPE1", "TYPE2", "TYPE2"],
            "metric": ["METRIC1", "METRIC2", "METRIC1", "METRIC2"],
            "template": [
                'COUNT_IF("{{ col_name }}" = TRUE)',
                'COUNT_IF("{{ col_name }}" = FALSE)',
                'COUNT_IF("{{ col_name }}" = TRUE)',
                'COUNT_IF("{{ col_name }}" = FALSE)',
            ],
            "normalization": [
                "TO_CHAR({{ metric_query }}, 'FM9999999999999999999999999999.0000')",
                "TO_CHAR({{ metric_query }}, 'FM9999999999999999999999999999.0000')",
                "TO_CHAR({{ metric_query }}, '{{ column_numeric_format }}')",
                "TO_CHAR({{ metric_query }}, '{{ column_numeric_format }}')",
            ],
        }
    )

    assert expected_metrics_templates.equals(templates_loader_manager.metrics_templates)
