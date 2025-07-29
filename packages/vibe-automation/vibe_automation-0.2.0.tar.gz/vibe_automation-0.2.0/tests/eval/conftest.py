import pytest
from playwright.sync_api import Route
from urllib.parse import urlparse
from pathlib import Path
from va.playwright import get_browser_context


@pytest.fixture
async def eval_page(request):
    """Fixture that creates a page with web environment setup."""
    # Check if request.param exists (it's set by @setup_eval_page decorator)
    if not hasattr(request, "param"):
        raise ValueError(
            "eval_page fixture can only be used with @setup_eval_page decorator. "
            "Please decorate your test function with @setup_eval_page({'url': '...', 'html': '...'}) "
            "to configure the page environment."
        )

    config = request.param

    # Create browser and page instances
    async with get_browser_context(headless=True) as browser:
        page = await browser.new_page()

        # Set up request interception
        async def handle_route(route: Route):
            request_url = route.request.url
            parsed_url = urlparse(request_url)
            config_url = config.get("url", "")
            config_parsed = urlparse(config_url)

            # Check if this request matches our configured URL
            if (
                parsed_url.netloc == config_parsed.netloc
                and parsed_url.path == config_parsed.path
            ):
                # Serve the configured HTML content
                html_content = config.get("html", "")

                # If html is a Path object, read the file
                if isinstance(html_content, Path):
                    html_content = html_content.read_text(encoding="utf-8")

                await route.fulfill(
                    status=200, content_type="text/html", body=html_content
                )
                return

            # Check if this request matches any additional resources
            resources = config.get("resources", [])
            for resource in resources:
                resource_url = resource.get("url", "")
                resource_parsed = urlparse(resource_url)

                if (
                    parsed_url.netloc == resource_parsed.netloc
                    and parsed_url.path == resource_parsed.path
                ):
                    # Serve the resource content
                    resource_content = resource.get("content", "")

                    # If html is a Path object, read the file
                    if isinstance(resource_content, Path):
                        resource_content = resource_content.read_text(encoding="utf-8")

                    # Determine content type based on URL extension
                    content_type = "text/html"
                    if resource_url.endswith(".js"):
                        content_type = "application/javascript"
                    elif resource_url.endswith(".css"):
                        content_type = "text/css"
                    elif resource_url.endswith(".json"):
                        content_type = "application/json"

                    await route.fulfill(
                        status=200, content_type=content_type, body=resource_content
                    )
                    return

            # Let other requests pass through
            await route.continue_()

        # Register the route handler
        await page.route("**/*", handle_route)

        # Automatically navigate to the configured URL before starting the test
        await page.goto(config.get("url"))
        await page.wait_for_load_state("networkidle")

        try:
            yield page
        finally:
            # Clean up - unroute all handlers
            await page.unroute("**/*")
