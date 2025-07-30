"""API tool for fetching data from REST APIs."""

import json
from typing import Any, Dict, Optional

import httpx
from langchain.tools import BaseTool
from pydantic import Field


class APITool(BaseTool):
    """Tool for making API requests based on AI-generated specifications."""

    name: str = "api_fetcher"
    description: str = (
        "Fetch data from APIs. The tool accepts a URL, HTTP method, "
        "headers, and optional body/params based on the AI prompt analysis."
    )

    timeout: int = Field(default=30, description="Request timeout in seconds")

    def _run(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Execute API request.

        Args:
            url: API endpoint URL
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            headers: Optional HTTP headers
            params: Optional query parameters
            json_body: Optional JSON body for POST/PUT requests

        Returns:
            Response data as dictionary
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_body,
                )

                response.raise_for_status()

                # Try to parse JSON response
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    data = {"text": response.text}

                return {
                    "status": "success",
                    "status_code": response.status_code,
                    "data": data,
                    "headers": dict(response.headers),
                }

        except httpx.HTTPStatusError as e:
            return {
                "status": "error",
                "status_code": e.response.status_code,
                "error": str(e),
                "response_text": e.response.text,
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "error_type": type(e).__name__}

    async def _arun(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Async version of the API tool."""
        raise NotImplementedError("Async execution not implemented yet")
