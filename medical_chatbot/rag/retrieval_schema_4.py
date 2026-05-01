from pydantic import BaseModel
from typing import List

class RetrievedChunk(BaseModel):
    chunk_id: str
    doc_id: str
    text: str
    score: float

class RetrievalResult(BaseModel):
    query: str
    top_k: int
    results: List[RetrievedChunk]
    best_score: float
    should_refuse: bool
    refusal_reason: str | None=None

    





