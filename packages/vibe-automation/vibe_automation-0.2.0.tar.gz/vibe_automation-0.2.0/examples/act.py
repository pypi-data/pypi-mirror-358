import asyncio
import logging

from va import step, workflow
from va.playwright import get_browser_context


@workflow("Act Example")
async def main():
    async with get_browser_context(headless=False, slow_mo=1000) as browser:
        page = await browser.new_page()

        with step("Navigate to the test page"):
            await page.goto("https://httpbin.org/forms/post")

        with step("Use page.act to fill form"):
            # Use the act method to accomplish a user task
            result = await page.act(
                "Fill out the form with customer name 'John Smith'",
            )

            print(f"Task completed: {result.success}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
