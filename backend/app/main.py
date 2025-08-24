from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api import orders, agents, assign, telemetry, reports, webhooks
from app.models.db import init_engine, create_all
from app.utils.logging import logger
import os

app = FastAPI(title="SLS Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(assign.router, prefix="/api/assign", tags=["assign"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(telemetry.router, prefix="/api/telemetry", tags=["telemetry"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


@app.on_event("startup")
async def startup_event():
    init_engine()
    create_all()
    logger.info("SLS Platform started")
