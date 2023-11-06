from sqlalchemy.ext.asyncio import AsyncSession

from src.dataset.service import (
    create_category,
    create_source,
    create_super_category,
    create_text,
    read_categories,
    read_category_by_name,
    read_source_by_name,
    read_sources,
    read_super_categories,
    read_super_category_by_name,
    read_text_by_title,
)
from src.schemas import CategoryCreate, SourceCreate, SuperCategoryCreate, TextCreate


async def get_metadata(db: AsyncSession):
    sources = await read_sources(db)
    cats = await read_categories(db)
    supcats = await read_super_categories(db)

    source_names = [source.name for source in sources]
    cats_names = [cat.name for cat in cats]
    supcats_names = [supcat.name for supcat in supcats]

    return source_names, cats_names, supcats_names


async def save_metadata(db: AsyncSession, src_name, cat_name, supcat_name, title, body):
    exist_title = await read_text_by_title(db, title)
    if exist_title:
        return
    # Пытаемся получить существующий
    exist_src = await read_source_by_name(db, src_name)
    if not exist_src:
        exist_src = await create_source(db, SourceCreate(name=src_name))

    # Пытаемся получить существующую
    exist_cat = await read_category_by_name(db, cat_name)
    if not exist_cat:
        exist_cat = await create_category(db, CategoryCreate(name=cat_name))

    # Пытаемся получить существующую
    exist_supcat = await read_super_category_by_name(db, supcat_name)
    if not exist_supcat:
        exist_supcat = await create_super_category(
            db, SuperCategoryCreate(name=supcat_name)
        )

    # Теперь создаем полученную новость
    text = TextCreate(
        title=title,
        body=body,
        link=None,
        source_id=exist_src.id,
        category_id=exist_cat.id,
        supercategory_id=exist_supcat.id,
    )
    await create_text(db, text)
