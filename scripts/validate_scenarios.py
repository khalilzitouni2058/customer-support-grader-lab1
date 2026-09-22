import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "scenarios.jsonl"

REQUIRED_FIELDS = {"id", "category", "customer_message", "policy", "candidate_reply"}
CATEGORY_RANGES = {
    "returns_refunds": range(1, 26),
    "damaged_wrong_items": range(26, 51),
    "shipping_delivery": range(51, 76),
    "billing_subscriptions": range(76, 101),
    "account_access": range(101, 126),
    "orders_products": range(126, 151),
}
APPROVED_CATEGORIES = set(CATEGORY_RANGES)


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


items = []
try:
    with PATH.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                fail(f"Line {line_no}: invalid JSON: {exc}")

            missing = REQUIRED_FIELDS - set(item)
            extra = set(item) - REQUIRED_FIELDS
            if missing:
                fail(f"Line {line_no}: missing fields {sorted(missing)}")
            if extra:
                fail(f"Line {line_no}: unexpected fields {sorted(extra)}")

            for field in REQUIRED_FIELDS:
                value = item[field]
                if value is None or str(value).strip() == "":
                    fail(f"Line {line_no}: field '{field}' is empty")

            if not isinstance(item["id"], int):
                fail(f"Line {line_no}: id must be an integer")

            category = item["category"]
            if category not in APPROVED_CATEGORIES:
                fail(f"Line {line_no}: category '{category}' is not approved")

            if item["id"] not in CATEGORY_RANGES[category]:
                fail(
                    f"Line {line_no}: id {item['id']} is outside the "
                    f"required range for {category}"
                )

            items.append(item)
except FileNotFoundError:
    fail(f"Scenario file not found: {PATH}")

ids = [int(x["id"]) for x in items]

if len(ids) != len(set(ids)):
    duplicates = sorted([item_id for item_id, count in Counter(ids).items() if count > 1])
    fail(f"Duplicate scenario IDs found: {duplicates}")

expected_ids = list(range(1, 151))
if sorted(ids) != expected_ids:
    missing = sorted(set(expected_ids) - set(ids))
    unexpected = sorted(set(ids) - set(expected_ids))
    fail(f"IDs must be exactly 1-150. Missing={missing}; unexpected={unexpected}")

counts = Counter(item["category"] for item in items)
for category in CATEGORY_RANGES:
    if counts[category] != 25:
        fail(f"Category '{category}' has {counts[category]} items; expected 25")

if len(items) != 150:
    fail(f"Expected 150 scenarios; found {len(items)}")

customer_messages = [item["customer_message"] for item in items]
candidate_replies = [item["candidate_reply"] for item in items]
if len(customer_messages) != len(set(customer_messages)):
    fail("Exact duplicate customer messages found")
if len(candidate_replies) != len(set(candidate_replies)):
    fail("Exact duplicate candidate replies found")

print(f"Total scenarios: {len(items)}")
for category in CATEGORY_RANGES:
    print(f"{category}: {counts[category]}")
print("Validation passed.")
