from abc import ABC, abstractmethod

from src.dataset.constants import TICKERS


class Parser(ABC):
    def __init__(self, tickers=TICKERS):
        self.headers = {
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 YaBrowser/23.3.1.906 (beta) Yowser/2.5 Safari/537.36",
            "accept-language": "ru,en;q=0.9,ba;q=0.8",
        }
        self.tickers = tickers

    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    async def process_data(self, session, data):
        pass
