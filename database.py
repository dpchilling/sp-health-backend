from __future__ import annotations
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "sp_health_centers_sao_paulo.sqlite"
CSV_PATH = DATA_DIR / "sp_health_centers_sao_paulo.csv"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn