import json
from datetime import datetime
from pathlib import Path

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
    read_texts,
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


async def save_metadata(
    db: AsyncSession,
    src_name,
    cat_name,
    supcat_name,
    title,
    body,
    timestamp=None,
    link=None,
):
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

    if timestamp is None:
        timestamp = datetime.utcnow()

    # Теперь создаем полученную новость
    text = TextCreate(
        title=title,
        body=body,
        link=link,
        timestamp=timestamp,
        source_id=exist_src.id,
        category_id=exist_cat.id,
        supercategory_id=exist_supcat.id,
    )
    await create_text(db, text)


async def make_dataset_files(
    db: AsyncSession, filename="about.json", filepath="tmp/news"
):
    sources = await read_sources(db, skip=0, limit=1000)
    cats = await read_categories(db, skip=0, limit=1000)
    supcats = await read_super_categories(db, skip=0, limit=30000)
    # texts_info = await read_texts_info(db, skip=0, limit=30000)
    texts = await read_texts(db, skip=0, limit=30000)
    await save_text_to_files(texts, filepath)

    about_json = {
        "sources": [
            {
                "id": src.id,
                "name": src.name,
            }
            for src in sources
        ],
        "categories": [
            {
                "id": cat.id,
                "name": cat.name,
            }
            for cat in cats
        ],
        "supercategories": [
            {
                "id": supcat.id,
                "name": supcat.name,
            }
            for supcat in supcats
        ],
        "texts": [
            {
                "id": text.id,
                "file_name": f"news/new_{text.id}/news.txt",
                "time": text.timestamp.strftime("%m-%d-%Y %H:%M:%S"),
                "source_id": text.source_id,
                "category_id": text.category_id,
                "supercategory_id": text.supercategory_id,
            }
            for text in texts
        ],
    }
    full_file_path = filepath + "/" + filename
    files_dir = Path(filepath)
    files_dir.mkdir(parents=True, exist_ok=True)

    with open(full_file_path, "w") as json_file:
        json.dump(about_json, json_file, indent=4)

    return "news"


async def save_text_to_files(texts, base_dir):
    for text in texts:
        # Создаем директорию для каждой новости
        news_dir = Path(base_dir) / f"news/new_{text.id}"
        news_dir.mkdir(parents=True, exist_ok=True)

        # Путь к файлу для данной новости
        file_path = news_dir / "news.txt"

        # Создаем текст для сохранения (title + "\n\n" + body)
        text_to_save = f"{text.title}\n\n{text.body}"

        # Сохраняем текст в файл
        with file_path.open("w", encoding="utf-8") as news_file:
            news_file.write(text_to_save)
