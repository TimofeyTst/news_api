from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.dataset.schemas import DatasetRead

router = APIRouter()

from src.dataset.service import (
    insert_test_dataset,
    read_categories,
    read_sources,
    read_super_categories,
    read_texts,
)
from src.dataset.utils import get_metadata, save_metadata


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


@router.get("/check_source")
async def get_exist_source(
    db: AsyncSession = Depends(get_async_session), new_name: str = "Yahoo"
):
    sources, _, _ = await get_metadata(db)
    exists = new_name in sources
    return {"status": exists}


@router.post("")
async def create_test_dataset(db: AsyncSession = Depends(get_async_session)):
    await insert_test_dataset(db)
    return {"status": "success"}


@router.post("/save_metadata")
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
