import logging

from playwright.sync_api import Locator
from stagehand import StagehandPage

from .locator import PromptBasedLocator

log = logging.getLogger("va.playwright")


class Page:
    def __init__(self, page: StagehandPage):
        self._stagehand_page = page

    def get_by_prompt(
        self,
        prompt: str,
    ) -> PromptBasedLocator:
        """
        Returns a PromptBasedLocator that can be used with or without fallback locators

        Parameters:
        -----------
        prompt (str): The natural language description of the element to locate.
        timeout (int) (optional): Timeout value in seconds for the connection with backend API service.
        wait_for_network_idle (bool) (optional): Whether to wait for network reaching full idle state before querying the page. If set to `False`, this method will only check for whether page has emitted [`load` event](https://developer.mozilla.org/en-US/docs/Web/API/Window/load_event).
        include_hidden (bool) (optional): Whether to include hidden elements on the page. Defaults to `True`.
        mode (ResponseMode) (optional): The response mode. Can be either `standard` or `fast`. Defaults to `fast`.
        experimental_query_elements_enabled (bool) (optional): Whether to use the experimental implementation of the query elements feature. Defaults to `False`.

        Returns:
        --------
        PromptBasedLocator: A locator that uses prompt-based element finding
        """
        return PromptBasedLocator(self, prompt)

    async def get_locator_by_prompt(
        self,
        prompt: str,
    ) -> Locator | None:
        """
        Internal method to get element by prompt - used by PromptBasedLocator

        Returns:
        --------
        Playwright [Locator](https://playwright.dev/python/docs/api/class-locator) | None: The found element or `None` if no matching elements were found.
        """

        results = await self._stagehand_page.observe(prompt)

        if not results:
            return None

        selector = results[0].selector
        return self._stagehand_page.locator(selector)

    def __getattr__(self, name):
        """Forward attribute lookups to the underlying Stagehand page."""
        return getattr(self._stagehand_page, name)
