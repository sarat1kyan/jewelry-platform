from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from datetime import datetime
from app.models.db import Base

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    customer_phone = Column(String, default="")
    category = Column(String, nullable=False)
    design = Column(String, default="")
    stone = Column(String, default="")
    metal = Column(String, nullable=False)
    size = Column(String, default="")
    price = Column(Float, default=0.0)
    instructions = Column(Text, default="")
    canonical_filename = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    suggestions = relationship("Suggestion", back_populates="order")

class Suggestion(Base):
    __tablename__ = "suggestions"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    filename = Column(String)
    path = Column(String)
    size = Column(String)
    score = Column(Integer, default=0)
    temp_link = Column(String, default="")
    order = relationship("Order", back_populates="suggestions")

class Agent(Base):
    __tablename__ = "agents"
    agent_id = Column(String, primary_key=True)
    user = Column(String, default="")
    hostname = Column(String, default="")
    last_seen = Column(DateTime, default=datetime.utcnow)
    active_task_id = Column(String, nullable=True)
    is_rhino_running = Column(Boolean, default=False)
    cpu_5m = Column(Float, default=0.0)
    idle_minutes = Column(Float, default=0.0)

class Heartbeat(Base):
    __tablename__ = "heartbeats"
    id = Column(Integer, primary_key=True)
    agent_id = Column(String, ForeignKey("agents.agent_id"))
    user = Column(String, default="")
    hostname = Column(String, default="")
    os_version = Column(String, default="")
    rhino_version = Column(String, default="")
    is_rhino_running = Column(Boolean, default=False)
    is_rhino_foreground = Column(Boolean, default=False)
    active_task_id = Column(String, nullable=True)
    cpu_5m = Column(Float, default=0.0)
    idle_minutes = Column(Float, default=0.0)
    last_input_ts = Column(String, default="")
    ts = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    agent_id = Column(String)
    type = Column(String)
    task_id = Column(String, nullable=True)
    meta = Column(Text, default="")
    ts = Column(DateTime, default=datetime.utcnow)

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    agent_id = Column(String)
    task_id = Column(String)
    ts = Column(DateTime, default=datetime.utcnow)
