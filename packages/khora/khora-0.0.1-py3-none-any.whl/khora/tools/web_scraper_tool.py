"""Web scraper tool for extracting data from websites using Playwright."""

import asyncio
from typing import Any, Dict, Optional

from langchain.tools import BaseTool
from playwright.async_api import async_playwright
from pydantic import Field


class WebScraperTool(BaseTool):
    """Tool for scraping data from websites using Playwright."""

    name: str = "web_scraper"
    description: str = (
        "Extract data from websites using Playwright. Can handle JavaScript-rendered "
        "content, interact with pages, and extract complex data structures."
    )

    timeout: int = Field(default=30000, description="Page timeout in milliseconds")
    headless: bool = Field(default=True, description="Run browser in headless mode")

    def _run(
        self,
        url: str,
        wait_for: Optional[str] = None,
        selectors: Optional[Dict[str, str]] = None,
        extract_all_text: bool = False,
        extract_links: bool = False,
        extract_tables: bool = False,
        screenshot: bool = False,
        execute_script: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Scrape web page and extract data using Playwright.

        Args:
            url: Website URL to scrape
            wait_for: CSS selector or state to wait for before extraction
            selectors: CSS selectors for specific elements
            extract_all_text: Extract all text content
            extract_links: Extract all links
            extract_tables: Extract tables as structured data
            screenshot: Take a screenshot of the page
            execute_script: Custom JavaScript to execute on the page

        Returns:
            Extracted data as dictionary
        """
        # Run async function in sync context
        return asyncio.run(
            self._async_run(
                url=url,
                wait_for=wait_for,
                selectors=selectors,
                extract_all_text=extract_all_text,
                extract_links=extract_links,
                extract_tables=extract_tables,
                screenshot=screenshot,
                execute_script=execute_script,
                **kwargs,
            )
        )

    async def _async_run(
        self,
        url: str,
        wait_for: Optional[str] = None,
        selectors: Optional[Dict[str, str]] = None,
        extract_all_text: bool = False,
        extract_links: bool = False,
        extract_tables: bool = False,
        screenshot: bool = False,
        execute_script: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Async implementation of web scraping."""
        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(headless=self.headless)
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                )
                page = await context.new_page()

                # Navigate to URL
                await page.goto(url, timeout=self.timeout)

                # Wait for specific element or state if specified
                if wait_for:
                    if wait_for in ["load", "domcontentloaded", "networkidle"]:
                        await page.wait_for_load_state(wait_for)  # type: ignore
                    else:
                        await page.wait_for_selector(wait_for, timeout=self.timeout)
                else:
                    # Default: wait for network to be idle
                    await page.wait_for_load_state("networkidle", timeout=self.timeout)

                result: Dict[str, Any] = {"url": page.url, "title": await page.title()}

                # Execute custom JavaScript if provided
                if execute_script:
                    script_result = await page.evaluate(execute_script)
                    result["script_result"] = script_result

                # Extract based on selectors
                if selectors:
                    extracted_data: Dict[str, list[str]] = {}
                    for key, selector in selectors.items():
                        elements = await page.query_selector_all(selector)
                        extracted_data[key] = []
                        for elem in elements:
                            text = await elem.text_content()
                            if text:
                                extracted_data[key].append(text.strip())
                    result["selected_data"] = extracted_data

                # Extract all text
                if extract_all_text:
                    result["text"] = await page.inner_text("body")

                # Extract links
                if extract_links:
                    links = await page.evaluate(
                        """
                        () => Array.from(document.querySelectorAll('a[href]')).map(a => ({
                            text: a.textContent.trim(),
                            href: a.href,
                            title: a.title || null
                        }))
                    """
                    )
                    result["links"] = links

                # Extract tables
                if extract_tables:
                    tables = await page.evaluate(
                        """
                        () => Array.from(document.querySelectorAll('table')).map(table => {
                            const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim());
                            const rows = Array.from(table.querySelectorAll('tr')).slice(1).map(row => {
                                const cells = Array.from(row.querySelectorAll('td, th'));
                                const rowData = {};
                                cells.forEach((cell, i) => {
                                    const key = headers[i] || `column_${i}`;
                                    rowData[key] = cell.textContent.trim();
                                });
                                return rowData;
                            });
                            return rows;
                        })
                    """
                    )
                    result["tables"] = tables

                # Take screenshot if requested
                if screenshot:
                    screenshot_data = await page.screenshot(full_page=True)
                    result["screenshot"] = {
                        "size": len(screenshot_data),
                        "note": "Screenshot data available as bytes",
                    }

                await browser.close()

                return {"status": "success", "data": result}

        except Exception as e:
            return {"status": "error", "error": str(e), "error_type": type(e).__name__}

    async def _arun(
        self,
        url: str,
        wait_for: Optional[str] = None,
        selectors: Optional[Dict[str, str]] = None,
        extract_all_text: bool = False,
        extract_links: bool = False,
        extract_tables: bool = False,
        screenshot: bool = False,
        execute_script: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Async version of the web scraper tool."""
        return await self._async_run(
            url=url,
            wait_for=wait_for,
            selectors=selectors,
            extract_all_text=extract_all_text,
            extract_links=extract_links,
            extract_tables=extract_tables,
            screenshot=screenshot,
            execute_script=execute_script,
            **kwargs,
        )
