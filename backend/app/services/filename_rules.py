from pathlib import Path
import pandas as pd
from functools import lru_cache
from typing import Dict
from app.models.schemas import OrderIn

BASELINE = {
    "category": {
        "ER": "er", "WB": "wb", "Earring": "ear", "Necklace": "nck", "Bracelet": "brc",
    },
    "design": {
        "Solitaire": "sol", "Halo": "hal", "Bezel": "bez", "Hidden Halo": "hha", "Three Stone": "tst",
        "Three‑Stone": "tst", "Vintage": "vin", "Tension": "ten", "Signet": "sig", "Unique": "uni",
    },
    "stone": {
        "Round": "rou", "Princess": "pri", "Oval": "ovl", "Emerald": "eme", "Cushion": "cus",
        "Pear": "pea", "Asscher": "asc", "Marquise": "mar", "Radiant": "rad", "Heart": "hrt",
        "Trillion": "tri", "Baguette": "bag", "Kite": "kit", "Hexagon": "hex",
    },
    "metal": {
        "14k White Gold": "14kw", "14k Yellow Gold": "14ky", "14k Rose Gold": "14kr",
        "18k White Gold": "18kw", "18k Yellow Gold": "18ky", "Platinum": "pt",
        "14k White": "14kw", "14k Yellow": "14ky", "14k Rose": "14kr",
        "18k White": "18kw", "18k Yellow": "18ky",
    }
}

@lru_cache()
def load_rules() -> Dict[str, Dict[str, str]]:
    xl_path = Path(__file__).with_name("SLS Naming SH.xlsx")
    rules = {k: v.copy() for k, v in BASELINE.items()}
    if xl_path.exists():
        try:
            xls = pd.ExcelFile(xl_path)
            for sheet in xls.sheet_names:
                df = xls.parse(sheet)
                cols = {c.lower(): c for c in df.columns}
                name_col = cols.get("name") or next((c for c in df.columns if "name" in c.lower()), None)
                code_col = cols.get("code") or next((c for c in df.columns if "code" in c.lower()), None)
                if not (name_col and code_col):
                    continue
                key = None
                s = sheet.lower()
                if "category" in s or "ring type" in s or "type" in s:
                    key = "category"
                elif "design" in s or "shank" in s or "style" in s:
                    key = "design"
                elif "stone" in s or "shape" in s:
                    key = "stone"
                elif "metal" in s or "material" in s:
                    key = "metal"
                if key:
                    for _, row in df.iterrows():
                        name = str(row[name_col]).strip()
                        code = str(row[code_col]).strip().lower()
                        if name and code and code != "nan":
                            rules[key][name] = code
        except Exception:
            pass
    return rules

def _map(rules: Dict[str, Dict[str, str]], bucket: str, value: str) -> str:
    if not value:
        return ""
    if value in rules[bucket]:
        return rules[bucket][value]
    for k, v in rules[bucket].items():
        if k.lower() == value.lower():
            return v
    if bucket == "metal":
        return value.lower().replace(" ", "").replace("gold", "g")
    return value.lower()[:3]

def build_filename(order: OrderIn, rules=None) -> str:
    if rules is None:
        rules = load_rules()
    parts = []
    parts.append(_map(rules, "category", order.category))
    parts.append(_map(rules, "design", order.design or ""))
    parts.append(_map(rules, "stone", order.stone or ""))
    parts.append(_map(rules, "metal", order.metal))
    if order.size:
        parts.append(str(order.size).replace(".", "_"))
    core = "_".join([p for p in parts if p])
    return f"{core}.3dm"
