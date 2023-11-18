from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.parser.utils import run_client_in_background
from src.yahoo.file_parser import YahooCategoryFileParser, YahooFileParser
from src.yahoo.parser import YahooParser

router = APIRouter()


@router.post("")
async def parse_yahoo(
    background_tasks: BackgroundTasks,
    queries_count: int = 1,
    db: AsyncSession = Depends(get_async_session),
):
    # Запустить клиент в фоновой задаче
    parser = YahooParser()
    background_tasks.add_task(run_client_in_background, db, queries_count, parser)
    return {"status": "started"}


@router.post("/from_files")
async def parse_yahoo_file(
    background_tasks: BackgroundTasks,
    queries_count: int = 1,
    db: AsyncSession = Depends(get_async_session),
):
    filepaths = ["src/yahoo/data/second_data.json"]
    # Запустить клиент в фоновой задаче
    parser = YahooFileParser(filepaths=filepaths)
    background_tasks.add_task(run_client_in_background, db, queries_count, parser)
    return {"status": "started"}


@router.post("/parse_categories")
async def parse_yahoo_file(
    background_tasks: BackgroundTasks,
    queries_count: int = 1,
    db: AsyncSession = Depends(get_async_session),
):
    filepaths = ["src/yahoo/data/yahoo_categories.json"]
    # Запустить клиент в фоновой задаче
    parser = YahooCategoryFileParser(filepaths=filepaths)
    background_tasks.add_task(run_client_in_background, db, queries_count, parser)
    return {"status": "started"}
