from sqlalchemy.ext.asyncio import AsyncSession

from src.investing.categories.async_client import Client as InvestingClient
from src.investing.categories.get_logger import get_logger
from src.parser.async_client import Client


async def run_client_in_background(db: AsyncSession, queries_count, parser):
    client = Client(db, queries_count, parser, debug=True)
    await client.start()


async def run_investing_client_bg(db: AsyncSession, queries_count, urls_file):
    client = InvestingClient(db, queries_count, urls_file, logger=get_logger())
    await client.run_tasks()
