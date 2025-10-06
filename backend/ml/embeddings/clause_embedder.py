
try:
    from sentence_transformers import SentenceTransformer
    _HAS_SBT = True
except Exception:
    _HAS_SBT = False

import numpy as np

class ClauseMapper:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if _HAS_SBT:
            self.model = SentenceTransformer(model_name)
        else:
            # simple fallback: random but deterministic embedding based on hash
            self.dim = 384
    def embed_clause(self, clause: str):
        if _HAS_SBT:
            vec = self.model.encode(clause)
            return np.array(vec)
        else:
            # deterministic pseudo-embedding
            import hashlib
            h = hashlib.sha256(clause.encode('utf-8')).digest()
            arr = np.frombuffer(h, dtype=np.uint8).astype(np.float32)
            # expand/trim to dim
            rep = np.resize(arr, (self.dim,))
            return rep / (rep.max() + 1e-9)
