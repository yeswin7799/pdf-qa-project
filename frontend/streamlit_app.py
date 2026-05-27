import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="PDF Q&A", page_icon="📄")
st.title("📄 PDF Question & Answer")
st.caption("Upload a PDF, then ask questions about it.")

# ── Section 1: PDF Upload ──────────────────────────────────────
st.header("Step 1 — Upload a PDF")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    if st.button("Ingest PDF"):
        with st.spinner("Uploading and processing..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/ingest",
                    files={"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                )
                if response.status_code == 200:
                    st.success("PDF ingested successfully!")
                    st.session_state["pdf_ready"] = True
                else:
                    st.error(f"Ingestion failed: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach the backend. Is FastAPI running on port 8000?")
                
# ── Section 2: Question & Answer ──────────────────────────────
st.header("Step 2 — Ask a Question")

# Initialize chat history once
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Only show question input if a PDF has been ingested
if st.session_state.get("pdf_ready"):

    question = st.text_input("Type your question here")

    if st.button("Ask"):
        if question.strip() == "":
            st.warning("Please enter a question before clicking Ask.")
        else:
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/ask",
                        json={"question": question}
                    )
                    if response.status_code == 200:
                        answer = response.json().get("answer", "No answer returned.")
                        st.session_state["chat_history"].append({
                            "question": question,
                            "answer": answer
                        })
                    else:
                        st.error(f"Error: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot reach the backend. Is FastAPI running on port 8000?")

    # Render chat history — newest first
    if st.session_state["chat_history"]:
        st.divider()
        st.subheader("Chat History")
        for entry in reversed(st.session_state["chat_history"]):
            st.markdown(f"**You:** {entry['question']}")
            st.markdown(f"**Answer:** {entry['answer']}")
            st.divider()

else:
    st.info("Upload and ingest a PDF first to enable questions.")