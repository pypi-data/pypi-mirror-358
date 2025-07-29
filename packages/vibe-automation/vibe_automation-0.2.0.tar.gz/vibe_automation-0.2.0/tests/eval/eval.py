import pytest
from functools import wraps
import inspect


def setup_eval_page(*, url: str = "http://localhost/", html, resources=None):
    """
    Set up test environment for web automation using synthetic HTML or WARC file. Example usage:

    @setup_eval_page(
        html="<input name='search query'/> <button>Search</button>"
    )
    async def test_get_by_prompt(eval_page):
        element = eval_page.get_by_prompt("The search button")
        assert await element.text_content() == "Search"

    Alternatively, you can also serve the HTML from a given local file content.

    You can also provide additional resources to be served:

    @setup_eval_page(
        html="<script src='/script.js'></script>",
        resources=[
            {"url": "http://localhost/script.js", "content": "console.log('loaded');"}
        ]
    )

    It works by intercepting requests from the Playwright page and serves the corresponding response.
    """

    # Create config dict from kwargs
    config = {"url": url, "html": html, "resources": resources or []}

    def decorator(test_func):
        # Add pytest.mark.parametrize with indirect=True
        test_func = pytest.mark.parametrize("eval_page", [config], indirect=True)(
            test_func
        )

        if inspect.iscoroutinefunction(test_func):

            @wraps(test_func)
            async def async_wrapper(*args, **kwargs):
                return await test_func(*args, **kwargs)

            return async_wrapper
        else:

            @wraps(test_func)
            def wrapper(*args, **kwargs):
                return test_func(*args, **kwargs)

            return wrapper

    return decorator
