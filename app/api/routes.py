from fastapi import APIRouter, Request
from sqlmodel import Session, select
from sqlalchemy import desc
from app.db.database import engine
from app.db.models import Service, Metric, ServiceGroup
from jinja2 import Environment, FileSystemLoader
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os

router = APIRouter()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

env = Environment(
    loader=FileSystemLoader("app/templates"),
    autoescape=True
)

# ---------------------- SCHEMAS ----------------------

class ServiceCreate(BaseModel):
    name: str
    url: str


class GroupCreate(BaseModel):
    name: str


# ---------------------- ROOT ----------------------

@router.get("/")
def root():
    return {
        "project": "Pulse",
        "status": "running",
        "docs": "/docs",
        "dashboard": "/dashboard"
    }


# ---------------------- DASHBOARD ----------------------

@router.get("/dashboard")
def dashboard(request: Request):
    with Session(engine) as session:
        services = session.exec(select(Service)).all()

        data = []
        for s in services:
            metrics = session.exec(
                select(Metric)
                .where(Metric.service_id == s.id)
                .order_by(desc(Metric.checked_at))
                .limit(50)
            ).all()

            total = len(metrics)
            success = sum(1 for m in metrics if m.success)
            uptime = (success / total * 100) if total > 0 else 0

            latest = metrics[0] if metrics else None
            status = "up" if latest and latest.success else "down"

            data.append({
                "name": s.name,
                "url": s.url,
                "status": status,
                "uptime": round(uptime, 2)
            })

    template = env.get_template("dashboard.html")

    html = template.render(services=data)

    return HTMLResponse(content=html)


# ---------------------- SERVICES ----------------------

@router.post("/services")
def add_service(data: ServiceCreate):
    with Session(engine) as session:
        service = Service(name=data.name, url=data.url)
        session.add(service)
        session.commit()
        session.refresh(service)
        return service


@router.get("/services")
def get_services():
    with Session(engine) as session:
        return session.exec(select(Service)).all()


@router.get("/services/{service_id}")
def get_service(service_id: int):
    with Session(engine) as session:
        service = session.get(Service, service_id)
        if not service:
            return {"msg": "not found"}
        return service


# ---------------------- METRICS ----------------------

@router.get("/metrics")
def get_metrics():
    with Session(engine) as session:
        return session.exec(select(Metric)).all()


@router.get("/metrics/{service_id}")
def get_service_metrics(service_id: int):
    with Session(engine) as session:
        return session.exec(
            select(Metric)
            .where(Metric.service_id == service_id)
            .order_by(desc(Metric.checked_at))
            .limit(50)
        ).all()


# ---------------------- ANALYTICS ----------------------

@router.get("/services/{service_id}/stats")
def get_service_stats(service_id: int):
    with Session(engine) as session:
        metrics = session.exec(
            select(Metric).where(Metric.service_id == service_id)
        ).all()

    total = len(metrics)
    success = sum(1 for m in metrics if m.success)
    uptime = (success / total * 100) if total > 0 else 0

    return {
        "total_checks": total,
        "success_checks": success,
        "uptime_percent": round(uptime, 2)
    }


@router.get("/services/{service_id}/status")
def get_service_status(service_id: int):
    with Session(engine) as session:
        metric = session.exec(
            select(Metric)
            .where(Metric.service_id == service_id)
            .order_by(desc(Metric.checked_at))
        ).first()

    if not metric:
        return {"status": "unknown"}

    return {
        "status": "up" if metric.success else "down",
        "last_checked": metric.checked_at,
        "response_time": metric.response_time
    }


@router.get("/services/{service_id}/failures")
def get_failures(service_id: int):
    with Session(engine) as session:
        metrics = session.exec(
            select(Metric)
            .where(
                (Metric.service_id == service_id) &
                (Metric.success.is_(False))
            )
            .order_by(desc(Metric.checked_at))
            .limit(50)
        ).all()

    return {
        "failure_count": len(metrics),
        "failures": metrics
    }


# ---------------------- GROUPS ----------------------

@router.post("/groups")
def create_group(data: GroupCreate):
    with Session(engine) as session:
        g = ServiceGroup(name=data.name)
        session.add(g)
        session.commit()
        session.refresh(g)
        return g


@router.get("/groups")
def get_groups():
    with Session(engine) as session:
        return session.exec(select(ServiceGroup)).all()


@router.post("/services/{service_id}/group/{group_id}")
def assign_group(service_id: int, group_id: int):
    with Session(engine) as session:
        service = session.get(Service, service_id)
        if not service:
            return {"msg": "service not found"}

        service.group_id = group_id
        session.add(service)
        session.commit()
        session.refresh(service)
        return service
    

@router.delete("/services/{service_id}")
def delete_service(service_id: int):
    with Session(engine) as session:
        service = session.get(Service, service_id)

        if not service:
            return {"msg": "not found"}

        session.delete(service)
        session.commit()

        return {"msg": "deleted"}