from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class ServiceGroup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Service(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    url: str
    group_id: Optional[int] = Field(default=None, foreign_key="servicegroup.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Metric(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    service_id: int
    status_code: int
    response_time: float
    success: bool
    checked_at: datetime = Field(default_factory=datetime.utcnow)