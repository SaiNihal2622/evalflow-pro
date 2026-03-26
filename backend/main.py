"""EvalFlow Pro – AI Evaluation & Data Quality Engine.

FastAPI application entry point.
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from db import init_db, close_db
from routes import evaluate_router, stats_router, export_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("evalflow")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: init DB on startup, cleanup on shutdown."""
    logger.info("🚀 Starting EvalFlow Pro...")
    await init_db()
    logger.info("✅ Database initialized")
    yield
    await close_db()
    logger.info("👋 EvalFlow Pro shut down")


app = FastAPI(
    title="EvalFlow Pro",
    description="AI Evaluation & Data Quality Engine — evaluate LLM responses with structured metrics",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = round((time.time() - start) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({elapsed}ms)")
    return response


# Mount routers
app.include_router(evaluate_router)
app.include_router(stats_router)
app.include_router(export_router)


@app.get("/")
async def root():
    return {
        "name": "EvalFlow Pro",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
