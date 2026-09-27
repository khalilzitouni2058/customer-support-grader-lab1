from pathlib import Path
import json
import pandas as pd

ANNOTATIONS_PATH = Path(__file__).resolve().parents[1] / "data" / "annotations.json"


def _read_records() -> list[dict]:
    ANNOTATIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not ANNOTATIONS_PATH.exists():
        return []
    with ANNOTATIONS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def _write_records(records: list[dict]) -> None:
    temporary_path = ANNOTATIONS_PATH.with_suffix(".tmp")
    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)
        file.write("\n")
    temporary_path.replace(ANNOTATIONS_PATH)


def save_annotation(record: dict):
    records = _read_records()
    key = (int(record["item_id"]), record["annotator_id"])
    updated = {
        **record,
        "item_id": key[0],
        "updated_at": pd.Timestamp.utcnow().isoformat(),
    }
    records = [
        existing
        for existing in records
        if (int(existing["item_id"]), existing["annotator_id"]) != key
    ]
    records.append(updated)
    records.sort(key=lambda item: (int(item["item_id"]), item["annotator_id"]))
    _write_records(records)


def load_annotations() -> pd.DataFrame:
    return pd.DataFrame(_read_records())


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
