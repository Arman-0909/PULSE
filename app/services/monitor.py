import httpx
import time
from sqlmodel import Session
from app.db.database import engine
from app.db.models import Metric


async def check_service(service):
    start = time.time()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(service.url, timeout=5)

        response_time = time.time() - start

        metric = Metric(
            service_id=service.id,
            status_code=response.status_code,
            response_time=response_time,
            success=response.status_code == 200
        )

    except Exception:
        metric = Metric(
            service_id=service.id,
            status_code=0,
            response_time=0,
            success=False
        )

    with Session(engine) as session:
        session.add(metric)
        session.commit()