import asyncio

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from src.parser.worker import Worker


class Client:
    def __init__(
        self,
        db: AsyncSession,
        task_count: int = 1,
        parser=None,
        debug=False,
    ):
        if task_count <= 0:
            raise ValueError("Tasks count must be > 0")

        self.task_count = task_count
        self.parser = parser
        self.debug = debug
        self.que = asyncio.Queue()
        self.lock = asyncio.Lock()
        self.processed_urls = 0
        self.db = db

    async def start(self):
        async with aiohttp.ClientSession() as session:
            # Создание асинхронных задач
            workers = [Worker(self, session).start() for _ in range(self.task_count)]
            if self.debug:
                self.tasks_created = len(workers)
                print(f"\033[33mTasks created: {self.tasks_created}\033[0m")

            for data in self.parser.get_data():
                await self.que.put(data)

            await self.que.put(None)
            await asyncio.gather(*workers)
