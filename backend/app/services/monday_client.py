import os, httpx
from typing import Optional, Dict
from app.models.schemas import OrderIn

API_URL = "https://api.monday.com/v2"

class MondayClient:
    def __init__(self):
        self.token = os.getenv("MONDAY_TOKEN")
        self.board_id = os.getenv("BOARD_ID")
        if not self.token or not self.board_id:
            raise RuntimeError("MONDAY_TOKEN/BOARD_ID not configured")

    def create_draft_item(self, order: OrderIn, filename: str) -> Optional[Dict]:
        query = (
            "mutation ($board_id: ID!, $item_name: String!) {"
            " create_item (board_id: $board_id, item_name: $item_name) { id name }"
            "}"
        )
        vars = {"board_id": self.board_id, "item_name": f"{order.customer_name} - {filename}"}
        headers = {"Authorization": self.token, "Content-Type": "application/json"}
        try:
            r = httpx.post(API_URL, headers=headers, json={"query": query, "variables": vars}, timeout=10)
            r.raise_for_status()
            data = r.json()
            return data.get("data", {}).get("create_item", {})
        except Exception:
            return None
