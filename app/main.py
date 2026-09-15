
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.research import router as research_router
from app.memory.memory import is_redis_connected
from app.rag.vector_store import client
from app.config import settings



# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("researchos")


# ---------------------------------------------------------
# Application lifecycle
# ---------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs when the FastAPI application starts and stops.
    """

    logger.info(
        "Starting %s v%s",
        settings.app_name,
        settings.app_version,
    )

    logger.info(
        "Environment: %s",
        settings.environment,
    )

    logger.info(
        "Qdrant collection: %s",
        settings.qdrant_collection,
    )

    yield

    logger.info("Shutting down %s", settings.app_name)


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    description=(
        "Production-ready AI research platform using "
        "LangGraph, Qdrant, Tavily, DeepSeek and Redis."
    ),
    version=settings.app_version,
    lifespan=lifespan,
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------

app.include_router(
    research_router,
    prefix="/api",
)


# ---------------------------------------------------------
# Basic endpoints
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
def health():
    """
    Basic API health check.

    This only verifies that the FastAPI application
    itself is running.
    """

    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/api/status")
def status():
    """
    Returns the status of the ResearchOS services.
    """

    # Qdrant
    qdrant_status = "offline"

    try:
        client.get_collections()
        qdrant_status = "online"
    except Exception:
        qdrant_status = "offline"

    # Redis
    redis_status = (
        "online"
        if is_redis_connected()
        else "offline"
    )

    # DeepSeek
    deepseek_status = (
        "online"
        if settings.deepseek_api_key
        else "offline"
    )

    # Tavily
    tavily_status = (
        "online"
        if settings.tavily_api_key
        else "offline"
    )

    return {
        "status": "online",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "qdrant_collection": settings.qdrant_collection,

        "services": {
            "deepseek": deepseek_status,
            "tavily": tavily_status,
            "qdrant": qdrant_status,
            "redis": redis_status,
        },
    }

