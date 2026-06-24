from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
import os
import shutil
import fitz  # PyMuPDF
import numpy as np
import faiss
import json
import requests
from fastapi.middleware.cors import CORSMiddleware
import re
from docx import Document
from fastapi.concurrency import run_in_threadpool

# ---------- Setup ----------

load_dotenv(find_dotenv())

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("❌ GROQ_API_KEY not found. Check your .env file.")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Lazy-load both heavy models — load ONLY on first request
_model = None
_nlp = None

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            _nlp = False  # Mark as failed so we don't retry
    return _nlp if _nlp else None

app = FastAPI()

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vericlaim-ai.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Utilities ----------

def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def extract_clauses_from_pdf(text: str) -> list[str]:
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    clauses = [
        clause.strip()
        for clause in cleaned_text.split(".")
        if len(clause.strip()) > 20
    ]
    return clauses


def parse_and_enhance_query(user_query: str) -> str:
    nlp = get_nlp()  # Lazy load only when needed
    if not nlp:
        return user_query

    doc = nlp(user_query)
    keywords = []

    for token in doc:
        if token.ent_type_ in ['DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL']:
            keywords.append(token.text)
        elif token.ent_type_ in ['GPE', 'LOC']:
            keywords.append(token.text)
        elif token.pos_ in ['NOUN', 'PROPN', 'ADJ']:
            keywords.append(token.lemma_)

    enhanced_query = " ".join(keywords)
    return enhanced_query if enhanced_query else user_query


def process_claim(user_query: str, clause: str):
    prompt = f"""
You are an insurance claim analyst. Based on the user query and clause, decide the claim outcome.

Query: {user_query}

Clause: {clause}

Analyze if the claim should be approved or rejected based on the clause conditions. Return only a JSON response with these exact fields:
- decision: "Approved" or "Rejected"
- amount: estimated amount like "₹50000" or "N/A" if rejected
- justification: brief explanation based on the clause

Response:
"""

    try:
        response = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            },
            timeout=60
        )

        result = response.json()

        if "choices" not in result or not result["choices"]:
            return {"error": "Unexpected response from Groq", "raw": result}

        content = result["choices"][0]["message"]["content"]
        json_start = content.find("{")
        json_end = content.rfind("}") + 1

        if json_start != -1 and json_end != -1:
            return json.loads(content[json_start:json_end])

        return {"error": "Could not parse JSON", "raw": content}

    except Exception as e:
        return {"error": str(e)}


def build_faiss_and_search(clauses: list[str], query: str):
    """Encode clauses and search — done in one shot to minimize peak memory."""
    model = get_model()

    # Encode in small batches to reduce peak memory
    batch_size = 16
    all_embeddings = []
    for i in range(0, len(clauses), batch_size):
        batch = clauses[i:i + batch_size]
        embeddings = model.encode(batch, convert_to_numpy=True)
        all_embeddings.append(embeddings)

    clause_embeddings_np = np.vstack(all_embeddings).astype("float32")

    dimension = clause_embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(clause_embeddings_np)

    parsed_query = parse_and_enhance_query(query)
    query_embedding = model.encode([parsed_query], convert_to_numpy=True).astype("float32")

    distances, indices = index.search(query_embedding, min(5, len(clauses)))
    matched_clauses = [clauses[i] for i in indices[0]]

    # Free index memory immediately
    del index
    del clause_embeddings_np

    return matched_clauses

# ---------- Routes ----------

@app.get("/")
def root():
    return {"message": "Insurance Claim API running with Groq API for LLM."}


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), user_query: str = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    def process_pdf():
        text = extract_text_from_pdf(file_path)
        real_clauses = extract_clauses_from_pdf(text)

        if not real_clauses:
            raise HTTPException(status_code=400, detail="No valid clauses found in PDF.")

        # Cap clauses to top 100 to limit memory usage
        real_clauses = real_clauses[:100]

        matched_clauses = build_faiss_and_search(real_clauses, user_query)
        top_clauses = ', '.join(matched_clauses[:5])
        llm_result = process_claim(user_query, top_clauses)

        return {
            "matched_clauses": matched_clauses,
            "LLM_response": llm_result
        }

    result = await run_in_threadpool(process_pdf)

    return {
        "message": "File uploaded and processed successfully.",
        "user_query": user_query,
        "matched_clauses": result["matched_clauses"],
        "LLM_response": result["LLM_response"]
    }


@app.post("/upload-docs")
async def upload_doc(file: UploadFile = File(...), user_query: str = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        document = Document(file_path)
        text = "\n".join([para.text for para in document.paragraphs])
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read Word document.")

    def process_doc():
        real_clauses = extract_clauses_from_pdf(text)

        if not real_clauses:
            raise HTTPException(status_code=400, detail="No valid clauses found in Word document.")

        # Cap clauses to top 100 to limit memory usage
        real_clauses = real_clauses[:100]

        matched_clauses = build_faiss_and_search(real_clauses, user_query)
        top_clauses = ', '.join(matched_clauses[:5])
        llm_result = process_claim(user_query, top_clauses)

        return {
            "matched_clauses": matched_clauses,
            "LLM_response": llm_result
        }

    result = await run_in_threadpool(process_doc)

    return {
        "message": "Word document uploaded and processed successfully.",
        "user_query": user_query,
        "matched_clauses": result["matched_clauses"],
        "LLM_response": result["LLM_response"]
    }
