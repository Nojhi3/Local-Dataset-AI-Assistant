import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
REQUEST_TIMEOUT = 30

st.set_page_config(page_title="Local Dataset AI Assistant", page_icon=":books:")
st.title("Local Dataset AI Assistant")
st.caption("Upload CSV/JSON and chat over your local data.")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "selected_dataset_id" not in st.session_state:
    st.session_state["selected_dataset_id"] = "(latest)"


def _safe_get(path: str, timeout: int = REQUEST_TIMEOUT) -> tuple[bool, dict]:
    try:
        response = requests.get(f"{BACKEND_URL}{path}", timeout=timeout)
    except requests.RequestException as exc:
        return False, {"error": f"Network error: {exc}"}
    if not response.ok:
        return False, {"error": f"Request failed ({response.status_code}): {response.text}"}
    return True, response.json()


def _safe_post(path: str, json: dict | None = None, files: dict | None = None, timeout: int = REQUEST_TIMEOUT) -> tuple[bool, dict]:
    try:
        response = requests.post(
            f"{BACKEND_URL}{path}",
            json=json,
            files=files,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        return False, {"error": f"Network error: {exc}"}
    if not response.ok:
        return False, {"error": f"Request failed ({response.status_code}): {response.text}"}
    return True, response.json()


backend_ok, health_payload = _safe_get("/health")
if backend_ok:
    st.success("Backend connected.")
else:
    st.error(f"Backend unavailable at {BACKEND_URL}. {health_payload['error']}")

st.subheader("1) Upload Dataset")
uploaded_file = st.file_uploader("Choose CSV or JSON", type=["csv", "json"])

if uploaded_file is not None:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    if st.button("Upload"):
        with st.spinner("Uploading and indexing dataset..."):
            ok, payload = _safe_post("/api/upload", files=files, timeout=60)
        if ok:
            st.success("Uploaded successfully")
            st.session_state["dataset_id"] = payload.get("dataset_id")
            st.session_state["selected_dataset_id"] = payload.get("dataset_id", "(latest)")
            st.json(payload)
            st.rerun()
        else:
            st.error(payload["error"])

st.subheader("2) Ask Questions")
question = st.text_input("Question")

datasets_ok, datasets_payload = _safe_get("/api/datasets")
datasets = datasets_payload.get("datasets", []) if datasets_ok else []
dataset_options = ["(latest)"] + [item["id"] for item in datasets]

if st.session_state["selected_dataset_id"] not in dataset_options:
    st.session_state["selected_dataset_id"] = "(latest)"

selected = st.selectbox(
    "Dataset",
    dataset_options,
    index=dataset_options.index(st.session_state["selected_dataset_id"]),
)
st.session_state["selected_dataset_id"] = selected
dataset_id = None if selected == "(latest)" else selected

if datasets:
    selected_name = next((item["name"] for item in datasets if item["id"] == dataset_id), None)
    if selected_name:
        st.caption(f"Selected dataset: {selected_name}")
elif not datasets_ok:
    st.warning(f"Could not fetch datasets. {datasets_payload['error']}")

if st.button("Ask"):
    if not question.strip():
        st.warning("Enter a question first.")
        st.stop()
    payload = {"question": question, "dataset_id": dataset_id or None}
    with st.spinner("Thinking over uploaded data..."):
        ok, response_payload = _safe_post("/api/chat", json=payload, timeout=120)
    if ok:
        answer = response_payload.get("answer", "No answer returned")
        st.session_state["chat_history"].append(
            {
                "question": question,
                "answer": answer,
                "dataset_id": response_payload.get("dataset_id"),
                "sources": response_payload.get("sources", []),
            }
        )
        st.write(answer)
        st.json(response_payload)
    else:
        st.error(response_payload["error"])

st.subheader("3) Chat History")
if not st.session_state["chat_history"]:
    st.caption("No chat yet.")
else:
    for idx, item in enumerate(reversed(st.session_state["chat_history"]), start=1):
        st.markdown(f"**Q{idx}:** {item['question']}")
        st.markdown(f"**A{idx}:** {item['answer']}")
        st.caption(f"Dataset: {item.get('dataset_id')}, Sources: {item.get('sources')}")
        st.divider()

if st.button("Clear Chat History"):
    st.session_state["chat_history"] = []
    st.rerun()
