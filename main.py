from __future__ import annotations
import re
import sqlite3
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import DB_PATH, CSV_PATH, get_connection
from models import LookupResponse

app = FastAPI(title="SP Health Caller ID API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D+", "", phone or "")
    if not digits:
        return ""
    if digits.startswith("55"):
        return "+" + digits
    if len(digits) in {10, 11}:
        return "+55" + digits
    return "+" + digits


def ensure_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Seed CSV not found: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    required = {"name", "phone", "city", "type", "address", "whatsapp", "notes"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {sorted(missing)}")
    df["normalized_phone"] = df["phone"].astype(str).map(normalize_phone)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("health_centers", conn, if_exists="replace", index=False)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_health_phone ON health_centers(normalized_phone)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_health_city ON health_centers(city)")
    conn.commit()
    conn.close()


@app.on_event("startup")
def startup() -> None:
    ensure_database()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "db": str(DB_PATH)}


@app.get("/v1/lookup", response_model=LookupResponse)
def lookup(phone: str) -> LookupResponse:
    normalized = normalize_phone(phone)
    if not normalized:
        raise HTTPException(status_code=400, detail="Invalid phone number")

    conn = get_connection()
    row = conn.execute(
        """
        SELECT name, type, address, whatsapp, city, notes, normalized_phone
        FROM health_centers
        WHERE normalized_phone = ?
          AND lower(city) = 'sÃ£o paulo'
        LIMIT 1
        """,
        (normalized,),
    ).fetchone()
    conn.close()

    if row is None:
        return LookupResponse(is_health=False, matched_phone=normalized)

    return LookupResponse(
        is_health=True,
        name=row["name"],
        type=row["type"],
        address=row["address"],
        whatsapp=row["whatsapp"],
        city=row["city"],
        notes=row["notes"],
        matched_phone=row["normalized_phone"],
    )