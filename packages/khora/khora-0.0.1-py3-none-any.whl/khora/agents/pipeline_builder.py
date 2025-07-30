"""Pipeline builder agent for creating Dagster pipelines dynamically."""

import json
from typing import Any, Dict

from dagster import AssetExecutionContext, asset, define_asset_job
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from khora.agents.data_fetcher import DataFetcherAgent
from khora.utils.data_models import DataRequest, PipelineConfig


class PipelineBuilderAgent:
    """Agent for building Dagster pipelines based on natural language descriptions."""

    def __init__(self, openai_api_key: str, model: str = "gpt-4-turbo-preview"):
        """Initialize the pipeline builder agent."""
        self.llm = ChatOpenAI(
            api_key=SecretStr(openai_api_key), model=model, temperature=0
        )
        self.data_fetcher = DataFetcherAgent(openai_api_key, model)

    def analyze_pipeline_request(self, description: str) -> PipelineConfig:
        """
        Analyze a natural language pipeline description and create PipelineConfig.

        Args:
            description: Natural language description of the pipeline

        Returns:
            PipelineConfig with structured pipeline definition
        """
        system_prompt = """
        You are a pipeline configuration assistant. Analyze the user's description
        and create a structured pipeline configuration.

        Identify:
        1. Data sources to fetch from (API, web scraping, Google Docs/Sheets)
        2. The sequence of operations
        3. Any transformations or processing needed
        4. Output format requirements

        Respond with a JSON object that matches the PipelineConfig schema:
        {
            "name": "pipeline_name",
            "description": "pipeline description",
            "requests": [
                {
                    "source_type": "api|web_scraper|google_docs|spreadsheet",
                    "prompt": "what data to fetch",
                    "source_config": {},
                    "filters": {},
                    "metadata": {}
                }
            ],
            "parallel_execution": true/false,
            "output_format": "json"
        }
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=description),
        ]

        response = self.llm.invoke(messages)

        try:
            content = (
                response.content
                if isinstance(response.content, str)
                else str(response.content)
            )
            config_dict = json.loads(content)
            # Convert to PipelineConfig
            config_dict["requests"] = [
                DataRequest(**req) for req in config_dict.get("requests", [])
            ]
            return PipelineConfig(**config_dict)
        except (json.JSONDecodeError, ValueError):
            # Fallback to a simple configuration
            return PipelineConfig(
                name="custom_pipeline",
                description=description,
                requests=[],
                parallel_execution=True,
            )

    def build_pipeline(self, config: PipelineConfig) -> Dict[str, Any]:
        """
        Build a Dagster pipeline from configuration.

        Args:
            config: Pipeline configuration

        Returns:
            Dictionary containing Dagster assets and jobs
        """
        assets = []

        # Create assets for each data request
        for i, request in enumerate(config.requests):
            asset_name = f"{config.name}_{request.source_type}_{i}"

            @asset(
                name=asset_name,
                description=f"Fetch data: {request.prompt}",
                metadata={"source_type": request.source_type, "prompt": request.prompt},
            )
            async def fetch_data_asset(
                context: AssetExecutionContext,
                req: DataRequest = request,
                fetcher: DataFetcherAgent = self.data_fetcher,
            ) -> Dict[str, Any]:
                """Asset for fetching data based on request."""
                context.log.info(f"Fetching data from {req.source_type}")
                response = await fetcher.fetch_data(req)

                if response.status == "error":
                    context.log.error(f"Error fetching data: {response.error_message}")
                    raise Exception(response.error_message)

                return response.data or {}

            assets.append(fetch_data_asset)

        # Create a job that runs all assets
        job = define_asset_job(
            name=f"{config.name}_job",
            selection=[asset.key for asset in assets],
            description=config.description or f"Job for {config.name}",
        )

        return {"assets": assets, "jobs": [job], "config": config}

    def generate_pipeline_code(self, config: PipelineConfig) -> str:
        """
        Generate Python code for a Dagster pipeline.

        Args:
            config: Pipeline configuration

        Returns:
            Python code as string
        """
        code_template = '''
"""Auto-generated Dagster pipeline: {name}"""

from dagster import AssetExecutionContext, asset, define_asset_job, Definitions
from khora.agents import DataFetcherAgent
from khora.utils.data_models import DataRequest, DataSourceType
from khora.utils.config import load_config

# Load configuration
config = load_config()
data_fetcher = DataFetcherAgent(
    openai_api_key=config["openai_api_key"],
    model=config["openai_model"]
)

# Define assets
'''

        code = code_template.format(name=config.name)

        # Generate asset code for each request
        for i, request in enumerate(config.requests):
            asset_code = f'''
@asset(
    name="{config.name}_{request.source_type}_{i}",
    description="Fetch: {request.prompt}"
)
async def fetch_{request.source_type}_{i}(context: AssetExecutionContext):
    """Fetch data from {request.source_type}."""
    request = DataRequest(
        source_type=DataSourceType.{request.source_type.upper()},
        prompt="{request.prompt}",
        source_config={json.dumps(request.source_config)},
        filters={json.dumps(request.filters)},
                 metadata={json.dumps(request.metadata)}
     )

     response = await data_fetcher.fetch_data(request)

     if response.status == "error":
         raise Exception(f"Failed to fetch data: {{response.error_message}}")

     return response.data

'''
            code += asset_code

        # Generate job definition
        asset_names = [
            f"fetch_{req.source_type}_{i}" for i, req in enumerate(config.requests)
        ]

        job_code = f"""
# Define job
{config.name}_job = define_asset_job(
    name="{config.name}_job",
    selection={asset_names},
    description="{config.description or "Auto-generated job"}"
)

# Define Dagster definitions
defs = Definitions(
    assets={asset_names},
    jobs=[{config.name}_job]
)
"""

        code += job_code

        return code
