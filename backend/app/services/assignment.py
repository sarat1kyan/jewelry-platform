from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.orm import Agent, Assignment
from sqlalchemy import func

def top_free_workers(db: Session) -> List[Dict]:
    agents = db.query(Agent).all()
    tasks_today = dict(db.query(Assignment.agent_id, func.count(Assignment.id)).group_by(Assignment.agent_id).all())
    ranked = []
    for a in agents:
        ranked.append({
            "agent_id": a.agent_id,
            "user": a.user,
            "cpu_5m": a.cpu_5m or 0.0,
            "idle_minutes": a.idle_minutes or 0.0,
            "active_task_id": a.active_task_id,
            "tasks_today": tasks_today.get(a.agent_id, 0),
        })
    ranked.sort(key=lambda w: (w["active_task_id"] is not None, w["cpu_5m"], w["idle_minutes"], w["tasks_today"]))
    return ranked[:3]
