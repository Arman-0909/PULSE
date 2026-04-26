from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import create_db
from app.api.routes import router
from app.scheduler.jobs import start_scheduler
from app.utils.logger import get_logger

logger = get_logger("pulse")


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    start_scheduler()
    logger.info("Pulse is running")
    yield
    logger.info("Pulse shutting down")


app = FastAPI(
    title="Pulse",
    description="Real-time API & Service Health Monitoring",
    version="2.0.0",
    lifespan=lifespan
)

# CORS for API consumers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)