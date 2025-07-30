"""Example data pipeline implementation."""

from typing import Any, Dict, List

from dagster import (
    AssetExecutionContext,
    AssetsDefinition,
    Config,
    asset,
    define_asset_job,
)

from khora.agents import DataFetcherAgent
from khora.utils.config import load_config
from khora.utils.data_models import DataRequest, DataSourceType


class PipelineConfig(Config):
    """Configuration for pipeline execution."""

    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"


def create_data_pipeline(
    name: str, requests: List[DataRequest], config: Dict[str, Any]
) -> List[AssetsDefinition]:
    """
    Create a Dagster pipeline dynamically.

    Args:
        name: Pipeline name
        requests: List of data requests
        config: Configuration dictionary

    Returns:
        List of Dagster assets
    """
    assets = []
    data_fetcher = DataFetcherAgent(
        openai_api_key=config.get("openai_api_key", ""),
        model=config.get("openai_model", "gpt-4-turbo-preview"),
    )

    for i, request in enumerate(requests):
        asset_name = f"{name}_{request.source_type}_{i}"

        @asset(
            name=asset_name,
            description=f"Fetch: {request.prompt}",
            metadata={"source_type": request.source_type, "prompt": request.prompt},
        )
        async def fetch_data(
            context: AssetExecutionContext,
            req: DataRequest = request,
            fetcher: DataFetcherAgent = data_fetcher,
        ) -> Dict[str, Any]:
            """Fetch data based on request."""
            context.log.info(f"Fetching data from {req.source_type}")
            response = await fetcher.fetch_data(req)

            if response.status == "error":
                context.log.error(f"Error: {response.error_message}")
                raise Exception(response.error_message)

            return response.data or {}

        assets.append(fetch_data)

    return assets


def create_example_assets() -> List[AssetsDefinition]:
    """Create example assets for demonstration."""

    @asset(name="example_api_data", description="Example API data fetching")
    async def example_api_data(context: AssetExecutionContext) -> Dict[str, Any]:
        """Fetch example data from an API."""
        context.log.info("Fetching example API data")

        # Example implementation
        config = load_config()
        fetcher = DataFetcherAgent(
            openai_api_key=config.get("openai_api_key", ""),
            model=config.get("openai_model", "gpt-4-turbo-preview"),
        )

        request = DataRequest(
            source_type=DataSourceType.API,
            prompt="Fetch weather data for San Francisco",
            source_config={
                "url": "https://api.weather.com/v1/weather",
                "params": {"city": "San Francisco"},
            },
        )

        response = await fetcher.fetch_data(request)
        return (response.data or {}) if response.status == "success" else {}

    @asset(name="example_web_data", description="Example web scraping")
    async def example_web_data(context: AssetExecutionContext) -> Dict[str, Any]:
        """Scrape example data from a website."""
        context.log.info("Scraping example web data")

        config = load_config()
        fetcher = DataFetcherAgent(
            openai_api_key=config.get("openai_api_key", ""),
            model=config.get("openai_model", "gpt-4-turbo-preview"),
        )

        request = DataRequest(
            source_type=DataSourceType.WEB_SCRAPER,
            prompt="Extract article titles from a news website",
            source_config={
                "url": "https://example.com/news",
                "selectors": {"titles": "h2.article-title"},
            },
        )

        response = await fetcher.fetch_data(request)
        return (response.data or {}) if response.status == "success" else {}

    return [example_api_data, example_web_data]


# Define example job
example_job = define_asset_job(
    name="example_data_pipeline",
    selection=["example_api_data", "example_web_data"],
    description="Example pipeline for fetching data from multiple sources",
)
