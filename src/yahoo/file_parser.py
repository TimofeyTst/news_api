import json

from src.dataset.constants import TICKERS
from src.yahoo.parser import YahooParser


class YahooFileParser(YahooParser):
    def __init__(self, tickers=TICKERS, filepaths: list = None):
        super().__init__(tickers)
        self.filepaths = filepaths

    def get_data(self):
        for filepath in self.filepaths:
            with open(filepath, "r") as file:
                data = json.load(file)

                for entry in data:
                    source = entry.get("source_name", None)
                    category = "Investments"
                    ticker = entry.get("ticker", None)
                    link = entry.get("link", None)

                    yield [source, category, ticker, link]
