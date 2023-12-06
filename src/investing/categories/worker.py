# from parsing import parse_news_links, parse_news_content
import aiohttp

from src.dataset.utils import save_metadata
from src.investing.categories.parsing import parse_news_content, parse_news_links


async def worker(client):
    async with aiohttp.ClientSession() as session:
        while True:
            data = await client.que.get()
            if data is None:
                await client.que.put(None)
                break

            cat, html_text = data

            news_data = parse_news_links(html_text)
            if news_data is None:
                client.logger.info(f"Client: empty news data after parsing")
                continue

            for source, title, timestamp, news_url in news_data:
                url = f"{client.base_url}{news_url}"
                res = await client.fetch_url(session, url)
                body = parse_news_content(res)
                if body is None:
                    continue

                async with client.lock:
                    await save_metadata(
                        client.db, source, cat, "None", title, body, timestamp, url
                    )

            client.total_news += len(news_data)
            client.total_pages += 1
            if client.logger:
                client.logger.debug(f"Category: {cat} - parsed links: {len(news_data)}")
                if client.total_news % 100 == 0:
                    client.logger.info(
                        f"Client: total parsed news: {client.total_news} total pages: {client.total_pages}"
                    )
