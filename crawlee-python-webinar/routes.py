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

    await context.enqueue_links(selector='a.product-card__link-overlay', label='detail')


@router.handler('detail')
async def detail_handler(context: PlaywrightCrawlingContext) -> None:
    """Handler for shoe details."""

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
