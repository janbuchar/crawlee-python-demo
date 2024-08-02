from crawlee.basic_crawler import Router
from crawlee.playwright_crawler import PlaywrightCrawlingContext

router = Router[PlaywrightCrawlingContext]()


@router.default_handler
async def default_handler(context: PlaywrightCrawlingContext) -> None:
    """Default request handler."""

    # Wait for the popup to be visible to ensure it has loaded on the page.
    await context.page.get_by_test_id('dialog-accept-button').click()
