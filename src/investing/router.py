from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.investing.parser import InvestingFileParser
from src.parser.utils import run_client_in_background, run_investing_client_bg

router = APIRouter()


@router.post("")
async def parse_investing(
    background_tasks: BackgroundTasks,
    queries_count: int = 1,
    db: AsyncSession = Depends(get_async_session),
):
    # Запустить клиент в фоновой задаче
    filepaths = [f"src/investing/data/parsed/data{i}.json" for i in range(18)]
    parser = InvestingFileParser(filepaths=filepaths)
    background_tasks.add_task(run_client_in_background, db, queries_count, parser)
    return {"status": "started"}


@router.post("/categories")
async def parse_investing_categories(
    background_tasks: BackgroundTasks,
    queries_count: int = 1,
    urls_file: str = "src/investing/data/categories.txt",
    db: AsyncSession = Depends(get_async_session),
):
    background_tasks.add_task(run_investing_client_bg, db, queries_count, urls_file)
    return {"status": "started"}
