from typing import List, Dict, Optional, Any
import hashlib
import json
from typing import List, Optional

class Embeddings:
    def __init__(self, dimension: int = 128):
        self.dimension = dimension

    def encode(self, text: str) -> List[float]:
        """Simple deterministic embedding based on hashing."""
        hash_val = hashlib.md5(text.encode()).hexdigest()
        seed = int(hash_val[:8], 16)
        import random
        rng = random.Random(seed)
        vec = [rng.random() for _ in range(self.dimension)]
        # Normalize
        norm = sum(v ** 2 for v in vec) ** 0.5
        return [v / norm for v in vec]

    def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Cosine similarity."""
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a ** 2 for a in vec1) ** 0.5
        norm2 = sum(b ** 2 for b in vec2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)
