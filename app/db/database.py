from sqlmodel import SQLModel, create_engine
from app.db import models

DATABASE_URL = "sqlite:///./pulse.db"

engine = create_engine(DATABASE_URL, echo=True)

def create_db():
    SQLModel.metadata.create_all(engine)