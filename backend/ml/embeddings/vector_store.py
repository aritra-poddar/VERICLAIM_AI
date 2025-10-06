
import numpy as np

class DecisionEngine:
    def __init__(self, dim: int = 384):
        self.dim = dim
        self.store = {}  # id -> (vector, metadata)
    def upsert(self, id: str, vector, metadata: dict):
        vec = np.array(vector)
        self.store[id] = (vec, metadata)
    def query(self, vector, top_k: int = 1):
        q = np.array(vector)
        results = []
        for k, (v, m) in self.store.items():
            # cosine similarity
            if np.linalg.norm(v)==0 or np.linalg.norm(q)==0:
                score = 0.0
            else:
                score = float(np.dot(v, q) / (np.linalg.norm(v) * np.linalg.norm(q)))
            results.append((k, score, m))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
