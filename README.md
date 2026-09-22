# Customer Support Grader

Project 1 — CS496 AI Engineering

This repository is the starting point for an evaluation harness for customer-support reply generation.

## What is already included

- A Streamlit annotation UI
- Balanced 4-person assignment: 75 items per annotator, 2 annotators per item
- Local SQLite storage for development
- Optional Supabase storage for shared online annotation
- Progress dashboard
- CSV export of collected annotations
- JSONL schema for scenarios
- Placeholder folders for the later evaluation harness, prompts, results, and report artifacts

## Dataset design

Each scenario should contain:

- `id`
- `category`
- `customer_message`
- `policy`
- `candidate_reply`

The final dataset contains 150 NovaCart customer-support scenarios. The master
policy is stored in `data/company_policy.md`, and each JSONL row includes only
the policy excerpt relevant to that scenario.

Annotators score the same candidate reply on:

- Correctness: 0–2
- Completeness: 0–2
- Policy compliance: 0–2
- Politeness: 0–2
- Clarity: 0–2
- Short reason / note

Maximum score: 10.

## Balanced annotation assignment

For exactly 150 items:

| Items | Annotators |
|---|---|
| 1–25 | A + B |
| 26–50 | A + C |
| 51–75 | A + D |
| 76–100 | B + C |
| 101–125 | B + D |
| 126–150 | C + D |

Each annotator receives exactly 75 items.

## Local setup

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
streamlit run app/main.py
```

The app requires PIN hashes in `.streamlit/secrets.toml`. If Supabase settings
are blank, annotations are saved to the local SQLite database at
`data/annotations.db`.

## PIN login

Member names are stored in:

```text
config/team.json
```

PINs are not stored in `team.json`, source code, or the database. Store only
SHA-256 PIN hashes in Streamlit secrets.

Generate a hash for each member's PIN:

```bash
python scripts/generate_pin_hash.py 1234
```

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and replace
the placeholder hashes:

```toml
SUPABASE_URL = ""
SUPABASE_KEY = ""

[PIN_HASHES]
A = "SHA256_HASH_FOR_MEMBER_A_PIN"
B = "SHA256_HASH_FOR_MEMBER_B_PIN"
C = "SHA256_HASH_FOR_MEMBER_C_PIN"
D = "SHA256_HASH_FOR_MEMBER_D_PIN"
```

Do not commit `.streamlit/secrets.toml`.

## Shared online annotation

For teammates to annotate from different computers, use the Supabase backend.

1. Create a free Supabase project.
2. Open the SQL editor.
3. Run the SQL in `docs/supabase.sql`.
4. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
5. Add your Supabase URL, Supabase key, and `[PIN_HASHES]`.
6. Deploy the repository to Streamlit Community Cloud or another host.
7. Add the same secrets in the deployment settings.
8. Share the deployed URL with your teammates.

Do **not** commit `.streamlit/secrets.toml`.

## Replace member names

Edit:

`config/team.json`

You can keep IDs A/B/C/D while changing the displayed names.

## Add scenarios

Edit:

`data/scenarios.jsonl`

The current file contains the final 150-item NovaCart dataset. If you revise it,
run:

```bash
python scripts/validate_scenarios.py
```

## Later project structure

```text
customer-support-grader/
├── app/
├── config/
├── data/
├── docs/
├── harness/
├── prompts/
├── results/
├── scripts/
├── README.md
├── requirements.txt
└── .gitignore
```

The later harness can be added under `harness/` without changing the annotation UI.
