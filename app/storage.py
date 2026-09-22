from pathlib import Path
import sqlite3
import pandas as pd

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "annotations.db"


def _get_supabase_client():
    try:
        import streamlit as st
        from supabase import create_client

        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None


def _ensure_sqlite():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS annotations (
                item_id INTEGER NOT NULL,
                annotator_id TEXT NOT NULL,
                correctness INTEGER NOT NULL,
                completeness INTEGER NOT NULL,
                policy_compliance INTEGER NOT NULL,
                politeness INTEGER NOT NULL,
                clarity INTEGER NOT NULL,
                total_score INTEGER NOT NULL,
                reason TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (item_id, annotator_id)
            )
            """
        )


def save_annotation(record: dict):
    client = _get_supabase_client()
    if client:
        client.table("annotations").upsert(
            record,
            on_conflict="item_id,annotator_id"
        ).execute()
        return

    _ensure_sqlite()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO annotations (
                item_id, annotator_id, correctness, completeness,
                policy_compliance, politeness, clarity, total_score, reason,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(item_id, annotator_id)
            DO UPDATE SET
                correctness=excluded.correctness,
                completeness=excluded.completeness,
                policy_compliance=excluded.policy_compliance,
                politeness=excluded.politeness,
                clarity=excluded.clarity,
                total_score=excluded.total_score,
                reason=excluded.reason,
                updated_at=CURRENT_TIMESTAMP
            """,
            (
                record["item_id"],
                record["annotator_id"],
                record["correctness"],
                record["completeness"],
                record["policy_compliance"],
                record["politeness"],
                record["clarity"],
                record["total_score"],
                record.get("reason", ""),
            )
        )


def load_annotations() -> pd.DataFrame:
    client = _get_supabase_client()
    if client:
        data = client.table("annotations").select("*").execute().data
        return pd.DataFrame(data)

    _ensure_sqlite()
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(
            "SELECT * FROM annotations ORDER BY item_id, annotator_id",
            conn
        )


def get_annotation(item_id: int, annotator_id: str):
    df = load_annotations()
    if df.empty:
        return None
    row = df[
        (df["item_id"] == item_id) &
        (df["annotator_id"] == annotator_id)
    ]
    if row.empty:
        return None
    return row.iloc[0].to_dict()
