from contextlib import contextmanager, asynccontextmanager
import os
from playwright.sync_api import Page as PlaywrightPage
from .page import Page as VibePage
from stagehand import Stagehand, StagehandConfig
from stagehand.context import StagehandContext


class WrappedContext:
    """Browser context wrapper that automatically wraps pages with VibePage functionality."""

    def __init__(self, stagehand_context: StagehandContext):
        self._stagehand_context = stagehand_context

    def __getattr__(self, name):
        # Forward attribute lookups to the underlying StagehandContext
        attr = getattr(self._stagehand_context, name)

        # Special handling for methods that return pages
        if name == "new_page":
            # Replace with our own implementation that wraps the page
            async def wrapped_new_page(*args, **kwargs):
                stagehand_page = await self._stagehand_context.new_page(*args, **kwargs)
                return VibePage(stagehand_page)

            return wrapped_new_page

        elif name == "pages":

            async def wrapped_pages():
                stagehand_pages = self._stagehand_context.pages
                result = []
                for stagehand_page in stagehand_pages:
                    result.append(VibePage(stagehand_page))
                return result

            return wrapped_pages

        return attr


def get_browser(headless: bool | None = None, slow_mo: float | None = None):
    """Get browser - use get_browser_sync for sync contexts or get_browser_async for async contexts"""
    # For backward compatibility, try to detect if we're in async context
    import asyncio

    try:
        asyncio.get_running_loop()
        # We're in an async context, but this function is sync
        # We'll return the sync version and let the user handle async properly
        return get_browser_sync(headless, slow_mo)
    except RuntimeError:
        # No event loop, use sync version
        return get_browser_sync(headless, slow_mo)


@contextmanager
def get_browser_sync(headless: bool | None = None, slow_mo: float | None = None):
    """Recommended way to get a Playwright browser instance in Vibe Automation Framework.

    There are three running modes:
    1. during local development, we can get a local browser instance
    2. in managed execution environment, the browser instance are provided by Orby. This is
       activated via the presence of CONNECTION_URL.
    Returns a wrapped browser that automatically wraps pages with VibePage functionality
    when new_page() is called, eliminating the need for manual wrap() calls.
    """
    connection_url = os.environ.get("CONNECTION_URL")
    if connection_url:
        # Connect to existing browser instance via CDP
        local_browser_launch_options = {
            "cdp_url": connection_url,
        }
    else:
        # Launch a new browser instance
        local_browser_launch_options = {
            "headless": headless,
            "slow_mo": slow_mo,
        }

    config = StagehandConfig(
        env="LOCAL",
        model_name="claude-3-7-sonnet-20250219",
        model_client_options={"apiKey": os.getenv("ANTHROPIC_API_KEY")},
        local_browser_launch_options=local_browser_launch_options,
    )

    stagehand = Stagehand(config)
    import asyncio

    asyncio.run(stagehand.init())

    try:
        yield WrappedContext(stagehand.context)
    finally:
        asyncio.run(stagehand.close())


@asynccontextmanager
async def get_browser_context(
    headless: bool | None = None, slow_mo: float | None = None
):
    """Async version of get_browser for use in async contexts."""
    connection_url = os.environ.get("CONNECTION_URL")
    if connection_url:
        # Connect to existing browser instance via CDP
        local_browser_launch_options = {
            "cdp_url": connection_url,
        }
    else:
        # Launch a new browser instance
        local_browser_launch_options = {
            "headless": headless,
            "slow_mo": slow_mo,
        }

    config = StagehandConfig(
        env="LOCAL",
        model_name="claude-3-7-sonnet-20250219",
        model_client_options={"apiKey": os.getenv("ANTHROPIC_API_KEY")},
        local_browser_launch_options=local_browser_launch_options,
    )

    stagehand = Stagehand(config)
    await stagehand.init()

    try:
        yield WrappedContext(stagehand.context)
    finally:
        await stagehand.close()


def wrap(page: PlaywrightPage) -> VibePage:
    if isinstance(page, VibePage):
        # already wrapped
        return page

    vibe_page = VibePage.create(page)
    return vibe_page
