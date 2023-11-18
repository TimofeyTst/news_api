import json

from src.dataset.constants import TICKERS
from src.parser.abstract_parser import Parser


class InvestingFileParser(Parser):
    category = "Investments"

    def __init__(
        self,
        tickers=TICKERS,
        filepaths: list = None,
        log_file_path="tmp/investing_parse_log.txt",
    ):
        super().__init__(tickers, log_file_path)
        self.filepaths = filepaths
        self.log_file_path = log_file_path

    def get_data(self):
        for filepath in self.filepaths:
            with open(filepath, "r") as file:
                data = json.load(file)

            self.logger.info("GET_DATA: starting file: %s, len: ", filepath, len(data))
            for entry in data:
                src = entry.get("source", None)
                cat = entry.get("cat", None)
                ticker = entry.get("ticker", None)
                title = entry.get("title", None)
                body = entry.get("body", None)
                timestamp = entry.get("timestamp", None)
                url = entry.get("url", None)

                yield [src, cat, ticker, title, body, timestamp, url]
            self.logger.info("GET_DATA: end of file: %s", filepath)
        self.logger.info("GET_DATA: end of data")

    async def process_data(self, session, data):
        src, cat, ticker, title, body, timestamp, url = data
        return [src, cat, ticker, title, body, timestamp, url]
