import sentry_sdk
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.config import app_configs, settings
from src.dataset.router import router as dataset_router
from src.investing.router import router as investing_router
from src.yahoo.router import router as yahoo_router

app = FastAPI(**app_configs)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)

if settings.ENVIRONMENT.is_deployed:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
    )


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(dataset_router, prefix="/dataset", tags=["dataset"])
app.include_router(yahoo_router, prefix="/yahoo", tags=["parser"])
app.include_router(investing_router, prefix="/investing", tags=["parser"])
