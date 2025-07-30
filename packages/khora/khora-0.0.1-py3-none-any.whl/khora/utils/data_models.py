"""Data models for Khora pipeline operations."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DataSourceType(str, Enum):
    """Supported data source types."""

    API = "api"
    WEB_SCRAPER = "web_scraper"
    GOOGLE_DOCS = "google_docs"
    SPREADSHEET = "spreadsheet"


class DataRequest(BaseModel):
    """Model for data fetching requests."""

    source_type: DataSourceType
    prompt: str = Field(..., description="AI prompt describing what data to fetch")
    source_config: Dict[str, Any] = Field(
        default_factory=dict, description="Configuration specific to the data source"
    )
    filters: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(use_enum_values=True)


class DataResponse(BaseModel):
    """Model for data fetching responses."""

    request_id: str
    status: str = Field(..., description="success, error, or partial")
    data: Optional[Any] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_type: DataSourceType

    model_config = ConfigDict(use_enum_values=True)


class PipelineConfig(BaseModel):
    """Configuration for pipeline execution."""

    name: str
    description: Optional[str] = None
    requests: List[DataRequest]
    parallel_execution: bool = True
    retry_config: Dict[str, Any] = Field(
        default_factory=lambda: {"max_retries": 3, "retry_delay": 5}
    )
    output_format: str = "json"
