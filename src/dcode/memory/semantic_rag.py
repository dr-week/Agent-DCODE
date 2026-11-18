"""
Zero-dependency Semantic / Keyword BM25-style RAG Memory over project documents and code.
"""

import math
import re
from typing import Any, Dict, List


class SemanticMemory:
    """Lightweight in-memory BM25-style retriever for agent knowledge and code chunks."""

    def __init__(self) -> None:
        self.documents: List[Dict[str, Any]] = []

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r"[a-zA-Z0-9_]{2,}", text.lower())

    def add_document(self, doc_id: str, content: str, metadata: Dict[str, Any] = None) -> None:
        tokens = self._tokenize(content)
        self.documents.append({
            "id": doc_id,
            "content": content,
            "tokens": tokens,
            "metadata": metadata or {},
        })

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.documents:
            return []

        q_tokens = self._tokenize(query)
        n_docs = len(self.documents)
        avg_len = sum(len(d["tokens"]) for d in self.documents) / max(n_docs, 1)
        k1, b = 1.5, 0.75

        scored = []
        for doc in self.documents:
            doc_tokens = doc["tokens"]
            doc_len = len(doc_tokens)
            score = 0.0
            for qt in q_tokens:
                tf = doc_tokens.count(qt)
                if tf == 0:
                    continue
                df = sum(1 for d in self.documents if qt in d["tokens"])
                idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
                denom = tf + k1 * (1 - b + b * (doc_len / max(avg_len, 1)))
                score += idf * ((tf * (k1 + 1)) / denom)
            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {"id": d["id"], "score": round(s, 3), "content": d["content"], "metadata": d["metadata"]}
            for s, d in scored[:top_k]
        ]
