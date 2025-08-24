from app.models.schemas import HeartbeatIn, AgentEventIn

def test_agent_schemas():
    hb = HeartbeatIn(agent_id="dev1", is_rhino_running=True)
    assert hb.is_rhino_running is True
    ev = AgentEventIn(agent_id="dev1", type="file_done")
    assert ev.type == "file_done"
