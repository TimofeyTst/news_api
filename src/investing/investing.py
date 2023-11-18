import asyncio
import json
import logging
from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger("parser")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler = logging.FileHandler("data/parsed/parse_log.txt", mode="w")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 YaBrowser/23.3.1.906 (beta) Yowser/2.5 Safari/537.36",
    "accept-language": "ru,en;q=0.9,ba;q=0.8",
}


async def fetch_url(session, url):
    try:
        async with session.get(url, headers=headers) as response:
            return await response.text()
    except aiohttp.client_exceptions.ClientConnectorError as e:
        logger.error(f"Error connecting to {url}: {e}")
    except Exception as e:
        logger.error(f"Failed to retrieve the URL '{url}': {e}")

    return None


def parse_total_pages(html_text):
    soup = BeautifulSoup(html_text, "lxml")
    pages_block = soup.find("div", class_="flex gap-2 items-center")
    pages = pages_block.find_all("button") if pages_block else None
    if pages:
        pages_count = int(pages[-1].text)
    else:
        pages_count = 1
    return pages_count


def parse_news_links(html_text):
    # source, title, timestamp, url
    result = []
    soup = BeautifulSoup(html_text, "lxml")
    articles = soup.find_all("article")

    for article in articles:
        if article.find("svg"):
            continue

        link = article.find("a", class_="inline-block")
        url = link["href"]
        title = link.text
        source_name = article.find_all("span")[-1].text
        time_tag = article.find("time")
        if time_tag:
            datetime_string = time_tag.get("datetime")
            datetime_object = datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S")
        else:
            datetime_object = None

        result.append([source_name, title, datetime_object, url])

    return result, len(articles)


def parse_news_content(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    body = soup.find("div", class_="articlePage")
    content = body.find_all(["p", "h2"], recursive=False)

    result_content = " ".join(tag.get_text(strip=True) for tag in content)
    return result_content


async def parse_file(urls, save_file_path):
    all_data = []
    logger.info("SELENIUM: starting driver...")
    BASE_URL = "https://www.investing.com"

    async with aiohttp.ClientSession() as session:
        for ticker, url in urls:
            try:
                old_len = len(all_data)
                logger.info(f"SELENIUM: opening page URL: {url}...")
                res = await fetch_url(session, url)
                total_pages = parse_total_pages(res)
                logger.info(
                    f"Ticker: {ticker} - Starting parsing... Total pages: {total_pages}"
                )
                total_news = 0
                for i in range(1, total_pages + 1):
                    page_url = f"{url}/{i}"
                    try:
                        res = await fetch_url(session, page_url)
                        data, total = parse_news_links(res)
                        logger.debug(
                            f"Ticker: {ticker} - Page {i} parsed links: {len(data)}, on page links: {total}"
                        )
                        total_news += total

                        # category & supercategroy определяем из самой ссылки, скорее всего придется вручную
                        for source, title, timestamp, news_url in data:
                            res = await fetch_url(session, f"{BASE_URL}{news_url}")
                            body = parse_news_content(res)
                            all_data.append(
                                {
                                    "source": source,
                                    "cat": "Investments",
                                    "ticker": ticker,
                                    "title": title,
                                    "body": body,
                                    "timestamp": str(timestamp),
                                    "url": f"{BASE_URL}{news_url}",
                                }
                            )
                        logger.debug(
                            f"Ticker: {ticker} - Page {i} parsed ticker news: {len(all_data) - old_len}, totally ticker news: {total_news}"
                        )

                    except Exception as e:
                        error_message = getattr(e, "msg", str(e))
                        logger.error(
                            f"Ticker: {ticker}: Error processing URL {page_url}, message: {error_message}"
                        )

                logger.info(
                    f"Ticker: {ticker} - Ending parsing. Total pages: {total_pages}, parsed ticker news: {len(all_data) - old_len}, totally ticker news: {total_news}, totally news: {len(all_data)}"
                )

            except Exception as e:
                error_message = getattr(e, "msg", str(e))
                logger.error(
                    f"Ticker: {ticker} - Error processing URL '{url}', message: {error_message}"
                )
    logger.info("SELENIUM: quit driver...")

    with open(save_file_path, "w", encoding="utf-8") as file:
        json.dump(all_data, file, ensure_ascii=False, indent=4)


async def main():
    file_path = "data/investing.txt"
    with open(file_path, "r") as f:
        urls = [url.split() for url in f.readlines()]

    task_count = 20
    batch_size = len(urls) // task_count + 1

    workers = [
        parse_file(
            urls[i * batch_size : (i + 1) * batch_size],
            save_file_path=f"data/parsed/data{i}.json",
        )
        for i in range(task_count)
    ]
    await asyncio.gather(*workers)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
