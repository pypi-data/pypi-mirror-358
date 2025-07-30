"""Example pipeline using Khora."""

import asyncio

from khora.agents import DataFetcherAgent, PipelineBuilderAgent
from khora.utils.config import load_config
from khora.utils.data_models import DataRequest, DataSourceType, PipelineConfig


async def example_single_fetch():
    """Example of fetching data from a single source."""
    config = load_config()

    # Initialize data fetcher
    fetcher = DataFetcherAgent(
        openai_api_key=config.get("openai_api_key", ""),
        model=config.get("openai_model", "gpt-4-turbo-preview"),
    )

    # Create a request to fetch weather data
    request = DataRequest(
        source_type=DataSourceType.API,
        prompt="Fetch current weather data for San Francisco from OpenWeatherMap API",
        source_config={
            "url": "https://api.openweathermap.org/data/2.5/weather",
            "params": {"q": "San Francisco", "appid": "your_api_key"},
        },
    )

    # Fetch the data
    response = await fetcher.fetch_data(request)

    if response.status == "success":
        print("Weather data fetched successfully!")
        print(response.data)
    else:
        print(f"Error: {response.error_message}")


async def example_pipeline_builder():
    """Example of building a pipeline from natural language."""
    config = load_config()

    # Initialize pipeline builder
    builder = PipelineBuilderAgent(
        openai_api_key=config.get("openai_api_key", ""),
        model=config.get("openai_model", "gpt-4-turbo-preview"),
    )

    # Describe the pipeline in natural language
    pipeline_description = """
    Create a data pipeline that:
    1. Fetches cryptocurrency prices from CoinGecko API for Bitcoin, Ethereum, and Solana
    2. Scrapes the latest crypto news headlines from CoinDesk website
    3. Reads market analysis data from a Google Sheet with ID 'abc123'

    The pipeline should run these tasks in parallel and combine the results.
    """

    # Analyze and build the pipeline
    pipeline_config = builder.analyze_pipeline_request(pipeline_description)

    print(f"Generated Pipeline: {pipeline_config.name}")
    print(f"Description: {pipeline_config.description}")
    print(f"Number of data sources: {len(pipeline_config.requests)}")

    # Generate pipeline code
    code = builder.generate_pipeline_code(pipeline_config)
    print("\nGenerated Pipeline Code:")
    print("=" * 50)
    print(code[:500] + "...")  # Show first 500 chars

    # Build the actual Dagster pipeline
    pipeline_def = builder.build_pipeline(pipeline_config)
    print(f"\nCreated {len(pipeline_def['assets'])} Dagster assets")
    print(f"Created {len(pipeline_def['jobs'])} Dagster jobs")


def example_manual_pipeline():
    """Example of manually creating a pipeline configuration."""
    # Create requests manually
    requests = [
        DataRequest(
            source_type=DataSourceType.API,
            prompt="Fetch Bitcoin price from CoinGecko",
            source_config={
                "url": "https://api.coingecko.com/api/v3/simple/price",
                "params": {"ids": "bitcoin", "vs_currencies": "usd"},
            },
        ),
        DataRequest(
            source_type=DataSourceType.WEB_SCRAPER,
            prompt="Extract top news headlines from crypto news site",
            source_config={
                "url": "https://www.coindesk.com",
                "wait_for": "networkidle",
                "selectors": {"headlines": "h3.headline"},
                "extract_links": True,
                "screenshot": True,
            },
        ),
        DataRequest(
            source_type=DataSourceType.SPREADSHEET,
            prompt="Read trading signals from Google Sheet",
            source_config={
                "document_id": "your-sheet-id-here",
                "sheet_range": "Sheet1!A:E",
            },
        ),
    ]

    # Create pipeline configuration
    pipeline_config = PipelineConfig(
        name="crypto_analysis_pipeline",
        description="Pipeline for cryptocurrency market analysis",
        requests=requests,
        parallel_execution=True,
        output_format="json",
    )

    print("Manual Pipeline Configuration:")
    print(f"Name: {pipeline_config.name}")
    print(f"Requests: {len(pipeline_config.requests)}")
    for i, req in enumerate(pipeline_config.requests):
        print(f"  {i+1}. {req.source_type}: {req.prompt}")


if __name__ == "__main__":
    print("Khora Example Pipelines")
    print("=" * 50)

    # Run examples
    print("\n1. Single Data Fetch Example:")
    asyncio.run(example_single_fetch())

    print("\n2. Pipeline Builder Example:")
    asyncio.run(example_pipeline_builder())

    print("\n3. Manual Pipeline Configuration Example:")
    example_manual_pipeline()
