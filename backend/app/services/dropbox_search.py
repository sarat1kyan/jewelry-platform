import os
from typing import List, Dict
from dropbox import Dropbox, files
from dropbox.files import FileMetadata
from rapidfuzz import fuzz

def _client() -> Dropbox:
    token = os.getenv("DROPBOX_TOKEN")
    if not token:
        raise RuntimeError("DROPBOX_TOKEN not configured")
    return Dropbox(token)

def _temp_link(dbx: Dropbox, path: str) -> str:
    try:
        return dbx.files_get_temporary_link(path).link
    except Exception:
        return ""

def search_similar_files(canonical_name: str) -> List[Dict]:
    """
    Search exact and fuzzy .3dm files; return top 3 suggestions with ~4h temporary links.
    """
    try:
        dbx = _client()
    except Exception:
        # Safe fallback when token is not configured
        return [{"filename": canonical_name, "path": "/new", "size": "0", "score": 0, "temp_link": ""}]

    # Common search options: only .3dm files
    opts = files.SearchOptions(file_extensions=["3dm"])

    candidates: List[Dict] = []

    # 1) Exact search by the full canonical filename
    try:
        res = dbx.files_search_v2(files.SearchV2Arg(query=canonical_name, options=opts))
        for match in (res.matches or []):
            md = match.metadata.get_metadata()
            if isinstance(md, FileMetadata):
                candidates.append({"filename": md.name, "path": md.path_lower, "size": md.size})
    except Exception:
        # ignore search failure; we'll still return a fallback later if empty
        pass

    # 2) Broaden search: category + design prefix (first two parts)
    try:
        parts = canonical_name.split("_")
        prefix = "_".join(parts[:2]) if len(parts) >= 2 else parts[0]
        if prefix:
            res2 = dbx.files_search_v2(files.SearchV2Arg(query=prefix, options=opts))
            for match in (res2.matches or []):
                md = match.metadata.get_metadata()
                if isinstance(md, FileMetadata):
                    candidates.append({"filename": md.name, "path": md.path_lower, "size": md.size})
    except Exception:
        pass

    # De-dup and score with RapidFuzz
    seen = set()
    scored: List[Dict] = []
    for c in candidates:
        key = c["path"]
        if key in seen:
            continue
        seen.add(key)
        c["score"] = int(fuzz.WRatio(c["filename"], canonical_name))
        scored.append(c)

    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[:3] if scored else [{"filename": canonical_name, "path": "/new", "size": "0", "score": 0}]

    # Add temporary links
    for t in top:
        t["temp_link"] = _temp_link(dbx, t.get("path", "")) if t.get("path") and t["path"].startswith("/") else ""

    return top
