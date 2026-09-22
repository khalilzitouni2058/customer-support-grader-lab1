from pathlib import Path
import json
import sys

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from assignment import assigned_annotators
from auth import login_required, logout
from storage import get_annotation, load_annotations, save_annotation

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS_PATH = ROOT / "data" / "scenarios.jsonl"
TEAM_PATH = ROOT / "config" / "team.json"

CRITERIA = [
    ("correctness", "Correctness"),
    ("completeness", "Completeness"),
    ("policy_compliance", "Policy compliance"),
    ("politeness", "Politeness"),
    ("clarity", "Clarity"),
]
SCORE_OPTIONS = [0, 1, 2]
MEMBER_ITEM_RANGES = {
    "A": "1-75",
    "B": "1-25, 76-125",
    "C": "26-50, 76-100, 126-150",
    "D": "51-75, 101-150",
}


@st.cache_data(show_spinner=False)
def load_scenarios() -> list[dict]:
    if not SCENARIOS_PATH.exists():
        return []

    rows = []
    with SCENARIOS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


@st.cache_data(show_spinner=False)
def load_team() -> list[dict]:
    if not TEAM_PATH.exists():
        return [
            {"id": "A", "name": "Member A"},
            {"id": "B", "name": "Member B"},
            {"id": "C", "name": "Member C"},
            {"id": "D", "name": "Member D"},
        ]
    return json.loads(TEAM_PATH.read_text(encoding="utf-8"))["members"]


def assigned_for_member(scenarios: list[dict], annotator_id: str) -> list[dict]:
    return [
        scenario
        for scenario in scenarios
        if annotator_id in assigned_annotators(int(scenario["id"]))
    ]


def completed_ids(annotations: pd.DataFrame, annotator_id: str, assigned_ids: set[int]) -> set[int]:
    if annotations.empty:
        return set()

    rows = annotations[
        (annotations["annotator_id"] == annotator_id)
        & (annotations["item_id"].astype(int).isin(assigned_ids))
    ]
    return set(rows["item_id"].astype(int).tolist())


def expected_assignments() -> pd.DataFrame:
    rows = []
    for item_id in range(1, 151):
        for annotator_id in assigned_annotators(item_id):
            rows.append({"item_id": item_id, "annotator_id": annotator_id})
    return pd.DataFrame(rows)


def progress_table(members: list[dict], annotations: pd.DataFrame) -> pd.DataFrame:
    expected = expected_assignments()

    if annotations.empty:
        valid_annotations = pd.DataFrame(columns=["item_id", "annotator_id"])
    else:
        df = annotations.copy()
        df["item_id"] = df["item_id"].astype(int)
        valid_annotations = df.merge(expected, on=["item_id", "annotator_id"], how="inner")

    rows = []
    for member in members:
        assigned = int((expected["annotator_id"] == member["id"]).sum())
        completed = int(
            valid_annotations.loc[
                valid_annotations["annotator_id"] == member["id"],
                "item_id",
            ].nunique()
        )
        remaining = assigned - completed
        rows.append(
            {
                "Annotator": f'{member["id"]} - {member["name"]}',
                "Completed": completed,
                "Assigned": assigned,
                "Remaining": remaining,
                "Percent": f"{completed / assigned:.0%}" if assigned else "0%",
            }
        )
    return pd.DataFrame(rows)


def fully_annotated_count(annotations: pd.DataFrame) -> int:
    if annotations.empty:
        return 0

    expected = expected_assignments()
    df = annotations.copy()
    df["item_id"] = df["item_id"].astype(int)
    valid_annotations = df.merge(expected, on=["item_id", "annotator_id"], how="inner")
    per_item = valid_annotations.groupby("item_id")["annotator_id"].nunique()
    return int((per_item >= 2).sum())


def score_control(field: str, label: str, item_id: int, existing: dict) -> int | None:
    default = existing.get(field)
    if default is not None and not pd.isna(default):
        default = int(default)

    return st.segmented_control(
        label,
        SCORE_OPTIONS,
        default=default,
        format_func=lambda score: str(score),
        key=f"{field}-{item_id}",
        width="stretch",
    )


st.set_page_config(page_title="NovaCart annotation", layout="wide")

members = load_team()
annotator_id = login_required(members)
member_by_id = {member["id"]: member for member in members}
current_member = member_by_id.get(annotator_id, {"id": annotator_id, "name": annotator_id})
current_member_label = f'{current_member["id"]} - {current_member["name"]}'

st.title("NovaCart annotation")

scenarios = load_scenarios()

if not scenarios:
    st.error("No scenarios found in data/scenarios.jsonl.")
    st.stop()

with st.sidebar:
    st.caption("Logged in as")
    st.write(current_member_label)
    if st.button("Logout", type="secondary"):
        logout()
        st.rerun()

    st.caption(f"Assigned items: {MEMBER_ITEM_RANGES.get(annotator_id, '')}")
    view = st.segmented_control(
        "View",
        ["Annotate", "Progress", "Export"],
        default="Annotate",
        width="stretch",
    )

assigned_items = assigned_for_member(scenarios, annotator_id)
assigned_ids = {int(item["id"]) for item in assigned_items}
annotations = load_annotations()
done_ids = completed_ids(annotations, annotator_id, assigned_ids)
remaining_count = len(assigned_items) - len(done_ids)

with st.sidebar:
    st.metric("Assigned", len(assigned_items))
    st.metric("Completed", len(done_ids))
    st.metric("Remaining", remaining_count)
    if assigned_items:
        st.progress(len(done_ids) / len(assigned_items))

if view == "Annotate":
    unfinished_items = [
        item
        for item in assigned_items
        if int(item["id"]) not in done_ids
    ]

    if not unfinished_items:
        st.success("All assigned items are complete.")
        st.stop()

    item = unfinished_items[0]
    selected_id = int(item["id"])
    current_position = len(done_ids) + 1
    st.caption(
        f"{current_member_label} | Item {current_position} of {len(assigned_items)} "
        f"| {remaining_count} remaining"
    )
    item = next(scenario for scenario in scenarios if int(scenario["id"]) == selected_id)
    existing = get_annotation(selected_id, annotator_id) or {}

    top_cols = st.columns([1, 1], gap="medium")
    with top_cols[0]:
        with st.container(border=True):
            st.subheader(f"Item {selected_id}")
            st.caption(item["category"])
            st.markdown("**Customer message**")
            st.write(item["customer_message"])
            st.markdown("**Relevant policy**")
            st.write(item["policy"])

    with top_cols[1]:
        with st.container(border=True):
            st.subheader("Candidate reply")
            st.write(item["candidate_reply"])

    st.divider()
    st.subheader("Rate this reply")
    st.caption("0 = poor or violated, 1 = partially satisfied, 2 = fully satisfied.")

    with st.form(f"annotation-{selected_id}-{annotator_id}", border=False):
        score_cols = st.columns(5)
        scores = {}
        for col, (field, label) in zip(score_cols, CRITERIA):
            with col:
                scores[field] = score_control(field, label, selected_id, existing)

        all_scored = all(score is not None for score in scores.values())
        total_score = sum(int(score) for score in scores.values() if score is not None)
        st.metric("Total score", f"{total_score}/10" if all_scored else "Select all scores")

        explanation = st.text_area(
            "Short explanation of the rating",
            value=str(existing.get("reason", "") or ""),
            max_chars=600,
            placeholder="Briefly explain the main reason for your scores.",
        )

        submitted = st.form_submit_button("Submit annotation and load next item", type="primary")

        if submitted:
            if not all_scored:
                st.error("Please select a score for all five criteria.")
            elif not explanation.strip():
                st.error("Please add a short explanation for the rating.")
            else:
                record = {
                    "item_id": selected_id,
                    "annotator_id": annotator_id,
                    "correctness": int(scores["correctness"]),
                    "completeness": int(scores["completeness"]),
                    "policy_compliance": int(scores["policy_compliance"]),
                    "politeness": int(scores["politeness"]),
                    "clarity": int(scores["clarity"]),
                    "total_score": total_score,
                    "reason": explanation.strip(),
                }
                save_annotation(record)
                st.success("Annotation saved.")
                st.rerun()

elif view == "Progress":
    st.subheader("Progress")
    progress = progress_table(members, annotations)
    st.dataframe(progress, hide_index=True)
    st.metric("Items with both human annotations", f"{fully_annotated_count(annotations)}/150")

elif view == "Export":
    st.subheader("Export annotations")

    if annotations.empty:
        st.info("No annotations have been saved yet.")
    else:
        st.dataframe(annotations, hide_index=True)
        st.download_button(
            "Download annotations.csv",
            data=annotations.to_csv(index=False).encode("utf-8"),
            file_name="annotations.csv",
            mime="text/csv",
        )
