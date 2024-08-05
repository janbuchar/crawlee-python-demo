import asyncio
from contextlib import suppress, asynccontextmanager

from crawlee.basic_crawler import Router
from crawlee.models import Request
from crawlee.playwright_crawler import PlaywrightCrawlingContext
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

router = Router[PlaywrightCrawlingContext]()


@asynccontextmanager
async def accept_cookies(page: Page):
    task = asyncio.create_task(page.get_by_test_id('dialog-accept-button').click())
    try:
        yield
    finally:
        if not task.done():
            task.cancel()

        with suppress(asyncio.CancelledError, PlaywrightTimeoutError):
            await task


@router.default_handler
async def default_handler(context: PlaywrightCrawlingContext) -> None:
    """Default request handler."""

    async with accept_cookies(context.page):
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

    async with accept_cookies(context.page):
        await context.page.wait_for_load_state('networkidle')
        await context.infinite_scroll()
        await context.enqueue_links(
            selector='a.product-card__link-overlay', label='detail'
        )


@router.handler('detail')
async def detail_handler(context: PlaywrightCrawlingContext) -> None:
    """Handler for shoe details."""

    async with accept_cookies(context.page):
        title = await context.page.get_by_test_id(
            'product_title',
        ).text_content()

        price = await context.page.get_by_test_id(
            'currentPrice-container',
        ).first.text_content()

        description = await context.page.get_by_test_id(
            'product-description',
        ).text_content()

        await context.push_data(
            {
                'url': context.request.loaded_url,
                'title': title,
                'price': price,
                'description': description,
            }
        )
