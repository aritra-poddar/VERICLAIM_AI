import requests
import os
import sys

# --- Configuration ---
# Your FastAPI server should be running on this address
API_BASE_URL = "http://127.0.0.1:8000"
HEADERS = {"Content-Type": "application/json"}

# --- Path Setup ---
# Assuming you run this script from the VERICLAIM root directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# IMPORTANT: This path assumes your PDF is in VERICLAIM/data/
PDF_PATH = os.path.join(CURRENT_DIR, "data", "BAJAJ DATASET_1.PDF")

def train_fraud_detector(n_samples: int = 500):
    """Triggers the fraud model training endpoint."""
    print("--- 1. Training Fraud Detector ---")
    url = f"{API_BASE_URL}/fraud/train"
    payload = {"n_samples": n_samples}
    
    try:
        response = requests.post(url, json=payload, headers=HEADERS)
        response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
        print(f"✅ Fraud Detector trained successfully with {n_samples} samples.")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect or train fraud model: {e}")
        print("   -> Ensure your FastAPI server is running on port 8000.")

def upsert_policy_clauses_from_pdf():
    """Reads the PDF and upserts policy clauses into the vector store."""
    try:
        from pypdf import PdfReader
    except ImportError:
        print("❌ Cannot run clause upsert. Please install 'pypdf': pip install pypdf")
        return

    print("\n--- 2. Loading Policy Clauses from PDF ---")
    url = f"{API_BASE_URL}/clauses/upsert"
    
    if not os.path.exists(PDF_PATH):
        print(f"❌ PDF file not found at: {PDF_PATH}")
        return

    try:
        reader = PdfReader(PDF_PATH)
        print(f"Reading {len(reader.pages)} pages...")
        
        # Extract text and split it by double newline to get distinct paragraphs/clauses
        full_text = "".join(page.extract_text() or "" for page in reader.pages)
        # Filter clauses to ensure they are substantial pieces of text
        clauses = [c.strip() for c in full_text.split('\n\n') if len(c.strip()) > 50]
        
        print(f"Found {len(clauses)} substantial clauses to upload.")

        for i, clause_text in enumerate(clauses):
            if i >= 100: # Limit to 100 clauses to prevent excessive runtime
                break
                
            clause_id = f"P{i+1}"
            payload = {
                "clause_id": clause_id,
                "clause_text": clause_text,
                "metadata": {"source": "Bajaj Policy PDF", "page": "Unknown"}
            }
            
            response = requests.post(url, json=payload, headers=HEADERS)
            if response.status_code == 200:
                print(f"  -> Successfully upserted clause {clause_id}")
            else:
                print(f"  -> Failed to upsert clause {clause_id}. Status: {response.status_code}")
                
        print("✅ Clause loading complete.")
        
    except Exception as e:
        print(f"❌ An error occurred during PDF reading/upload: {e}")


if __name__ == "__main__":
    if not os.path.exists(os.path.join(CURRENT_DIR, "backend", "api", "main.py")):
        print("❌ ERROR: Please ensure you are running this script from the VERICLAIM root directory.")
        sys.exit(1)

    # You MUST ensure your FastAPI server is running before running this script!
    print("--- CHECK: Ensure FastAPI server is running on port 8000 ---")
    
    # 1. Train the fraud model using the CSV data (triggered internally by the backend)
    train_fraud_detector()
    
    # 2. Load policy terms from the PDF into the vector store
    upsert_policy_clauses_from_pdf()

    print("\n--- Data loading complete. You can now test the frontend form. ---")
