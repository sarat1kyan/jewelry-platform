from fastapi import APIRouter, Request, HTTPException
from app.models.db import SessionLocal
from app.models.orm import Order, Agent, Assignment
from app.services.telegram_bot import send_to
import os

router = APIRouter()

TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")

def _assert_secret(req: Request):
    exp = TELEGRAM_WEBHOOK_SECRET
    if not exp:
        return
    tok = req.query_params.get("token")
    if tok != exp:
        raise HTTPException(status_code=403, detail="forbidden")

@router.post("/webhooks/telegram")
async def telegram_webhook(request: Request):
    _assert_secret(request)
    upd = await request.json()
    try:
        # Inline callbacks
        if 'callback_query' in upd:
            cq = upd['callback_query']
            chat_id = str(cq['message']['chat']['id'])
            data = (cq.get('data') or '')
            if data.startswith('assign:'):
                # assign:<order_id>:<agent_id>
                _, order_id, agent_id = (data.split(':', 2) + [None, None, None])[:3]
                if order_id and agent_id:
                    db = SessionLocal()
                    try:
                        # upsert assignment
                        db.add(Assignment(order_id=int(order_id), agent_id=agent_id, task_id=f"TASK-{order_id}"))
                        ag = db.get(Agent, agent_id)
                        if ag:
                            ag.active_task_id = f"TASK-{order_id}"
                        db.commit()
                        send_to(chat_id, f"✅ Assigned order {order_id} to {agent_id}")
                    finally:
                        db.close()
            return {"ok": True}

        # Text commands
        if 'message' in upd:
            msg = upd['message']
            chat_id = str(msg['chat']['id'])
            text = (msg.get('text') or '').strip()

            if text.startswith('/orders'):
                db = SessionLocal()
                try:
                    items = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()
                    if not items:
                        send_to(chat_id, "No orders yet.")
                    else:
                        lines = ["Last 5 orders:"]
                        for o in items:
                            lines.append(f"#{o.id} {o.customer_name} — {o.canonical_filename}")
                        send_to(chat_id, "\n".join(lines))
                finally:
                    db.close()

            elif text.startswith('/workers'):
                db = SessionLocal()
                try:
                    agents = db.query(Agent).all()
                    if not agents:
                        send_to(chat_id, "No agents registered.")
                    else:
                        lines = ["Workers:"]
                        for a in agents:
                            status = f"busy({a.active_task_id})" if a.active_task_id else "free"
                            lines.append(f"{a.user or a.agent_id}: {status}, cpu={a.cpu_5m}, idle={a.idle_minutes}m")
                        send_to(chat_id, "\n".join(lines))
                finally:
                    db.close()

            elif text.startswith('/report'):
                rng = 'daily'
                if 'weekly' in text: rng = 'weekly'
                elif 'monthly' in text: rng = 'monthly'
                # You can wire this to /api/reports later
                send_to(chat_id, f"Report request accepted: {rng}")

            else:
                send_to(chat_id, "Commands: /orders, /workers, /report daily|weekly|monthly")

            return {"ok": True}

    except Exception:
        # swallow errors to avoid Telegram retries
        return {"ok": True}

    return {"ok": True}

@router.post("/webhooks/monday")
async def monday_webhook(request: Request):
    _ = await request.json()
    return {"ok": True}
