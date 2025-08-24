from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import AssignIn, AssignOut
from app.models.db import SessionLocal
from app.models.orm import Assignment, Agent
from sqlalchemy.orm import Session
from app.services.telegram_bot import send_text
from app.utils.logging import logger

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/assign", response_model=AssignOut)
def assign_worker(payload: AssignIn, db: Session = Depends(get_db)):
    agent = db.get(Agent, payload.agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    a = Assignment(order_id=payload.order_id, agent_id=payload.agent_id, task_id=payload.task_id)
    db.add(a); db.commit()
    try:
        send_text(f"Assigned order {payload.order_id} to {agent.user} ({agent.agent_id})")
    except Exception as e:
        logger.warning(f"Telegram send failed: {e}")
    return AssignOut(ok=True)
