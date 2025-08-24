# backend/app/api/agents.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.db import get_db
from app.models.orm import Agent, Heartbeat
from app.models.schemas import AgentRegisterIn, AgentRegisterOut, HeartbeatIn

router = APIRouter()

def _agent_id_col():
    """Return the ORM column object for agent id, supporting Agent.id or Agent.agent_id."""
    return getattr(Agent, "id", None) or getattr(Agent, "agent_id", None)

def _heartbeat_agent_id_key():
    """Return the key name for the Heartbeat FK/column: 'agent_id' (common) or fallback."""
    if hasattr(Heartbeat, "agent_id"):
        return "agent_id"
    # If your model uses a different name, add more fallbacks here.
    # For now, default to 'agent_id' to avoid silent drops.
    return "agent_id"

def _new_agent_kwargs(payload: AgentRegisterIn) -> dict:
    """Build constructor kwargs for Agent matching its column names."""
    kwargs = {"hostname": payload.hostname, "user": payload.user}
    if hasattr(Agent, "id"):
        kwargs["id"] = payload.agent_id
    elif hasattr(Agent, "agent_id"):
        kwargs["agent_id"] = payload.agent_id
    else:
        raise RuntimeError("Agent model has neither 'id' nor 'agent_id' column")
    return kwargs


@router.post("/register", response_model=AgentRegisterOut)
def register_agent(payload: AgentRegisterIn, db: Session = Depends(get_db)):
    """
    Register or update an agent (worker).
    Works whether the ORM column is Agent.id or Agent.agent_id.
    """
    agent_id_col = _agent_id_col()
    if agent_id_col is None:
        raise HTTPException(status_code=500, detail="Agent model missing id/agent_id column")

    agent = db.query(Agent).filter(agent_id_col == payload.agent_id).first()
    if not agent:
        agent = Agent(**_new_agent_kwargs(payload))
        db.add(agent)
    else:
        # Update mutable fields
        if hasattr(agent, "hostname"):
            agent.hostname = payload.hostname
        if hasattr(agent, "user"):
            agent.user = payload.user

    db.commit()
    # TODO: replace "ok" with a real JWT if you enable agent auth
    return AgentRegisterOut(agent_id=payload.agent_id, token="ok")


@router.post("/heartbeat")
def heartbeat(payload: HeartbeatIn, db: Session = Depends(get_db)):
    """
    Receive periodic agent status updates.
    """
    agent_id_col = _agent_id_col()
    if agent_id_col is None:
        raise HTTPException(status_code=500, detail="Agent model missing id/agent_id column")

    agent = db.query(Agent).filter(agent_id_col == payload.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="unknown agent")

    # Store heartbeat; avoid double-passing agent_id
    data = payload.model_dump(exclude={"agent_id"})
    hb_kwargs = dict(data)
    hb_kwargs[_heartbeat_agent_id_key()] = payload.agent_id

    hb = Heartbeat(**hb_kwargs)
    db.add(hb)
    db.commit()
    return {"ok": True}
