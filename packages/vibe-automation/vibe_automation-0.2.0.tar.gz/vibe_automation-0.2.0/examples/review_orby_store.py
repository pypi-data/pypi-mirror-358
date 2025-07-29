import logging

import asyncio
import os
from va import step, review, workflow, ReviewStatus
from va.playwright import get_browser_context


@workflow("Example workflow")
async def main():
    async with get_browser_context(headless=False, slow_mo=1000) as browser:
        page = await browser.new_page()

        with step("navigate to the form"):
            await page.goto(
                "https://docs.google.com/forms/d/1kVoQeC-71STEhOXb3ggpKGg9F3lEIXMxekZ4VJiotMs/viewform?edit_requested=true"
            )

        with step("fill the form"):
            await page.get_by_label("Username").fill("orby")
            await page.get_by_label("Rating").fill("10")
            r = review("final-review", "Please fill the review")
            r.wait(300)
            if r.status != ReviewStatus.READY:
                print("exiting execution since review was not filled")
                return

        with step("submit the form"):
            await page.get_by_label("Submit").click()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    os.environ["VA_EXECUTION_ID"] = "test"
    asyncio.run(main())
