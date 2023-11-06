import aiohttp
import yfinance as yf
from bs4 import BeautifulSoup

from src.dataset.constants import TICKERS
from src.parser.abstract_parser import Parser


# Занимается парсингом всех новостей источника Yahoo
# для указанной ссылки на компанию проходит по всем новостям
# и отправляет в self.callback
class YahooParser(Parser):
    def __init__(self, tickers=TICKERS):
        super().__init__(tickers)
        self.root = "https://finance.yahoo.com"

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
        title, body = self.parse_news_text(news)
        return [src, cat, supcat, title, body]

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
        soup = BeautifulSoup(html_text, "html.parser")

        # Ищем заголовок новости
        title = soup.select_one("h1")
        if title:
            news_title = title.text.strip()
        else:
            news_title = ""

        # Ищем тело новости
        body = soup.select(
            "div article div div div div div div.caas-content-wrapper > div.caas-body"
        )

        # Извлекаем текст из каждого элемента p и объединяем его
        news_content = "\n\n".join([p.text.strip() for p in body])

        return news_title, news_content
