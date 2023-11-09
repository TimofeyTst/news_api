from datetime import datetime

import aiohttp
import yfinance as yf
from bs4 import BeautifulSoup

from src.dataset.constants import TICKERS
from src.parser.abstract_parser import Parser


# Занимается парсингом всех новостей источника Yahoo
# для указанной ссылки на компанию проходит по всем новостям
# и отправляет в self.callback
class YahooParser(Parser):
    root = "https://finance.yahoo.com"

    def __init__(self, tickers=TICKERS):
        super().__init__(tickers)

    def get_data(self):
        source = "Yahoo"
        category = "Investments"
        for ticker in TICKERS.split():
            api = yf.Ticker(ticker)
            newses = api.news
            for news in newses:
                yield [source, category, ticker, news["link"]]

    async def process_data(self, session, data):
        src, cat, supcat, url = data
        news = await self.fetch_url(session, url)
        title, body, timestamp = self.parse_news_text(news)
        return [src, cat, supcat, title, body, timestamp, url]

    async def fetch_url(self, session, url):
        try:
            async with session.get(url, headers=self.headers) as response:
                return await response.text()
        except aiohttp.client_exceptions.ClientConnectorError as e:
            print(f"\033[91mError connecting to {url}: {e}\033[0m")
        except Exception as e:
            print(f"\033[91mFailed to retrieve the URL '{url}': {e}[0m]")

        return None

    def parse_news_text(self, html_text):
        soup = BeautifulSoup(html_text, "lxml")

        # Ищем заголовок новости
        title = soup.find("div", class_="caas-title-wrapper")
        if title:
            news_title = title.text.strip()
        else:
            news_title = ""

        # Ищем тело новости
        body = soup.find("div", class_="caas-body")
        if body:
            news_content = body.text
        else:
            news_content = ""

        time_tag = soup.find("time")
        if time_tag:
            datetime_string = time_tag.get("datetime")
            datetime_object = datetime.strptime(
                datetime_string, "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        else:
            datetime_object = None

        return news_title, news_content, datetime_object
