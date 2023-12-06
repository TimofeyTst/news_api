import asyncio

import aiohttp

from src.investing.categories.parsing import parse_is_next_page
from src.investing.categories.worker import worker

# from parsing import parse_is_next_page
# from worker import worker


class Client:
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 YaBrowser/23.3.1.906 (beta) Yowser/2.5 Safari/537.36",
        "accept-language": "ru,en;q=0.9,ba;q=0.8",
    }
    base_url = "https://www.investing.com"

    def __init__(self, db, task_count, urls_file, worker=worker, logger=None):
        if task_count <= 0:
            raise ValueError("Tasks count must be > 0")

        self.task_count = task_count
        self.urls_file = urls_file
        self.logger = logger
        self.que = asyncio.Queue(maxsize=task_count * 10)
        self.lock = asyncio.Lock()
        self.worker = worker
        self.total_news = 0
        self.total_pages = 0
        self.db = db

    def start(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.run_tasks())
        except KeyboardInterrupt:
            pass
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

    async def run_tasks(self):
        if self.logger:
            self.logger.info("Parsing: starting...")
        # Создание асинхронных задач
        workers = [self.create_tasks()]
        workers.extend([self.worker(self) for _ in range(self.task_count)])

        if self.logger:
            self.tasks_created = len(workers)
            self.logger.info(
                f"Tasks created: {self.tasks_created} (function for task creating and {self.tasks_created - 1} workers)"
            )

        await asyncio.gather(*workers)

        if self.logger:
            self.logger.info("Parsing: ended.")

    async def create_tasks(self):
        # Помещает полученные данные в очередь
        # html_text - страница со списком новостей
        # ожидаем, что воркер обработает все новости на ней
        # и сохранит в бд
        async with aiohttp.ClientSession() as session:
            async for cat, html_text in self.get_data(session):
                await self.que.put([cat, html_text])
            await self.que.put(None)

    async def get_data(self, session):
        with open(self.urls_file, "r") as file:
            for line in file:
                idx = 1
                is_next_page = True
                cat, base_url = line.split()
                while is_next_page:
                    url = f"{base_url}/{idx + 500}"
                    res = await self.fetch_url(session, url)
                    yield cat, res
                    is_next_page = await parse_is_next_page(res)

                    if self.logger and idx % 10 == 0:
                        self.logger.debug(
                            f"Category {cat}: total pages sent in queue '{idx}'"
                        )
                    idx += 1

    async def fetch_url(self, session, url):
        try:
            async with session.get(url, headers=self.headers) as response:
                return await response.text()
        except aiohttp.client_exceptions.ClientConnectorError as e:
            if self.logger:
                self.logger.error(f"Error connecting to {url}: {e}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to retrieve the URL '{url}': {e}")

        return None
