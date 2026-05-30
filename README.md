# 📄 PDF Document Q&A System

A production-grade **Retrieval-Augmented Generation (RAG)** application that lets you upload any PDF and ask questions about it in natural language. Built with FastAPI, ChromaDB, Sentence Transformers, and OpenAI GPT - deployed on AWS ECS Fargate with a Streamlit frontend.

---

## 🏗️ Architecture

```
Browser (Streamlit UI)
        │
        ▼
FastAPI Backend (AWS ECS Fargate)
        │
        ├── AWS S3          → persistent PDF storage
        ├── ChromaDB        → vector store for semantic search
        ├── Sentence Transformers → local embeddings (all-MiniLM-L6-v2)
        └── OpenAI GPT-3.5  → answer generation
```

---

## ✨ Features

- **PDF Upload & Ingestion** - upload any PDF through the browser; text is extracted, chunked, embedded, and stored automatically
- **Semantic Search** - questions are matched to relevant document chunks using vector similarity, not keyword search
- **Local Embeddings** - uses `sentence-transformers` (free, offline) instead of paid embedding APIs
- **Input Guardrails** - two-layer protection against prompt injection and off-topic questions
- **Structured Logging** - every request and error is logged to AWS CloudWatch with key-value structured format
- **Automated CI/CD** - every `git push` to `main` builds, pushes, and deploys automatically via GitHub Actions

---

## 🗂️ Project Structure

```
pdf-qa-project/
├── app/
│   ├── ingest.py          # PDF extraction, chunking, embedding, S3 + ChromaDB storage
│   ├── retrieve.py        # semantic search against ChromaDB
│   ├── generate.py        # prompt engineering + OpenAI GPT call
│   └── guardrails.py      # input validation and injection detection
├── frontend/
│   ├── streamlit_app.py   # Streamlit UI
│   └── requirements.txt   # frontend dependencies
├── main.py                # FastAPI app with /ingest and /ask endpoints
├── Dockerfile             # container definition
├── requirements.txt       # backend dependencies
└── .github/
    └── workflows/
        └── deploy.yml     # GitHub Actions CI/CD pipeline
```

---

## 🚀 How It Works

### Phase 1 - Ingestion
1. User uploads a PDF through the Streamlit UI
2. FastAPI receives the file and calls `ingest()`
3. PDF text is extracted using `pypdf`
4. Text is split into 500-character overlapping chunks via LangChain's `RecursiveCharacterTextSplitter`
5. Each chunk is embedded using `all-MiniLM-L6-v2` from `sentence-transformers`
6. Chunks + embeddings are stored in ChromaDB
7. The PDF file is uploaded to AWS S3 for persistent storage

### Phase 2 - Question Answering
1. User types a question in the Streamlit UI
2. Input is validated by the guardrails layer (length check, injection detection)
3. The question is embedded using the same model
4. ChromaDB finds the most semantically similar chunks
5. Chunks are assembled into a context string
6. GPT-3.5-turbo generates an answer strictly based on that context
7. Answer is returned and displayed in the UI

---

## 🛡️ Guardrails

The app implements a two-layer defense system:

**Layer 1 - Python Validation (fast, free)**
- Rejects questions that are too short (< 5 chars) or too long (> 500 chars)
- Detects prompt injection keywords (`ignore previous instructions`, `act as`, `jailbreak`, etc.)

**Layer 2 - System Prompt Hardening**
- LLM is instructed to only answer from the provided document context
- Explicitly told to reject off-topic questions and behavioral override attempts

---

## ☁️ AWS Infrastructure

| Service | Purpose |
|---|---|
| ECS Fargate | Runs the FastAPI container - serverless, no VM management |
| ECR | Stores Docker images |
| S3 | Persistent PDF file storage |
| CloudWatch | Structured log collection with 7-day retention |
| IAM | Scoped deployment permissions for GitHub Actions |

---

## ⚙️ CI/CD Pipeline

Every push to `main` triggers the GitHub Actions workflow:

```
git push → GitHub Actions
              ├── Configure AWS credentials
              ├── docker build
              ├── docker push → ECR
              └── aws ecs update-service → deploys new image
```

---

## 🛠️ Local Setup

### Prerequisites
- Python 3.10+
- Docker
- AWS CLI configured
- OpenAI API key

### 1. Clone the repo
```bash
git clone https://github.com/yeswin7799/pdf-qa-project.git
cd pdf-qa-project
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
pip install -r frontend/requirements.txt
```

### 4. Set environment variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your_s3_bucket_name
```

### 5. Run FastAPI backend
```bash
uvicorn main:app --reload --port 8000
```

### 6. Run Streamlit frontend (new terminal)
```bash
streamlit run frontend/streamlit_app.py
```

Open `http://localhost:8501` in your browser.

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI |
| Frontend UI | Streamlit |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector Store | ChromaDB |
| LLM | OpenAI GPT-3.5-turbo |
| PDF Parsing | pypdf |
| Text Splitting | LangChain RecursiveCharacterTextSplitter |
| File Storage | AWS S3 + boto3 |
| Containerization | Docker |
| Container Registry | AWS ECR |
| Deployment | AWS ECS Fargate |
| Monitoring | AWS CloudWatch |
| CI/CD | GitHub Actions |

---

## 📝 API Endpoints

### `POST /ingest`
Upload and process a PDF file.

**Request:** `multipart/form-data` with field `file` (PDF)

**Response:**
```json
{ "message": "Successfully ingested filename.pdf" }
```

### `POST /ask`
Ask a question about the ingested document.

**Request:**
```json
{ "question": "What are this person's skills?" }
```

**Response:**
```json
{ "answer": "The document mentions skills in Python, FastAPI, and AWS." }
```

---

## 🔒 Security Notes

- AWS credentials are stored as GitHub Secrets - never hardcoded
- `.env` file is in `.gitignore` - never committed
- IAM user has minimum required permissions only
- Input guardrails prevent prompt injection attacks

---

## 👤 Author

**Yeswin Chintapalli**
- Portfolio: [yeswinchintapalli.netlify.app](https://yeswinchintapalli.netlify.app)
- LinkedIn: [yeswinchintapalli](https://www.linkedin.com/in/yeswinchintapalli/)
- Email: chiny02@purdue.edu
