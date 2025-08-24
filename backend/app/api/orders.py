from fastapi import APIRouter, Depends, HTTPException
from app.services.filename_rules import load_rules, build_filename
from app.services.dropbox_search import search_similar_files
from app.services.monday_client import MondayClient
from app.services.telegram_bot import notify_new_order
from app.models.schemas import OrderIn, OrderOut
from app.models.db import SessionLocal
from app.models.orm import Order, Suggestion
from sqlalchemy.orm import Session
from app.utils.logging import logger
from app.services.assignment import top_free_workers

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", response_model=OrderOut)
def create_order(order: OrderIn, db: Session = Depends(get_db)):
    rules = load_rules()
    filename = build_filename(order, rules)
    suggestions = search_similar_files(filename)
    workers = top_free_workers(db)
    db_order = Order(
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        customer_phone=order.customer_phone,
        category=order.category,
        design=order.design,
        stone=order.stone,
        metal=order.metal,
        size=str(order.size or ""),
        price=order.price,
        instructions=order.instructions or "",
        canonical_filename=filename,
    )
    db.add(db_order); db.commit(); db.refresh(db_order)
    for s in suggestions:
        db.add(Suggestion(order_id=db_order.id, **s))
    db.commit()
    try:
        monday = MondayClient()
        monday_item = monday.create_draft_item(order, filename)
    except Exception as e:
        logger.warning(f"Monday draft skipped: {e}")
        monday_item = None
    try:
        notify_new_order(order, filename, suggestions, workers, monday_item)
    except Exception as e:
        logger.warning(f"Telegram notify skipped: {e}")
    return OrderOut(
        id=db_order.id,
        filename=filename,
        suggestions=suggestions,
        workers=workers,
        monday_item=monday_item or {},
    )

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    suggestions = [{"filename": s.filename, "path": s.path, "size": s.size, "score": s.score, "temp_link": s.temp_link} for s in order.suggestions]
    workers = top_free_workers(db)
    monday_item = {}
    return OrderOut(id=order.id, filename=order.canonical_filename, suggestions=suggestions, workers=workers, monday_item=monday_item)
