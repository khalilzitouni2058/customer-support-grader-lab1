import hashlib
import hmac

import streamlit as st

AUTHENTICATED_KEY = "authenticated"
ANNOTATOR_ID_KEY = "annotator_id"


def hash_pin(pin: str) -> str:
    """Return the SHA-256 hash for a PIN."""
    return hashlib.sha256(pin.encode("utf-8")).hexdigest()


def _pin_hashes() -> dict:
    try:
        return dict(st.secrets.get("PIN_HASHES", {}))
    except Exception:
        return {}


def verify_pin_hash(pin: str, expected_hash: str | None) -> bool:
    if not expected_hash:
        return False
    return hmac.compare_digest(hash_pin(pin), str(expected_hash).strip())


def verify_pin(annotator_id: str, pin: str) -> bool:
    expected_hash = _pin_hashes().get(annotator_id)
    return verify_pin_hash(pin, expected_hash)


def init_auth_state() -> None:
    st.session_state.setdefault(AUTHENTICATED_KEY, False)
    st.session_state.setdefault(ANNOTATOR_ID_KEY, None)


def logout() -> None:
    st.session_state[AUTHENTICATED_KEY] = False
    st.session_state[ANNOTATOR_ID_KEY] = None


def login_required(members: list[dict]) -> str:
    init_auth_state()

    member_ids = {member["id"] for member in members}
    annotator_id = st.session_state.get(ANNOTATOR_ID_KEY)
    if st.session_state.get(AUTHENTICATED_KEY) and annotator_id in member_ids:
        return annotator_id

    if st.session_state.get(AUTHENTICATED_KEY):
        logout()

    st.title("Customer Support Annotation")
    st.caption("Human Annotation Platform")

    member_labels = {f'{member["id"]} - {member["name"]}': member["id"] for member in members}

    with st.form("login-form"):
        selected_member = st.selectbox("Annotator", list(member_labels.keys()))
        pin = st.text_input("PIN", type="password")
        submitted = st.form_submit_button("Login", type="primary")

    if submitted:
        selected_id = member_labels[selected_member]
        if verify_pin(selected_id, pin):
            st.session_state[AUTHENTICATED_KEY] = True
            st.session_state[ANNOTATOR_ID_KEY] = selected_id
            st.rerun()
        else:
            st.error("Incorrect PIN.")

    st.stop()
