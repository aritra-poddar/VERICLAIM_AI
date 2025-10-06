# 🚀 VeriClaim: AI-Powered Insurance Claim Eligibility Checker

### 🧠 A Samsung PRISM Hackathon Project Submission

**VeriClaim** is an AI-driven, full-stack insurance claim verification system that automates the eligibility and fraud detection process using Natural Language Processing (NLP) and Machine Learning.  
It provides **instant, explainable decisions** — helping insurers, hospitals, and customers save time, reduce manual errors, and detect fraudulent claims efficiently.

<br>

## 🌟 Overview

Insurance claim validation is often time-consuming and vulnerable to human oversight. **VeriClaim** addresses this by leveraging **semantic embeddings**, **anomaly detection**, and **intelligent reasoning** to automate claim eligibility assessment.

This platform combines a **Python FastAPI backend**, a **React-based frontend**, and **ML & Gen AI-powered policy analysis**, resulting in a highly responsive and transparent decision-making system.

<br>

## 🧩 Key Features

| Feature | Description |
|----------|-------------|
| **Real-Time Eligibility Decisions** | Instantly predicts claim outcomes as **APPROVED**, **DENIED**, or **REQUIRES REVIEW**. |
| **Semantic Policy Matching** | Uses **Sentence Transformers** and vector similarity search to match natural language claim descriptions with policy clauses. |
| **Anomaly & Fraud Detection** | Employs an **Isolation Forest model** to identify statistically unusual claim patterns. |
| **Transparent Reasoning** | Each result includes semantic similarity scores, top-matched policy clauses, and fraud risk indicators for explainability. |
| **Modern UI/UX** | Built with **React**, featuring a **dark-themed, data-visualized interface** for clarity and ease of use. |

<br>

## 🛠️ Technology Stack

| Component | Technology | Role |
|------------|-------------|------|
| **Frontend** | React (JavaScript) | Form submission, results visualization, and dynamic UI rendering |
| **Backend/API** | FastAPI (Python) | Handles data routing, analysis orchestration, and ML model integration |
| **Machine Learning** | Scikit-learn, Joblib | Isolation Forest model for fraud and anomaly detection |
| **Policy Analysis** | Sentence Transformers, Pinecone/Vector Store | Semantic similarity matching between claim text and policy documents |
| **Data Layer** | CSV / Local Vector Storage | Stores embeddings and policy metadata |

<br>

## ⚙️ Architecture

Frontend (React)
      ↓
Backend (FastAPI)
      ↓
ML Models (Scikit-learn, Sentence Transformers)
      ↓
Vector Database (Pinecone / In-memory)
      ↓
Result: Decision + Reasoning + Clause Reference



## 🚀 Getting Started

### Prerequisites
- Python 3.8+  
- Node.js & npm  
- Virtual environment (`venv`) enabled  



### Step 1: Clone the Repository
```bash
git clone https://github.com/aritra-poddar/VERICLAIM_AI.git
cd VERICLAIM_AI
```



### Step 2: Set Up and Run the Backend
```bash
# Activate your Python virtual environment first
uvicorn backend.api.main:app --reload --port 8000
```



### Step 3: Load ML Models and Policy Data
```bash
python load_data.py
```
This command trains the fraud detection model using claim datasets (CSV) and embeds policy clauses into the vector store for semantic matching.



### Step 4: Start the Frontend
```bash
cd frontend
npm install
npm start
```

The application will be available at **http://localhost:3000**

<br>

## 📊 Sample Output
- **Eligibility Status:** APPROVED / DENIED / REQUIRES REVIEW  
- **Top Matching Policy Clause:** Extracted from vector embeddings  
- **Semantic Similarity Score:** e.g., 0.87  
- **Fraud Risk Level:** Low / Medium / High  

<br>

## 🔒 Ethical & Social Impact

VeriClaim contributes to **trustworthy and efficient insurance ecosystems** by:
- Reducing manual workload for claims adjusters  
- Detecting potential fraud early  
- Ensuring fair, explainable decisions for customers  
- Improving data-driven insurance workflows  

<>br

## 🧑‍💻 Contributors
[**Aritra Poddar**](https://github.com/aritra-poddar) <br>
[**Aaditya Gupta**](https://github.com/aadityaguptaaa)<br>
B.Tech (CSE) — AI & Full Stack Developer  


<br>

## 🏆 Submission Information
**Hackathon:** Samsung PRISM 2025  
**Track:** Artificial Intelligence & Software Innovation  
**Project Category:** AI + Insurance Automation  

<br>

## 🧭 Future Enhancements
- Integration with real insurance provider APIs  
- Deployment on AWS / Hugging Face Spaces  
- Adding LLM-powered explanation layer for more natural feedback  
- Blockchain-backed claim integrity verification  



## 📜 License
This project is released under the **MIT License** — free to use, modify, and build upon.



### 💡 “Empowering insurers with intelligent, transparent, and automated decision-making.”
