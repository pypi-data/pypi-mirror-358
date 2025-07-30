"""Dagster definitions for Khora pipelines."""

from dagster import Definitions

from khora.pipelines.data_pipeline import create_example_assets, example_job
from khora.utils.config import load_config

# Load configuration
config = load_config()

# Create definitions
defs = Definitions(
    assets=create_example_assets(), jobs=[example_job], resources={"config": config}
)
