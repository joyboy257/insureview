import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import router as v1_router
from app.core.config import settings

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Insurance Portfolio API")
    yield
    logger.info("Shutting down Insurance Portfolio API")


app = FastAPI(
    title="Insurance Portfolio Analyzer API",
    description="Singapore insurance policy analysis platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def pdpa_logging_middleware(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        logger.info(
            "api_call",
            extra={
                "method": request.method,
                "path": request.url.path,
                "ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            },
        )
    return response


app.include_router(v1_router)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )
