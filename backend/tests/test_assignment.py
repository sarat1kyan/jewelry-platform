from app.services.assignment import top_free_workers
from app.models.db import init_engine, create_all, SessionLocal
from app.models.orm import Agent

def test_assignment_ranking():
    init_engine(); create_all()
    db = SessionLocal()
    try:
        db.query(Agent).delete()
        db.add_all([
            Agent(agent_id="a1", user="A", cpu_5m=5, idle_minutes=10),
            Agent(agent_id="a2", user="B", cpu_5m=2, idle_minutes=5),
            Agent(agent_id="a3", user="C", cpu_5m=1, idle_minutes=1, active_task_id="t1"),
        ]); db.commit()
        ranked = top_free_workers(db)
        assert ranked[0]["agent_id"] == "a2"
    finally:
        db.close()
