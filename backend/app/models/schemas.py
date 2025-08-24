from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict

class OrderIn(BaseModel):
    customer_name: str
    customer_email: EmailStr
    customer_phone: Optional[str] = ""
    category: str
    design: Optional[str] = ""
    stone: Optional[str] = ""
    metal: str
    size: Optional[float] = None
    price: float
    instructions: Optional[str] = ""

class OrderOut(BaseModel):
    id: int
    filename: str
    suggestions: List[Dict]
    workers: List[Dict]
    monday_item: Dict

class AgentRegisterIn(BaseModel):
    agent_id: str
    user: str
    hostname: str

class AgentRegisterOut(BaseModel):
    agent_id: str
    token: str

class HeartbeatIn(BaseModel):
    agent_id: str
    user: Optional[str] = ""
    hostname: Optional[str] = ""
    os_version: Optional[str] = ""
    rhino_version: Optional[str] = ""
    is_rhino_running: bool = False
    is_rhino_foreground: bool = False
    active_task_id: Optional[str] = None
    cpu_5m: Optional[float] = 0.0
    idle_minutes: Optional[float] = 0.0
    last_input_ts: Optional[str] = ""

class AgentEventIn(BaseModel):
    agent_id: str
    type: str
    task_id: Optional[str] = None
    meta: Optional[dict] = {}

class AssignIn(BaseModel):
    order_id: int
    agent_id: str
    task_id: str

class AssignOut(BaseModel):
    ok: bool
