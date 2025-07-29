import asyncio
import logging

from va import step, review, workflow, ReviewStatus
from va.playwright import get_browser_context


@workflow("Example workflow")
async def main():
    async with get_browser_context(headless=False, slow_mo=1000) as browser:
        page = await browser.new_page()

        with step("navigate to the form"):
            await page.goto("https://forms.gle/pV8CD8cAjgZPWcmV6")

        with step("fill the form"):
            await page.get_by_label("What is the item you would like to order?").fill(
                "T-shirt"
            )
            await page.get_by_label("Your name").fill("<NAME>")

        with step("submit the form"):
            r = review("final-review", "Check if the form is correct")
            if r.status != ReviewStatus.READY:
                print("exiting execution since review is not ready")
                return
            await page.get_by_text("Submit").click()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
