from fastapi import FastAPI
from app.db.database import create_db
from app.api.routes import router
from app.scheduler.jobs import start_scheduler

app = FastAPI(title="Pulse")

@app.on_event("startup")
async def on_startup():
    create_db()
    start_scheduler()

app.include_router(router)

@app.get("/")
def root():
    return {"msg": "Pulse is running"}