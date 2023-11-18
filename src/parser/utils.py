from sqlalchemy.ext.asyncio import AsyncSession

from src.parser.async_client import Client


async def run_client_in_background(db: AsyncSession, queries_count, parser):
    client = Client(db, queries_count, parser, debug=True)
    await client.start()
