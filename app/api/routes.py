from fastapi import APIRouter, Request, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.db.database import get_session
from app.db.models import User, Service, ServiceGroup, Metric
from app.core.auth import hash_password, verify_password, create_token, decode_token
from app.core.websocket import manager
from app.utils.logger import get_logger

logger = get_logger("routes")
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# =========================
# AUTH HELPERS
# =========================
def get_current_user(request: Request, session: Session) -> User | None:
    token = request.cookies.get("pulse_token")
    if not token:
        return None
    username = decode_token(token)
    if not username:
        return None
    return session.exec(select(User).where(User.username == username)).first()


def is_authenticated(request: Request, session: Session) -> bool:
    return get_current_user(request, session) is not None


# =========================
# LOGIN
# =========================
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, session: Session = Depends(get_session)):
    if is_authenticated(request, session):
        return RedirectResponse(url="/admin", status_code=303)
    error = request.query_params.get("error", "")
    tab = request.query_params.get("tab", "login")
    return templates.TemplateResponse(request, "login.html", context={"error": error, "tab": tab})


@router.post("/login")
async def login(request: Request, session: Session = Depends(get_session)):
    form = await request.form()
    username = form.get("username", "").strip()
    password = form.get("password", "").strip()

    if not username or not password:
        return RedirectResponse(url="/login?error=All+fields+required", status_code=303)

    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password, user.password_hash):
        return RedirectResponse(url="/login?error=Invalid+username+or+password", status_code=303)

    token = create_token(username)
    response = RedirectResponse(url="/admin", status_code=303)
    response.set_cookie(key="pulse_token", value=token, httponly=True, max_age=86400, samesite="lax")
    logger.info(f"Login: {username}")
    return response


# =========================
# SIGNUP
# =========================
@router.post("/signup")
async def signup(request: Request, session: Session = Depends(get_session)):
    form = await request.form()
    username = form.get("username", "").strip()
    password = form.get("password", "").strip()
    confirm = form.get("confirm", "").strip()

    if not username or not password:
        return RedirectResponse(url="/login?tab=signup&error=All+fields+required", status_code=303)
    if len(password) < 6:
        return RedirectResponse(url="/login?tab=signup&error=Password+must+be+6%2B+characters", status_code=303)
    if password != confirm:
        return RedirectResponse(url="/login?tab=signup&error=Passwords+do+not+match", status_code=303)

    existing = session.exec(select(User).where(User.username == username)).first()
    if existing:
        return RedirectResponse(url="/login?tab=signup&error=Username+already+taken", status_code=303)

    user = User(username=username, password_hash=hash_password(password))
    session.add(user)
    session.commit()
    logger.info(f"Signup: {username}")

    token = create_token(username)
    response = RedirectResponse(url="/admin", status_code=303)
    response.set_cookie(key="pulse_token", value=token, httponly=True, max_age=86400, samesite="lax")
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("pulse_token")
    return response


# =========================
# HOME (public)
# =========================
@router.get("/", response_class=HTMLResponse)
def home(request: Request, session: Session = Depends(get_session)):
    services = session.exec(select(Service)).all()
    total = len(services)
    online = 0; total_response = 0; checked = 0

    for service in services:
        latest = session.exec(select(Metric).where(Metric.service_id == service.id).order_by(Metric.id.desc())).first()
        if latest:
            if latest.success: online += 1
            total_response += latest.response_time
            checked += 1

    avg_response = round(total_response / checked, 1) if checked > 0 else 0
    uptime_pct = round((online / total) * 100, 1) if total > 0 else 100

    return templates.TemplateResponse(request, "index.html", context={
        "total": total, "online": online, "offline": total - online,
        "avg_response": avg_response, "uptime_pct": uptime_pct,
        "logged_in": is_authenticated(request, session)
    })


# =========================
# DASHBOARD (public)
# =========================
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, session: Session = Depends(get_session)):
    services = session.exec(select(Service)).all()
    groups_map = {g.id: g.name for g in session.exec(select(ServiceGroup)).all()}

    result = []
    total_online = 0; total_response = 0; checked_count = 0

    for service in services:
        metrics = session.exec(select(Metric).where(Metric.service_id == service.id).order_by(Metric.id.desc())).all()
        total = len(metrics)
        success = len([m for m in metrics if m.success])
        uptime = (success / total * 100) if total > 0 else 0
        status = "up" if metrics and metrics[0].success else "down"
        response_time = metrics[0].response_time if metrics else 0
        last_checked = metrics[0].checked_at.strftime("%H:%M:%S") if metrics else "Never"
        sparkline = [m.response_time for m in reversed(metrics[:20])]

        if status == "up": total_online += 1
        if metrics: total_response += response_time; checked_count += 1

        result.append({
            "id": service.id, "name": service.name, "url": service.url,
            "group": groups_map.get(service.group_id),
            "status": status, "uptime": round(uptime, 1),
            "response_time": round(response_time, 1),
            "last_checked": last_checked, "sparkline": sparkline, "total_checks": total
        })

    avg_response = round(total_response / checked_count, 1) if checked_count > 0 else 0
    return templates.TemplateResponse(request, "dashboard.html", context={
        "services": result, "total": len(services),
        "online": total_online, "offline": len(services) - total_online,
        "avg_response": avg_response, "logged_in": is_authenticated(request, session)
    })


# =========================
# ADMIN (auth required)
# =========================
@router.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, session: Session = Depends(get_session)):
    user = get_current_user(request, session)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    services = session.exec(select(Service)).all()
    groups = session.exec(select(ServiceGroup)).all()
    groups_map = {g.id: g.name for g in groups}

    services_data = []
    for s in services:
        latest = session.exec(select(Metric).where(Metric.service_id == s.id).order_by(Metric.id.desc())).first()
        services_data.append({
            "id": s.id, "name": s.name, "url": s.url,
            "group_id": s.group_id, "group_name": groups_map.get(s.group_id),
            "status": "up" if latest and latest.success else ("down" if latest else "pending"),
        })

    toast = None; toast_type = "success"
    if request.query_params.get("added"):
        toast = f"Service \"{request.query_params.get('added')}\" added"
    elif request.query_params.get("deleted"):
        toast = f"Service \"{request.query_params.get('deleted')}\" deleted"
    elif request.query_params.get("edited"):
        toast = f"Service \"{request.query_params.get('edited')}\" updated"
    elif request.query_params.get("group_added"):
        toast = f"Group \"{request.query_params.get('group_added')}\" created"
    elif request.query_params.get("error"):
        toast = request.query_params.get("error"); toast_type = "error"

    return templates.TemplateResponse(request, "admin.html", context={
        "services": services_data, "groups": groups,
        "toast": toast, "toast_type": toast_type, "user": user
    })


# =========================
# CRUD (auth required)
# =========================
def _require_auth(request: Request, session: Session) -> User:
    user = get_current_user(request, session)
    if not user:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return user


@router.post("/add-service")
async def add_service(request: Request, session: Session = Depends(get_session)):
    _require_auth(request, session)
    form = await request.form()
    name = form.get("name", "").strip()
    url = form.get("url", "").strip()
    group_id = form.get("group_id")

    if not name or not url:
        return RedirectResponse(url="/admin?error=Name+and+URL+required", status_code=303)
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    if session.exec(select(Service).where(Service.url == url)).first():
        return RedirectResponse(url="/admin?error=URL+already+exists", status_code=303)

    session.add(Service(name=name, url=url, group_id=int(group_id) if group_id else None))
    session.commit()
    logger.info(f"Service added: {name}")
    return RedirectResponse(url=f"/admin?added={name}", status_code=303)


@router.post("/edit-service/{service_id}")
async def edit_service(service_id: int, request: Request, session: Session = Depends(get_session)):
    _require_auth(request, session)
    service = session.get(Service, service_id)
    if not service:
        return RedirectResponse(url="/admin?error=Not+found", status_code=303)

    form = await request.form()
    name = form.get("name", "").strip()
    url = form.get("url", "").strip()
    group_id = form.get("group_id")

    if name: service.name = name
    if url:
        if not url.startswith(("http://", "https://")): url = "https://" + url
        service.url = url
    service.group_id = int(group_id) if group_id else None
    session.add(service); session.commit()
    logger.info(f"Service edited: {service.name}")
    return RedirectResponse(url=f"/admin?edited={service.name}", status_code=303)


@router.post("/add-group")
async def add_group(request: Request, session: Session = Depends(get_session)):
    _require_auth(request, session)
    form = await request.form()
    name = form.get("name", "").strip()
    if not name:
        return RedirectResponse(url="/admin?error=Name+required", status_code=303)
    if session.exec(select(ServiceGroup).where(ServiceGroup.name == name)).first():
        return RedirectResponse(url="/admin?error=Group+exists", status_code=303)

    session.add(ServiceGroup(name=name)); session.commit()
    logger.info(f"Group created: {name}")
    return RedirectResponse(url=f"/admin?group_added={name}", status_code=303)


@router.post("/delete-service/{service_id}")
def delete_service(service_id: int, request: Request, session: Session = Depends(get_session)):
    _require_auth(request, session)
    service = session.get(Service, service_id)
    if not service:
        return RedirectResponse(url="/admin?error=Not+found", status_code=303)
    name = service.name
    for m in session.exec(select(Metric).where(Metric.service_id == service_id)).all():
        session.delete(m)
    session.delete(service); session.commit()
    logger.info(f"Service deleted: {name}")
    return RedirectResponse(url=f"/admin?deleted={name}", status_code=303)


# =========================
# WEBSOCKET
# =========================
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# =========================
# REST API
# =========================
@router.get("/api/services", tags=["API"])
def api_services(session: Session = Depends(get_session)):
    services = session.exec(select(Service)).all()
    groups_map = {g.id: g.name for g in session.exec(select(ServiceGroup)).all()}
    result = []
    for s in services:
        latest = session.exec(select(Metric).where(Metric.service_id == s.id).order_by(Metric.id.desc())).first()
        metrics = session.exec(select(Metric).where(Metric.service_id == s.id)).all()
        total = len(metrics); success = len([m for m in metrics if m.success])
        result.append({
            "id": s.id, "name": s.name, "url": s.url,
            "group": groups_map.get(s.group_id),
            "status": "up" if latest and latest.success else "down",
            "uptime": round((success/total*100) if total > 0 else 0, 1),
            "response_time": round(latest.response_time, 1) if latest else 0,
            "last_checked": latest.checked_at.isoformat() if latest else None,
            "sparkline": [m.response_time for m in metrics[-20:]]
        })
    return result


@router.get("/api/stats", tags=["API"])
def api_stats(session: Session = Depends(get_session)):
    services = session.exec(select(Service)).all()
    online = 0; total_response = 0; checked = 0
    for s in services:
        latest = session.exec(select(Metric).where(Metric.service_id == s.id).order_by(Metric.id.desc())).first()
        if latest:
            if latest.success: online += 1
            total_response += latest.response_time; checked += 1
    total = len(services)
    return {
        "total": total, "online": online, "offline": total - online,
        "avg_response": round(total_response / checked, 1) if checked > 0 else 0,
        "uptime_pct": round((online / total) * 100, 1) if total > 0 else 100
    }


@router.get("/api/services/{sid}/metrics", tags=["API"])
def api_metrics(sid: int, session: Session = Depends(get_session)):
    service = session.get(Service, sid)
    if not service: raise HTTPException(404, "Not found")
    metrics = session.exec(select(Metric).where(Metric.service_id == sid).order_by(Metric.id.desc())).all()
    return {"service": {"id": service.id, "name": service.name}, "count": len(metrics),
            "metrics": [{"status_code": m.status_code, "response_time": m.response_time, "success": m.success, "checked_at": m.checked_at.isoformat()} for m in metrics[:100]]}


@router.delete("/api/services/{sid}", tags=["API"])
def api_delete(sid: int, session: Session = Depends(get_session)):
    service = session.get(Service, sid)
    if not service: raise HTTPException(404, "Not found")
    name = service.name
    for m in session.exec(select(Metric).where(Metric.service_id == sid)).all(): session.delete(m)
    session.delete(service); session.commit()
    return {"deleted": name}


@router.get("/api/groups", tags=["API"])
def api_groups(session: Session = Depends(get_session)):
    return [{"id": g.id, "name": g.name} for g in session.exec(select(ServiceGroup)).all()]