from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlmodel import Session, select
from app.db.database import engine
from app.db.models import Service
from app.services.monitor import check_service

scheduler = AsyncIOScheduler()


async def monitor_all():
    with Session(engine) as session:
        services = session.exec(select(Service)).all()

    for service in services:
        await check_service(service)


def start_scheduler():
    scheduler.add_job(monitor_all, "interval", seconds=30)
    scheduler.start()