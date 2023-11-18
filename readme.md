# News api
## Fast setup
Предварительно нужно создать файл ```.env``` в корне проекта по шаблону .env.example

Далее надо освободить порт 5432, используемый обычно Postgres, после чего запускаем контейнер:

```shell
docker network create news_api
docker-compose up -d --build
docker compose exec news_api migrate
```

## Parsing
Парсинг с сайта yahoo.com при помощи Selenium с указанием файла для чтения и для сохранения, а также с указанием времени ожидания selenium webdriver

- -s файл для сохранения
- -t время ожидания selenium webdriver 
- -hp в качестве какого поля записывать

```bash
cd src/parser/selenium
python3 parse_news_links.py yahoo_categories.txt -t 60 -s yahoo_categories.json -hp category
```
Или
```bash
cd src/parser/selenium
python3 parse_news_links.py yahoo_urls.txt -t 40
```

Парсинг с сайта investing.com и запись в директорию data/parsed .json файлов в количестве равном числу задач
```bash
cd src/investing
python3 investing.py
```
Полученные файлы используются в маршруте этого роутера

## Commands
### Migrations
- Create an automatic migration from changes in `src/models.py`
```shell
docker compose exec news_api makemigrations users_added # or other name of the migration
```

- Run migrations
```shell
docker compose exec news_api migrate
```
- Downgrade migrations
```shell
docker compose exec news_api downgrade -1  # or -2 or base or hash of the migration
```

### Linter
```shell
docker compose exec news_api format
```

### Tests
```shell
docker compose exec news_api pytest
```

------
## Работа с запущенным сервером
По умолчанию сервер доступен на локальной сети на порту 8000
http://127.0.0.1:8000/
> Для просмотра документации допишите в конце адреса путь docs:
> http://127.0.0.1:8000/docs

## Production deploy
В файл .env добавить переменную SENTRY_DSN для мониторинга и заменить ENVIRONMENT. Например: 

```
...
ENVIRONMENT=PRODUCTION

SENTRY_DSN=https://123456789.ingest.sentry.io/987654321
...
```

Запустить контейнер
```shell
docker network create news_api
docker-compose -f docker-compose.prod.yml up -d --build
```


