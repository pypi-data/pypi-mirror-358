"""Unit tests for data models."""

from datetime import datetime

from khora.utils.data_models import (
    DataRequest,
    DataResponse,
    DataSourceType,
    PipelineConfig,
)


def test_data_request_creation():
    """Test DataRequest model creation."""
    request = DataRequest(
        source_type=DataSourceType.API,
        prompt="Fetch weather data",
        source_config={"url": "https://api.weather.com"},
        filters={"city": "SF"},
        metadata={"user": "test"},
    )

    assert request.source_type == "api"
    assert request.prompt == "Fetch weather data"
    assert request.source_config["url"] == "https://api.weather.com"
    assert request.filters["city"] == "SF"
    assert request.metadata["user"] == "test"


def test_data_response_creation():
    """Test DataResponse model creation."""
    response = DataResponse(
        request_id="test_123",
        status="success",
        data={"temperature": 20},
        source_type=DataSourceType.API,
    )

    assert response.request_id == "test_123"
    assert response.status == "success"
    assert response.data["temperature"] == 20
    assert response.source_type == "api"
    assert response.error_message is None
    assert isinstance(response.timestamp, datetime)


def test_data_response_with_error():
    """Test DataResponse with error."""
    response = DataResponse(
        request_id="test_456",
        status="error",
        error_message="Connection failed",
        source_type=DataSourceType.WEB_SCRAPER,
    )

    assert response.status == "error"
    assert response.error_message == "Connection failed"
    assert response.data is None


def test_pipeline_config_creation():
    """Test PipelineConfig model creation."""
    requests = [
        DataRequest(source_type=DataSourceType.API, prompt="Fetch data from API"),
        DataRequest(source_type=DataSourceType.WEB_SCRAPER, prompt="Scrape website"),
    ]

    config = PipelineConfig(
        name="test_pipeline",
        description="Test pipeline",
        requests=requests,
        parallel_execution=True,
        output_format="json",
    )

    assert config.name == "test_pipeline"
    assert config.description == "Test pipeline"
    assert len(config.requests) == 2
    assert config.parallel_execution is True
    assert config.output_format == "json"
    assert config.retry_config["max_retries"] == 3


def test_data_source_type_enum():
    """Test DataSourceType enum values."""
    assert DataSourceType.API.value == "api"
    assert DataSourceType.WEB_SCRAPER.value == "web_scraper"
    assert DataSourceType.GOOGLE_DOCS.value == "google_docs"
    assert DataSourceType.SPREADSHEET.value == "spreadsheet"
