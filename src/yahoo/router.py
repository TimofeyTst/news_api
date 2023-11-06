from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.yahoo.utils import run_client_in_background

router = APIRouter()


@router.post("")
async def parse_yahoo(
    background_tasks: BackgroundTasks,
    queries_count: int = 1,
    db: AsyncSession = Depends(get_async_session),
):
    # Запустить клиент в фоновой задаче
    background_tasks.add_task(run_client_in_background, db, queries_count)
    return {"status": "started"}
