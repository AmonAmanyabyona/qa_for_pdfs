# SmartReader 📘
> An intelligent PDF chatbot — upload any PDF and ask questions about it in natural language.

![Python](https://img.shields.io/badge/Python-3.11-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green) ![LangChain](https://img.shields.io/badge/LangChain-0.2+-orange) ![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5+-red)

---

## What It Does

SmartReader lets you upload a PDF document and chat with it using natural language. It uses a RAG (Retrieval-Augmented Generation) pipeline to find the most relevant chunks of your document and answer your questions accurately — without making things up.

The UI is a floating chat widget on a single web page. No page reloads, no sidebar navigation, no frameworks — just a clean, modern chatbot interface served by FastAPI.

---

## How It Works (Architecture)

```
User uploads PDF
      ↓
FastAPI /upload endpoint
      ↓
PDF text extracted (PyPDF)
      ↓
Text embedded into vectors (OpenAI text-embedding-3-small)
      ↓
Vectors stored in ChromaDB (in memory, deleted on shutdown)
      ↓
User asks a question
      ↓
FastAPI /chat endpoint
      ↓
Question embedded → similar chunks retrieved from ChromaDB
      ↓
Chunks + question sent to GPT-4o as context
      ↓
Answer returned to user
```

---

## Project Structure

```
qa_for_pdfs/
├── main.py                 ← FastAPI app: routes, startup, shutdown
├── rag.py                  ← RAG pipeline: retrieval + prompt + GPT call
├── pdf_loader.py           ← Loads and parses PDF into LangChain documents
├── embedding.py            ← OpenAI embedding function
├── vectorstore.py          ← ChromaDB create and load functions
├── retriever.py            ← Wraps vectorstore as a retriever
├── formatter.py            ← Formats retrieved docs into plain text
├── chat_complettion.py     ← OpenAI GPT-4o chat completion call
├── config.py               ← Loads OPENAI_API_KEY from .env
├── static/
│   ├── index.html          ← Single page UI with floating chat widget
│   ├── style.css           ← All widget and page styles
│   └── app.js              ← Upload + chat logic (fetch API calls)
├── uploaded_pdfs/          ← Temporary PDF storage (auto-deleted after embedding)
├── .env                    ← API keys (never committed)
├── .gitignore
└── requirements.txt
```

---

## File-by-File Breakdown

### `main.py`
The FastAPI application. Handles three routes:
- `POST /upload` — receives a PDF, saves it temporarily, embeds it into ChromaDB, then deletes the file
- `POST /chat` — receives a question, runs the RAG pipeline, returns an answer
- `GET /status` — returns whether a PDF is loaded and its filename

Also manages app lifecycle: preloads the embedding model on startup and deletes the vectorstore on shutdown so no user data is retained.

### `rag.py`
The core RAG pipeline. Given a question and a retriever, it retrieves the most relevant document chunks, formats them into a prompt, and calls GPT-4o. The prompt instructs the model to answer strictly from the document — no inference, no hallucination. Also passes the previous answer for conversational context.

### `pdf_loader.py`
Uses LangChain's `PyPDFLoader` to load a PDF from disk and return a list of `Document` objects (one per page).

### `embedding.py`
Returns an OpenAI embedding function using `text-embedding-3-small`. This model converts text into numerical vectors used for similarity search.

### `vectorstore.py`
Two functions: `create_vectorstore` builds a new ChromaDB collection from document chunks, and `load_vectorstore` loads an existing one from disk using a path and embedding function.

### `retriever.py`
Wraps a ChromaDB vectorstore as a LangChain retriever using similarity search. `retrieve_chunks` runs a query and returns the most relevant document chunks.

### `formatter.py`
Takes a list of LangChain `Document` objects and joins their text content into a single plain-text string for use in the prompt.

### `chat_complettion.py`
Sends a prompt to GPT-4o via the OpenAI API and returns the text response. Uses `temperature=1` for natural answers.

### `config.py`
Loads the `OPENAI_API_KEY` from the `.env` file using `python-dotenv`. Raises an error if the key is missing.

### `static/index.html`
Single HTML page. Contains the hero landing section and the chat widget markup. The widget has a header, a scrollable message area, and a bottom input bar with a paperclip upload button built into it.

### `static/style.css`
All styles for the page and widget. Dark gradient background for the hero, floating blue FAB button, white chat widget with slide-up animation, and iMessage-style message bubbles.

### `static/app.js`
All frontend logic:
- Opens/closes the chat widget
- Handles PDF file selection and upload via `fetch POST /upload`
- Displays upload status below the input bar
- Sends chat messages via `fetch POST /chat`
- Renders message bubbles with timestamps
- Shows a typing indicator while waiting for a response

---

## Privacy

SmartReader does not store user data. Uploaded PDFs are deleted immediately after embedding. Vectorstores (which contain extracted text chunks) are deleted when the server shuts down. Nothing is written to a database.

---

## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/AmonAmanyabyona/qa_for_pdfs.git
cd qa_for_pdfs
```

### 2. Create and activate virtual environment
```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Run the app
```bash
uvicorn main:app --reload --port 8000
```

Wait for `✅ Embedding model ready!` in the terminal, then open:
```
http://127.0.0.1:8000
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Uvicorn |
| PDF Parsing | LangChain + PyPDF |
| Embeddings | OpenAI text-embedding-3-small |
| Vector Store | ChromaDB |
| LLM | GPT-4o via OpenAI API |
| Frontend | Vanilla HTML + CSS + JavaScript |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/upload` | Upload and embed a PDF |
| POST | `/chat` | Ask a question about the PDF |
| GET | `/status` | Check if a PDF is loaded |

---

## Cost Estimate (OpenAI API)

| Action | Model | Approximate Cost |
|---|---|---|
| Upload a 10-page PDF | text-embedding-3-small | ~$0.0001 |
| Ask a question | GPT-4o | ~$0.002 per question |
| 100 questions/day | GPT-4o | ~$0.20/day |

---

*Built with FastAPI, LangChain, ChromaDB, and the OpenAI API.*