

```markdown
# 🎓 Grow with Gyan: Smart VTU & KCET College Advisor

> Bridging information deficits for rural Karnataka PUC Science graduates (such as Bidar, Kalaburagi, and Tumakuru) through transparent Return on Investment (ROI) metrics, cutoff analytics, and AI-powered counseling.

---

## 🏗️ System Architecture & Design

The platform uses a decoupled, serverless-first architecture optimized for zero-cost maintenance and lightning-fast cloud execution:

* **Frontend**: **Streamlit Cloud** — Handles user inputs (10th/PUC marks, KCET score, budget), presents interactive metrics, and renders Markdown-formatted AI counseling reports.
* **Backend**: **FastAPI on Modal** — A serverless ASGI application running inside a Linux container, handling rank estimation math, dataset lookup filtering, and Groq LLM agent coordination.
* **AI & Intelligence Engine**: **LangChain & Groq API** (`llama-3.3-70b-versatile` / `openai/gpt-oss-120b`) — Generates contextual, empathetic advisory strategies and option-entry warnings.

---

## 📊 System Flowchart

```text
 ┌──────────────────────┐         HTTP POST JSON         ┌─────────────────────────────────┐
 │                      │ ─────────────────────────────> │                                 │
 │  Streamlit Frontend  │                                │     Modal Serverless Backend    │
 │  (Streamlit Cloud)   │ <───────────────────────────── │       (FastAPI + Python)        │
 └──────────────────────┘       Structured JSON          └─────────────────────────────────>
                                                                          │
                                                           Reads Dataset & Estimates Rank
                                                                          │
                                                                          v
                                                         ┌─────────────────────────────────┐
                                                         │   Groq LPU Engine (LangChain)   │
                                                         │  - Generates Contextual Advice  │
                                                         └─────────────────────────────────┘

```

---

## 🚀 Step-by-Step Deployment Guide (VS Code Terminal)

Follow these exact commands in your local computer terminal to authenticate and deploy your serverless backend to Modal.

### Step 1: Install Modal CLI locally

```bash
pip install modal

```

### Step 2: Authenticate with your Modal Workspace

```bash
python -m modal setup

```

*(This command will trigger a web browser window to authenticate your Modal account and store your workspace token securely.)*

### Step 3: Register your Groq API Key as a Modal Secret

Store your secret securely in the Modal cloud container environment:

```bash
modal secret create groq-secret GROQ_API_KEY="your_groq_api_key_here"

```

### Step 4: Deploy the FastAPI Backend to Modal

Push your serverless application live:

```bash
modal deploy modal_backend.py

```

*Upon completion, Modal will print your live public webhook endpoint in the terminal (e.g., `https://<your-username>--grow-with-gyan-api-fastapi-app.us-east.modal.run`).*

### Step 5: Connect Streamlit Frontend

1. Copy your live Modal endpoint URL.
2. Go to your **Streamlit Cloud Dashboard** -> **Settings** -> **Secrets**.
3. Add or update your config keys:
```toml
GROQ_API_KEY = "your_groq_api_key_here"
MODAL_API_URL = "[https://your-modal-url.us-east.modal.run/api/v1/recommend](https://your-modal-url.us-east.modal.run/api/v1/recommend)"

```


4. Save and reboot your app.

---

## 🛠️ Troubleshooting & Challenges Faced (Post-Mortem Log)

During development and cloud deployment, several technical bottlenecks were encountered and systematically resolved:

### 1. Local Python Missing `fastapi` Import Error

* **Issue**: Running `modal deploy modal_backend.py` threw a local `ModuleNotFoundError: No module named 'fastapi'` because Modal inspects code execution locally before containerizing.
* **Resolution**: Installed the essential local dependency layer in the local virtual environment (`pip install fastapi pydantic pandas openpyxl langchain langchain-core langchain-groq`) so the CLI parser could read the decorators cleanly.

### 2. Serverless 500 Internal Server Error & Traceback Diagnostics

* **Issue**: The Streamlit client threw a `500 Server Error` when pinging the Modal webhook endpoint, but the serverless container hid the exact Python traceback.
* **Resolution**: Wrapped the core FastAPI endpoint logic inside a robust `try...except` block using Python's `traceback` package to pipe server-side exceptions directly into the container logs:
```python
except Exception as e:
    error_trace = traceback.format_exc()
    print("--- SERVER ERROR TRACEBACK ---\n", error_trace)
    raise HTTPException(status_code=500, detail=str(e))

```


Viewing these logs via `modal app logs grow-with-gyan-api` immediately exposed subsequent runtime faults.

### 3. Groq Model Deprecation / 404 Not Found Errors

* **Issue**: The server logs revealed a `groq.NotFoundError` (HTTP 404) stating that the target model identifier did not exist or was unavailable on the active plan tier.
* **Resolution**: Audited active production identifiers against Groq's documentation and updated the model string to an active tier-supported model (`openai/gpt-oss-120b` or standard Llama variants), completely resolving communication blocks.

---

## 📦 Project File Structure

```text
phase1/
├── modal_backend.py       # FastAPI backend container definition & rank logic
├── streamlit_app.py       # User interface layout & HTTP client
├── requirements.txt       # Streamlit Cloud python dependencies
└── README.md              # Full system documentation & deployment guide

```

```

```
