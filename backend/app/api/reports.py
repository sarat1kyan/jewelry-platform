from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from datetime import date, timedelta
import csv, io
from app.models.db import get_db
from sqlalchemy import text

router = APIRouter()

def daily_utilization(db: Session, day: str):
    sql = text("""
    WITH hb AS (
      SELECT agent_id, created_at::date as d,
             CASE WHEN is_rhino_running OR is_rhino_foreground THEN 1 ELSE 0 END AS active
      FROM heartbeats
      WHERE created_at::date = :day
    )
    SELECT agent_id,
           SUM(active) * 0.5 AS active_minutes,  -- 30s heartbeat ~ 0.5 min
           COUNT(*) AS total_heartbeats
    FROM hb
    GROUP BY agent_id
    ORDER BY agent_id;
    """)
    rows = db.execute(sql, {"day": day}).fetchall()
    return [{"agent_id": r[0], "active_minutes": float(r[1]), "heartbeats": int(r[2])} for r in rows]

@router.get("")
def reports(range: str = Query("daily", enum=["daily","weekly","monthly"]),
            db: Session = Depends(get_db)):
    today = date.today()
    if range == "daily":
        days = [today]
    elif range == "weekly":
        start = today - timedelta(days=today.weekday())
        days = [start + timedelta(days=i) for i in range(7)]
    else:
        start = today.replace(day=1)
        days = [start + timedelta(days=i) for i in range(31) if (start + timedelta(days=i)).month == start.month]

    by_day = []
    for d in days:
        rows = daily_utilization(db, d.isoformat())
        by_day.append({"day": d.isoformat(), "data": rows})

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["day","agent_id","active_minutes","heartbeats"])
    for day in by_day:
        for r in day["data"]:
            w.writerow([day["day"], r["agent_id"], r["active_minutes"], r["heartbeats"]])
    buf.seek(0)
    return StreamingResponse(buf, media_type="text/csv",
                             headers={"Content-Disposition":"attachment; filename=utilization.csv"})
