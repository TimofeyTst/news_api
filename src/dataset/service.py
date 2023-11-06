from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dataset.schemas import DatasetRead
from src.models import Category, Source, SuperCategory, Text
from src.schemas import (
    CategoryCreate,
    CategoryRead,
    SourceCreate,
    SourceRead,
    SuperCategoryCreate,
    SuperCategoryRead,
    TextCreate,
    TextRead,
)


async def read_sources(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> DatasetRead:
    query = select(Source).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


async def read_source_by_name(db: AsyncSession, name: str) -> SourceRead:
    query = select(Source).where(Source.name == name)
    result = await db.execute(query)
    return result.scalars().first()


async def create_source(db: AsyncSession, source: SourceCreate) -> SourceRead:
    insert_query = insert(Source).values(**source.model_dump()).returning(Source)

    source = await db.execute(insert_query)
    await db.commit()
    return source.scalars().first()


async def read_categories(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> DatasetRead:
    query = select(Category).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


async def read_category_by_name(db: AsyncSession, name: str) -> CategoryRead:
    query = select(Category).where(Category.name == name)
    result = await db.execute(query)
    return result.scalars().first()


async def create_category(db: AsyncSession, category: CategoryCreate) -> CategoryRead:
    insert_query = insert(Category).values(**category.model_dump()).returning(Category)

    category = await db.execute(insert_query)
    await db.commit()
    return category.scalars().first()


async def read_super_categories(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> DatasetRead:
    query = select(SuperCategory).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


async def read_super_category_by_name(db: AsyncSession, name: str) -> SuperCategoryRead:
    query = select(SuperCategory).where(SuperCategory.name == name)
    result = await db.execute(query)
    return result.scalars().first()


async def create_super_category(
    db: AsyncSession, supcat: SuperCategoryCreate
) -> SuperCategoryRead:
    insert_query = (
        insert(SuperCategory).values(**supcat.model_dump()).returning(SuperCategory)
    )

    supcat = await db.execute(insert_query)
    await db.commit()
    return supcat.scalars().first()


async def read_texts(db: AsyncSession, skip: int = 0, limit: int = 100) -> DatasetRead:
    query = select(Text).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()

async def read_text_by_title(db: AsyncSession, title: str) -> SourceRead:
    query = select(Text).where(Text.title == title)
    result = await db.execute(query)
    return result.scalars().first()

async def create_text(db: AsyncSession, text: TextCreate) -> TextRead:
    insert_query = insert(Text).values(**text.model_dump()).returning(Text)

    text = await db.execute(insert_query)
    await db.commit()
    return text.scalars().first()


async def insert_test_dataset(db: AsyncSession):
    source = Source(name="Yahoo")

    cat = Category(name="Investments")

    supcat = SuperCategory(name="AAPL")

    text = Text(
        title="Example title",
        body="This is a test dataset",
        source_id=1,
        category_id=1,
        supercategory_id=1,
    )

    db.add_all([source, cat, supcat, text])

    await db.commit()