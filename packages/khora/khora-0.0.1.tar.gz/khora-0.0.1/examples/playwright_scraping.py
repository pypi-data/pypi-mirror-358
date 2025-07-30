"""Example of advanced web scraping with Playwright in Khora."""

import asyncio

from khora.tools import WebScraperTool


async def example_basic_scraping():
    """Basic web scraping example."""
    scraper = WebScraperTool()

    result = await scraper._arun(
        url="https://example.com",
        extract_all_text=True,
        extract_links=True,
        extract_tables=True,
    )

    if result["status"] == "success":
        print("✅ Successfully scraped the page!")
        print(f"Title: {result['data']['title']}")
        print(f"Number of links: {len(result['data'].get('links', []))}")
        print(f"Number of tables: {len(result['data'].get('tables', []))}")
    else:
        print(f"❌ Error: {result['error']}")


async def example_javascript_site():
    """Scraping JavaScript-rendered content."""
    scraper = WebScraperTool()

    # Example: Scraping a React/Vue/Angular site
    result = await scraper._arun(
        url="https://news.ycombinator.com",
        wait_for="networkidle",  # Wait for all network requests to finish
        selectors={
            "titles": ".titleline > a",
            "scores": ".score",
            "comments": ".subline > a:last-child",
        },
    )

    if result["status"] == "success":
        data = result["data"]
        print("📰 Hacker News Top Stories:")
        titles = data.get("selected_data", {}).get("titles", [])
        for i, title in enumerate(titles[:10]):
            print(f"{i+1}. {title}")


async def example_custom_javascript():
    """Using custom JavaScript to extract data."""
    scraper = WebScraperTool()

    # Custom JavaScript to extract structured data
    custom_script = """
    () => {
        // Extract all product data from an e-commerce site
        const products = [];
        document.querySelectorAll('.product-item').forEach(item => {
            products.push({
                name: item.querySelector('.product-name')?.textContent.trim(),
                price: item.querySelector('.price')?.textContent.trim(),
                rating: item.querySelector('.rating')?.textContent.trim(),
                availability: item.querySelector('.availability')?.textContent.trim()
            });
        });
        return products;
    }
    """

    result = await scraper._arun(
        url="https://example-shop.com/products",
        wait_for=".product-item",  # Wait for products to load
        execute_script=custom_script,
    )

    if result["status"] == "success":
        products = result["data"].get("script_result", [])
        print(f"🛍️ Found {len(products)} products")
        for product in products[:5]:
            print(f"- {product.get('name')} - {product.get('price')}")


async def example_screenshot_capture():
    """Taking screenshots of web pages."""
    scraper = WebScraperTool()

    result = await scraper._arun(
        url="https://github.com/trending",
        wait_for="networkidle",
        screenshot=True,
        selectors={
            "repos": "h2.h3.lh-condensed a",
            "descriptions": "p.col-9.color-fg-muted",
        },
    )

    if result["status"] == "success":
        print("📸 Screenshot captured!")
        print(f"Screenshot size: {result['data']['screenshot']['size']} bytes")

        repos = result["data"].get("selected_data", {}).get("repos", [])
        print(f"\n🔥 Trending repositories: {len(repos)}")
        for repo in repos[:5]:
            print(f"- {repo}")


async def example_form_interaction():
    """Example of interacting with forms (conceptual - would need agent enhancement)."""
    print("\n📝 Form Interaction Example")
    print("Note: This demonstrates how Playwright could interact with forms.")
    print("The current implementation focuses on data extraction,")
    print("but Playwright supports:")
    print("- Filling forms: page.fill('#input-id', 'value')")
    print("- Clicking buttons: page.click('#submit-button')")
    print("- Selecting options: page.select_option('#dropdown', 'option-value')")
    print("- Typing text: page.type('#search', 'search query')")
    print(
        "\nThese capabilities can be added to the WebScraperTool for interactive scraping."
    )


async def main():
    """Run all examples."""
    print("🚀 Khora Playwright Web Scraping Examples")
    print("=" * 50)

    print("\n1️⃣ Basic Web Scraping:")
    await example_basic_scraping()

    print("\n2️⃣ JavaScript-Rendered Content:")
    await example_javascript_site()

    print("\n3️⃣ Custom JavaScript Extraction:")
    await example_custom_javascript()

    print("\n4️⃣ Screenshot Capture:")
    await example_screenshot_capture()

    print("\n5️⃣ Form Interaction (Conceptual):")
    await example_form_interaction()

    print("\n✨ Playwright advantages over traditional scraping:")
    print("- Handles JavaScript-rendered content")
    print("- Can wait for specific elements or states")
    print("- Supports screenshots and visual testing")
    print("- Can interact with forms and buttons")
    print("- Executes custom JavaScript in page context")
    print("- Better handling of modern web applications")


if __name__ == "__main__":
    asyncio.run(main())
