from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.dataset.schemas import DatasetRead, Report
from src.schemas import TextRead

router = APIRouter()

import shutil
from pathlib import Path

from src.dataset.service import (
    generate_yearly_report,
    insert_test_dataset,
    read_categories,
    read_newest_text_date,
    read_oldest_text_date,
    read_repeated_titles,
    read_sources,
    read_super_categories,
    read_texts,
    read_texts_count,
)
from src.dataset.utils import get_metadata, make_dataset_files, save_metadata


@router.get("", response_model=DatasetRead)
async def get_dataset(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_async_session)
):
    sources = await read_sources(db)
    cats = await read_categories(db)
    supcats = await read_super_categories(db)
    texts = await read_texts(db, skip=skip, limit=limit)

    return {
        "sources": sources,
        "categories": cats,
        "supercategories": supcats,
        "texts": texts,
    }


@router.get("/total_news")
async def get_dataset(db: AsyncSession = Depends(get_async_session)):
    texts_count = await read_texts_count(db)
    oldest_date = await read_oldest_text_date(db)
    newest_date = await read_newest_text_date(db)

    return {
        "texts_count": texts_count,
        "oldest_text_date": oldest_date,
        "newest_text_date": newest_date,
    }


@router.get("/download_db_zip")
async def download_db_zip(
    filename: str = "archive_db", db: AsyncSession = Depends(get_async_session)
):
    # Путь к сформированной директории
    db_path = await make_dataset_files(db)
    # Создаем временный каталог для архива
    temp_dir = Path("tmp")
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Создаем zip-архив
    shutil.make_archive(temp_dir / filename, "zip", "tmp", db_path)

    # Отправляем zip-архив в ответе
    return FileResponse(
        temp_dir / f"{filename}.zip",
        headers={"Content-Disposition": f"attachment; filename={filename}.zip"},
    )


@router.get("/check_source")
async def get_exist_source(
    db: AsyncSession = Depends(get_async_session), new_name: str = "Yahoo"
):
    sources, _, _ = await get_metadata(db)
    exists = new_name in sources
    return {"status": exists}


@router.get("/repeated_titles", response_model=list[TextRead])
async def get_exist_source(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_async_session)
):
    texts = await read_repeated_titles(db, skip=skip, limit=limit)
    return texts


@router.post("")
async def create_test_dataset(db: AsyncSession = Depends(get_async_session)):
    await insert_test_dataset(db)
    return {"status": "success"}


@router.get("/report", response_model=Report)
async def get_report(db: AsyncSession = Depends(get_async_session)):
    report = await generate_yearly_report(db)
    return {"years": report}


@router.post("")
async def create_test_dataset(db: AsyncSession = Depends(get_async_session)):
    await insert_test_dataset(db)
    return {"status": "success"}


@router.post("/news")
async def create_new_text(
    src_name: str = "BBC",
    cat_name: str = "Politics",
    supcat_name: str = "META",
    title: str = "TIMOFEY SHOKED OTHER",
    body: str = "IT IS BODY",
    db: AsyncSession = Depends(get_async_session),
):
    await save_metadata(db, src_name, cat_name, supcat_name, title, body)
    return {"status": "success"}
