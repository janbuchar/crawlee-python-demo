import asyncio

from crawlee.playwright_crawler.playwright_crawler import PlaywrightCrawler

from .routes import router


async def main() -> None:
    """The crawler entry point."""
    crawler = PlaywrightCrawler(
        headless=False,
        request_handler=router,
        max_requests_per_crawl=100,
    )

    await crawler.run(
        [
            'https://nike.com/cz/en',
        ]
    )

    await crawler.export_data('shoes.csv')


if __name__ == '__main__':
    asyncio.run(main())
