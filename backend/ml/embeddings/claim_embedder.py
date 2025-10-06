"""
Encodes claim documents (text extracted from PDFs / OCR) for vector search.
Provides helpers to chunk long texts, embed chunks, and return chunk metadata.
"""

from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import numpy as np
import math
import os

MODEL_NAME = os.getenv("CLAIM_EMBED_MODEL", "sentence-transformers/all-mpnet-base-v2")

class ClaimEmbedder:
    def __init__(self, model_name: str = MODEL_NAME, chunk_size: int = 400, chunk_overlap: int = 50):
        self.model = SentenceTransformer(model_name)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[str]:
        words = text.split()
        if len(words) <= self.chunk_size:
            return [text]
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            if end == len(words):
                break
            start = end - self.chunk_overlap
        return chunks

    def encode_claim(self, text: str, batch_size: int = 16) -> Tuple[List[str], np.ndarray]:
        chunks = self.chunk_text(text)
        embeddings = self.model.encode(chunks, batch_size=batch_size, show_progress_bar=True, convert_to_numpy=True)
        return chunks, embeddings
