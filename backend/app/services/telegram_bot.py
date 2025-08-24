import os, asyncio, httpx
from typing import List, Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
LEAD_CHAT_ID = os.getenv("TEAM_LEAD_CHAT_ID", "")
BASE = os.getenv("PUBLIC_BASE_URL", "https://kaktusing.org").rstrip("/")

_app: Application | None = None
_started = False

async def ensure_started():
    global _app, _started
    if _started or not BOT_TOKEN:
        return
    _app = Application.builder().token(BOT_TOKEN).build()
    _app.add_handler(CommandHandler("start", cmd_start))
    _app.add_handler(CommandHandler("workers", cmd_workers))
    _app.add_handler(CommandHandler("orders", cmd_orders))
    _app.add_handler(CommandHandler("reports", cmd_reports))
    _app.add_handler(CallbackQueryHandler(cb_buttons))
    await _app.initialize()
    await _app.start()
    _started = True

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("SLS Bot ready. Commands: /workers /orders /reports")

async def cmd_workers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with httpx.AsyncClient(timeout=10) as cx:
        r = await cx.get(f"{BASE}/api/agents/workers")
        workers = r.json()
    if not workers:
        await update.message.reply_text("No workers online.")
        return
    lines = []
    for w in workers:
        status = "busy" if w.get("active_task_id") else "free"
        lines.append(f"• {w.get('agent_id')} ({status}) cpu≈{w.get('cpu_5m','-')} idle={w.get('idle_minutes','-')}m")
    await update.message.reply_text("\n".join(lines))

async def cmd_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # If you add a real orders list endpoint, call it here.
    await update.message.reply_text("Orders list not implemented here yet.")

async def cmd_reports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with httpx.AsyncClient(timeout=20) as cx:
        r = await cx.get(f"{BASE}/api/reports?range=daily")
        content = r.text
    await update.message.reply_document(document=("daily.csv", content.encode("utf-8")))

async def cb_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    parts = q.data.split(":")
    if parts[0] == "assign":
        order_id, agent_id = parts[1], parts[2]
        if str(update.effective_user.id) != str(LEAD_CHAT_ID):
            await q.edit_message_text("Only Team Lead can assign.")
            return
        async with httpx.AsyncClient(timeout=10) as cx:
            r = await cx.post(f"{BASE}/api/assign", json={"order_id": order_id, "agent_id": agent_id})
        ok = r.status_code == 200
        await q.edit_message_text(f"Assigned {order_id} → {agent_id}" if ok else "Assign failed.")

async def notify_new_order(order: Dict, suggestions: List[Dict], top_workers: List[Dict]):
    if not BOT_TOKEN or not LEAD_CHAT_ID:
        return
    await ensure_started()
    lines = [
        f"New Order #{order.get('order_id')}",
        f"Client: {order.get('client_name')}",
        f"Filename: {order.get('filename')}",
        "Suggestions:"
    ]
    if suggestions:
        for s in suggestions:
            lines.append(f"  • {s.get('filename')} ({s.get('score','')})")
    else:
        lines.append("  • none")

    kb_rows = []
    if top_workers:
        row = []
        for w in top_workers[:3]:
            row.append(InlineKeyboardButton(
                text=f"Assign to {w.get('agent_id')}",
                callback_data=f"assign:{order.get('order_id')}:{w.get('agent_id')}"
            ))
        kb_rows.append(row)
    kb_rows.append([
        InlineKeyboardButton("Open in Monday", url=order.get("monday_url","https://monday.com")),
        InlineKeyboardButton("View similar files", url=order.get("similar_url", BASE))
    ])
    markup = InlineKeyboardMarkup(kb_rows)

    await _app.bot.send_message(
        chat_id=int(LEAD_CHAT_ID),
        text="\n".join(lines),
