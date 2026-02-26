import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(page_title="Local Dataset AI Assistant", page_icon=":books:")
st.title("Local Dataset AI Assistant")
st.caption("Upload CSV/JSON and chat over your local data.")

st.subheader("1) Upload Dataset")
uploaded_file = st.file_uploader("Choose CSV or JSON", type=["csv", "json"])

if uploaded_file is not None:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    if st.button("Upload"):
        response = requests.post(f"{BACKEND_URL}/api/upload", files=files, timeout=60)
        if response.ok:
            st.success("Uploaded successfully")
            payload = response.json()
            st.session_state["dataset_id"] = payload.get("dataset_id")
            st.json(payload)
        else:
            st.error(f"Upload failed: {response.status_code}")
            st.text(response.text)

st.subheader("2) Ask Questions")
question = st.text_input("Question")

datasets_response = requests.get(f"{BACKEND_URL}/api/datasets", timeout=30)
datasets = datasets_response.json().get("datasets", []) if datasets_response.ok else []
dataset_options = ["(latest)"] + [f"{item['id']} | {item['name']}" for item in datasets]
selected = st.selectbox("Dataset", dataset_options, index=0)
dataset_id = None if selected == "(latest)" else selected.split(" | ")[0]

if st.button("Ask"):
    payload = {"question": question, "dataset_id": dataset_id or None}
    response = requests.post(f"{BACKEND_URL}/api/chat", json=payload, timeout=120)
    if response.ok:
        st.write(response.json().get("answer", "No answer returned"))
        st.json(response.json())
    else:
        st.error(f"Chat failed: {response.status_code}")
        st.text(response.text)
