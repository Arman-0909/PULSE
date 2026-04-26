import httpx
import time
from datetime import datetime
from sqlmodel import Session
from app.db.database import engine
from app.db.models import Metric


async def check_service(service):
    start_time = time.time()

    try:
        async with httpx.AsyncClient(
            timeout=5,
            follow_redirects=True
        ) as client:

            response = await client.get(
                service.url,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "*/*",
                    "Connection": "keep-alive"
                }
            )

        response_time = round((time.time() - start_time) * 1000, 2)

        # ✔ treat <500 as success (real monitoring logic)
        success = response.status_code < 500

        metric = Metric(
            service_id=service.id,
            status_code=response.status_code,
            response_time=response_time,
            success=success,
            checked_at=datetime.utcnow()
        )

    except Exception as e:
        print(f"[ERROR] {service.url} -> {e}")

        metric = Metric(
            service_id=service.id,
            status_code=0,
            response_time=0.0,
            success=False,
            checked_at=datetime.utcnow()
        )

    # save to DB
    with Session(engine) as session:
        session.add(metric)
        session.commit()