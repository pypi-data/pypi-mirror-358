"""Unit tests for tools."""

from unittest.mock import AsyncMock, Mock, patch

from khora.tools import APITool, GoogleDocsTool, WebScraperTool


class TestAPITool:
    """Tests for APITool."""

    @patch("khora.tools.api_tool.httpx.Client")
    def test_api_tool_success(self, mock_client):
        """Test successful API request."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_response.headers = {"content-type": "application/json"}

        mock_client_instance = Mock()
        mock_client_instance.request.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance

        # Test tool
        tool = APITool()
        result = tool._run(
            url="https://api.example.com/data",
            method="GET",
            headers={"Authorization": "Bearer token"},
        )

        assert result["status"] == "success"
        assert result["status_code"] == 200
        assert result["data"]["result"] == "success"

    @patch("khora.tools.api_tool.httpx.Client")
    def test_api_tool_error(self, mock_client):
        """Test API request with error."""
        # Mock error response
        mock_client_instance = Mock()
        mock_client_instance.request.side_effect = Exception("Connection error")
        mock_client.return_value.__enter__.return_value = mock_client_instance

        # Test tool
        tool = APITool()
        result = tool._run(url="https://api.example.com/data")

        assert result["status"] == "error"
        assert "Connection error" in result["error"]


class TestWebScraperTool:
    """Tests for WebScraperTool."""

    @patch("khora.tools.web_scraper_tool.async_playwright")
    def test_web_scraper_success(self, mock_playwright):
        """Test successful web scraping."""
        # Create proper async mocks
        mock_page = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()

        # Setup page mock
        mock_page.goto = AsyncMock()
        mock_page.title = AsyncMock(return_value="Test Page")
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.url = "https://example.com"

        # Mock selector results
        mock_element = Mock()
        mock_element.text_content = AsyncMock(return_value="Test content")
        mock_page.query_selector_all = AsyncMock(return_value=[mock_element])

        # Mock other page methods
        mock_page.inner_text = AsyncMock(return_value="Full page text")
        mock_page.evaluate = AsyncMock(
            side_effect=lambda script: (
                [{"text": "Link 1", "href": "/link1", "title": None}]
                if "links" in script
                else [[{"Name": "Item1", "Value": "10"}]] if "table" in script else None
            )
        )

        # Setup browser context mock
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()

        # Setup chromium mock
        mock_chromium = Mock()
        mock_chromium.launch = AsyncMock(return_value=mock_browser)

        # Setup playwright async context manager
        mock_playwright_instance = AsyncMock()
        mock_playwright_instance.chromium = mock_chromium
        mock_playwright_instance.__aenter__ = AsyncMock(
            return_value=mock_playwright_instance
        )
        mock_playwright_instance.__aexit__ = AsyncMock(return_value=None)

        mock_playwright.return_value = mock_playwright_instance

        # Test tool
        tool = WebScraperTool()
        result = tool._run(
            url="https://example.com",
            selectors={"content": "p.content"},
            extract_links=True,
            extract_tables=True,
        )

        # Debug output
        if result["status"] != "success":
            print(f"Error result: {result}")

        assert result["status"] == "success"
        assert result["data"]["title"] == "Test Page"
        assert result["data"]["url"] == "https://example.com"


class TestGoogleDocsTool:
    """Tests for GoogleDocsTool."""

    @patch("khora.tools.google_docs_tool.build")
    @patch(
        "khora.tools.google_docs_tool.service_account.Credentials.from_service_account_file"
    )
    def test_google_sheets_success(self, mock_creds, mock_build):
        """Test successful Google Sheets data extraction."""
        # Mock Google Sheets API
        mock_service = Mock()
        mock_spreadsheets = Mock()
        mock_values = Mock()

        # Mock sheet metadata
        mock_spreadsheets.get.return_value.execute.return_value = {
            "properties": {"title": "Test Sheet"},
            "sheets": [{"properties": {"title": "Sheet1"}}],
        }

        # Mock sheet values
        mock_values.get.return_value.execute.return_value = {
            "values": [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]
        }

        mock_spreadsheets.values.return_value = mock_values
        mock_service.spreadsheets.return_value = mock_spreadsheets
        mock_build.return_value = mock_service

        # Test tool
        tool = GoogleDocsTool(credentials_path="/path/to/creds.json")
        result = tool._run(
            document_id="test_sheet_id", document_type="sheet", sheet_range="Sheet1!A:B"
        )

        assert result["status"] == "success"
        assert result["data"]["title"] == "Test Sheet"
        assert len(result["data"]["data"]["requested_range"]) == 2
        assert result["data"]["data"]["requested_range"][0]["Name"] == "Alice"
