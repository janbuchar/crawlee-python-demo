import asyncio

from crawlee.basic_crawler import Router
from crawlee.models import Request
from crawlee.playwright_crawler import PlaywrightCrawlingContext

router = Router[PlaywrightCrawlingContext]()


@router.default_handler
async def default_handler(context: PlaywrightCrawlingContext) -> None:
    """Default request handler."""

    # Wait for the popup to be visible to ensure it has loaded on the page.
    await context.page.get_by_test_id('dialog-accept-button').click()

    shoe_listing_links = (
        await context.page.get_by_test_id('link').filter(has_text='All shoes').all()
    )
    await context.add_requests(
        [
            Request.from_url(url, label='listing')
            for link in shoe_listing_links
            if (url := await link.get_attribute('href'))
        ]
    )


@router.handler('listing')
async def listing_handler(context: PlaywrightCrawlingContext) -> None:
    """Handler for shoe listings."""
