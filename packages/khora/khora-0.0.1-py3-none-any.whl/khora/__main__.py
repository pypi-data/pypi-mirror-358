"""Main entry point for Khora CLI."""

import asyncio
import json
import sys
from pathlib import Path

from khora.agents import DataFetcherAgent, PipelineBuilderAgent
from khora.utils.config import load_config
from khora.utils.data_models import DataRequest, DataSourceType


async def main() -> None:
    """Main CLI function."""
    config = load_config()

    if not config.get("openai_api_key"):
        print("Error: OPENAI_API_KEY not set in environment")
        sys.exit(1)

    print("Khora - AI-powered Data Pipeline Builder")
    print("=" * 40)

    # Example: Create a simple data fetching request
    if len(sys.argv) > 1:
        if sys.argv[1] == "fetch":
            if len(sys.argv) < 4:
                print("Usage: python -m khora fetch <source_type> <prompt>")
                sys.exit(1)

            source_type = sys.argv[2]
            prompt = " ".join(sys.argv[3:])

            fetcher = DataFetcherAgent(
                openai_api_key=config["openai_api_key"],
                model=config.get("openai_model", "gpt-4-turbo-preview"),
            )

            try:
                request = DataRequest(
                    source_type=DataSourceType(source_type), prompt=prompt
                )

                print(f"Fetching data from {source_type}...")
                response = await fetcher.fetch_data(request)

                if response.status == "success":
                    print("Success! Data fetched:")
                    print(json.dumps(response.data, indent=2))
                else:
                    print(f"Error: {response.error_message}")

            except ValueError:
                print(
                    "Error: Invalid source type. Valid types: api, web_scraper, google_docs, spreadsheet"
                )
                sys.exit(1)

        elif sys.argv[1] == "build":
            if len(sys.argv) < 3:
                print("Usage: python -m khora build <pipeline_description>")
                sys.exit(1)

            description = " ".join(sys.argv[2:])

            builder = PipelineBuilderAgent(
                openai_api_key=config["openai_api_key"],
                model=config.get("openai_model", "gpt-4-turbo-preview"),
            )

            print("Analyzing pipeline request...")
            pipeline_config = builder.analyze_pipeline_request(description)

            print(f"\nGenerated Pipeline: {pipeline_config.name}")
            print(f"Description: {pipeline_config.description}")
            print(f"Number of data sources: {len(pipeline_config.requests)}")

            # Generate code
            code = builder.generate_pipeline_code(pipeline_config)

            # Save to file
            output_file = Path(f"{pipeline_config.name}_pipeline.py")
            output_file.write_text(code)

            print(f"\nPipeline code saved to: {output_file}")
            print("\nTo run the pipeline:")
            print(f"  dagster dev -f {output_file}")

    else:
        print("\nUsage:")
        print("  python -m khora fetch <source_type> <prompt>")
        print("  python -m khora build <pipeline_description>")
        print("\nExamples:")
        print("  python -m khora fetch api 'Get weather data for NYC'")
        print(
            "  python -m khora build 'Create pipeline to fetch crypto prices and news'"
        )


if __name__ == "__main__":
    asyncio.run(main())
