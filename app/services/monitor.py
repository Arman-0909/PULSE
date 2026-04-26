import httpx
import time
import asyncio
from datetime import datetime
from sqlmodel import Session, select
from app.db.database import engine
from app.db.models import Metric, Service
from app.core.config import REQUEST_TIMEOUT, DEFAULT_HEADERS
from app.core.websocket import manager
from app.utils.logger import get_logger

logger = get_logger("monitor")


async def check_service(service):
    start_time = time.time()

    try:
        async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True
        ) as client:

            response = await client.get(
                service.url,
                headers=DEFAULT_HEADERS
            )

        response_time = round((time.time() - start_time) * 1000, 2)
        status_code = response.status_code
        success = status_code < 500

    except Exception as e:
        logger.error(f"{service.url} -> {e}")
        response_time = 0.0
        status_code = 0
        success = False

    checked_at = datetime.utcnow()

    # Save to DB
    metric = Metric(
        service_id=service.id,
        status_code=status_code,
        response_time=response_time,
        success=success,
        checked_at=checked_at
    )
    with Session(engine) as session:
        session.add(metric)
        session.commit()

    # Broadcast to WebSocket clients (use plain values, not ORM objects)
    try:
        await manager.broadcast({
            "type": "metric",
            "service_id": service.id,
            "name": service.name,
            "url": service.url,
            "status": "up" if success else "down",
            "status_code": status_code,
            "response_time": response_time,
            "checked_at": checked_at.strftime("%H:%M:%S")
        })
    except Exception as e:
        logger.error(f"Broadcast failed: {e}")