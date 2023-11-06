from sqlalchemy.ext.asyncio import AsyncSession

from src.parser.async_client import Client
from src.yahoo.parser import YahooParser


async def run_client_in_background(db: AsyncSession, queries_count):
    client = Client(db, queries_count, YahooParser(), debug=True)
    await client.start()
