from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os

# -------- ML Imports --------
from backend.ml.embeddings.clause_embedder import ClauseMapper
from backend.ml.embeddings.vector_store import DecisionEngine
from backend.ml.fraud.fraud_detection import FraudDetector

# -------- FastAPI Setup --------
app = FastAPI(title="VeriClaim AI - Backend API")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Global Models --------
CLAUSE_MODEL_NAME = os.getenv("CLAUSE_EMBED_MODEL", "all-MiniLM-L6-v2")
clause_mapper = ClauseMapper(model_name=CLAUSE_MODEL_NAME)
vector_store = DecisionEngine(dim=384)

# Load trained fraud model
fraud_detector = FraudDetector()
fraud_detector.load()

# Insert sample clauses
SAMPLE_CLAUSES = [
    "The insurer shall reimburse hospitalization expenses within 30 days.",
    "Pre-existing conditions are excluded from coverage.",
    "Accidental injuries are covered up to policy limit."
]
for idx, c in enumerate(SAMPLE_CLAUSES, 1):
    emb = clause_mapper.embed_clause(c)
    vector_store.upsert(f"policy_{idx}", emb, {"clause": c})

# -------- Pydantic Models --------
class VerifyRequest(BaseModel):
    user_query: str
    structured_entities: Optional[Dict[str, Any]] = None
    llm_context: Optional[Dict[str, Any]] = None

class VerifyResponse(BaseModel):
    status: str
    reason: str
    confidence: float
    fraud_score: Optional[float] = None
    insurance_eligible: Optional[str] = None
    relevant_clause: Optional[str] = None

# -------- Endpoints --------
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/verify-claim", response_model=VerifyResponse)
async def verify_claim(req: VerifyRequest):
    # --- Clause Embedding & Similarity ---
    q_text = req.user_query
    q_emb = clause_mapper.embed_clause(q_text)
    results = vector_store.query(q_emb, top_k=1)

    relevant_clause = results[0][2].get("clause", "No relevant clause found.") if results else "No relevant clause found."
    confidence = float(results[0][1]) if results else 0.0

    # --- Fraud Detection ---
    fraud_score = None
    fraud_flagged = False
    if req.structured_entities:
        result = fraud_detector.predict_anomaly(req.structured_entities)
        fraud_score = round(result.get("score", 0.0), 2)
        fraud_flagged = result.get("is_anomaly", False)

    # --- Decision Logic ---
    approve_keywords = ["reimburse", "covered", "entitled", "payable", "eligible", "injury", "accident"]
    deny_keywords = ["exclusion", "not covered", "excluded", "except", "pre-existing", "cosmetic"]

    decision = "Review"
    reason = "No strong policy match found."

    combined_text = (q_text + " " + relevant_clause).lower()

    # Deny has higher priority
    if any(w in combined_text for w in deny_keywords):
        decision = "Denied"
        reason = f"❌ Matched policy exclusion (Score: {confidence:.2f})."

    # Approve only if clear coverage
    elif any(w in combined_text for w in approve_keywords):
        if fraud_flagged:
            decision = "Review"
            reason = f"⚠️ Possible fraud despite policy coverage (Score: {confidence:.2f})."
        else:
            decision = "Approved"
            reason = f"✅ Matched policy coverage (Score: {confidence:.2f})."

    # Fraud override for neutral cases
    elif fraud_flagged:
        decision = "Denied"
        reason = f"❌ Flagged by fraud detector (Score: {fraud_score})."

    # -------- Insurance Eligibility Logic --------
    if decision == "Approved":
        insurance_eligible = "YES"
    elif decision == "Review":
        insurance_eligible = "MAYBE"
    else:  # Denied
        insurance_eligible = "NO"

    return VerifyResponse(
        status=decision,
        reason=reason,
        confidence=confidence,
        fraud_score=fraud_score,
        insurance_eligible=insurance_eligible,
        relevant_clause=relevant_clause
    )

# -------- Run Server --------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000, reload=True)
