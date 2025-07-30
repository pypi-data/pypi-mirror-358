"""Google Docs and Sheets tool for extracting data."""

from typing import Any, Dict, List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from langchain.tools import BaseTool
from pydantic import Field


class GoogleDocsTool(BaseTool):
    """Tool for extracting data from Google Docs and Sheets."""

    name: str = "google_docs_fetcher"
    description: str = (
        "Extract data from Google Docs and Google Sheets. "
        "Requires document/sheet ID and appropriate permissions."
    )

    credentials_path: Optional[str] = Field(
        default=None, description="Path to Google service account credentials JSON"
    )
    scopes: List[str] = Field(
        default_factory=lambda: [
            "https://www.googleapis.com/auth/documents.readonly",
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ]
    )

    def _run(
        self,
        document_id: str,
        document_type: str = "sheet",
        sheet_range: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Extract data from Google Docs or Sheets.

        Args:
            document_id: Google document or sheet ID
            document_type: Type of document ("doc" or "sheet")
            sheet_range: For sheets, the A1 notation range (e.g., "Sheet1!A1:D10")

        Returns:
            Extracted data as dictionary
        """
        try:
            # Initialize credentials
            if self.credentials_path:
                credentials = service_account.Credentials.from_service_account_file(  # type: ignore
                    self.credentials_path, scopes=self.scopes
                )
            else:
                # Use default credentials if available
                credentials = None

            if document_type.lower() == "sheet":
                return self._extract_sheet_data(document_id, sheet_range, credentials)
            elif document_type.lower() == "doc":
                return self._extract_doc_data(document_id, credentials)
            else:
                return {
                    "status": "error",
                    "error": f"Unsupported document type: {document_type}",
                }

        except Exception as e:
            return {"status": "error", "error": str(e), "error_type": type(e).__name__}

    def _extract_sheet_data(
        self, sheet_id: str, sheet_range: Optional[str], credentials: Any
    ) -> Dict[str, Any]:
        """Extract data from Google Sheets."""
        service = build("sheets", "v4", credentials=credentials)

        # Get sheet metadata
        sheet_metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()

        sheets = sheet_metadata.get("sheets", [])

        result = {
            "title": sheet_metadata.get("properties", {}).get("title"),
            "sheets": [s["properties"]["title"] for s in sheets],
            "data": {},
        }

        # If no range specified, get all sheets
        if not sheet_range:
            for sheet in sheets:
                sheet_name = sheet["properties"]["title"]
                range_name = f"{sheet_name}!A:Z"
                try:
                    sheet_data = (
                        service.spreadsheets()
                        .values()
                        .get(spreadsheetId=sheet_id, range=range_name)
                        .execute()
                    )

                    values = sheet_data.get("values", [])
                    if values:
                        # Convert to list of dicts using first row as headers
                        headers = values[0] if values else []
                        rows = []
                        for row in values[1:]:
                            row_dict = {}
                            for i, header in enumerate(headers):
                                row_dict[header] = row[i] if i < len(row) else ""
                            rows.append(row_dict)
                        result["data"][sheet_name] = rows
                except Exception:
                    result["data"][sheet_name] = []
        else:
            # Get specific range
            sheet_data = (
                service.spreadsheets()
                .values()
                .get(spreadsheetId=sheet_id, range=sheet_range)
                .execute()
            )

            values = sheet_data.get("values", [])
            if values:
                headers = values[0] if values else []
                rows = []
                for row in values[1:]:
                    row_dict = {}
                    for i, header in enumerate(headers):
                        row_dict[header] = row[i] if i < len(row) else ""
                    rows.append(row_dict)
                result["data"]["requested_range"] = rows

        return {"status": "success", "data": result}

    def _extract_doc_data(self, doc_id: str, credentials: Any) -> Dict[str, Any]:
        """Extract data from Google Docs."""
        service = build("docs", "v1", credentials=credentials)

        # Get document
        document = service.documents().get(documentId=doc_id).execute()

        title = document.get("title")
        content = []

        # Extract text content
        for element in document.get("body", {}).get("content", []):
            if "paragraph" in element:
                paragraph = element["paragraph"]
                text_elements = []
                for elem in paragraph.get("elements", []):
                    if "textRun" in elem:
                        text_elements.append(elem["textRun"]["content"])
                if text_elements:
                    content.append("".join(text_elements))

        return {
            "status": "success",
            "data": {
                "title": title,
                "content": "\n".join(content),
                "document_id": doc_id,
            },
        }

    async def _arun(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Async version of the Google Docs tool."""
        raise NotImplementedError("Async execution not implemented yet")
