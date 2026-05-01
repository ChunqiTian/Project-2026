import json
import re
from pathlib import Path
from typing import Any

from rank_bm25 import BM25Okapi
from rag.retrieval_schema_4 import RetrievedChunk, RetrievalResult

CHUNKS_PATH = Path("kb/processed/chunks.json")
def load_chunks(path: str | Path = CHUNKS_PATH) -> list[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def tokenize(text: str) -> list[str]:
    # Simple tokenizer: lowercase | keep only word-like tokens
    return re.findall(r"\b\w+\b", text.lower())

def build_bm25_index(chunks: list[dict[str, Any]]) -> tuple[BM25Okapi, list[list[str]]]:
    # Build BM25 index from chunk texts. Returns: fitted BM25 object; tokenized chunk texts
    tokenized_chunks = [tokenize(chunk["text"]) for chunk in chunks]
    bm25 = BM25Okapi(tokenized_chunks)
    return bm25, tokenized_chunks

def score_query(query: str, bm25: BM25Okapi) -> list[float]:
    # Score a query against all chunks using BM25.
    tokenized_query = tokenize(query)
    scores = bm25.get_scores(tokenized_query)
    return [float(score) for score in scores]

def rank_chunks(query:str, chunks: list[dict[str, Any]], top_k:int=3, refusal_threshold: float=1.0) -> RetrievalResult:
    # Retrieve top-k chunks using BM25 and decide whether evidence is too weak
    if not chunks: 
        return RetrievalResult(query=query, top_k=top_k, results=[], best_score=0.0, should_refuse=True, 
                               refusal_reason="No chunks available for retrieval.")
    bm25, _ = build_bm25_index(chunks)
    scores = score_query(query, bm25)
    ranked_pairs = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    top_pairs = ranked_pairs[:top_k]
    res = [RetrievedChunk(chunk_id=chunk["chunk_id"], doc_id=chunk["doc_id"], text=chunk["text"], score=float(score)) for chunk, score in top_pairs]
    best_score = float(top_pairs[0][1]) if top_pairs else 0.0
    
    should_refuse = best_score < refusal_threshold
    refusal_reason = None
    if should_refuse:
        refusal_reason = (f"Best BM25 score {best_score:.3f} is below threshold {refusal_threshold:.3f}.")
    
    return RetrievalResult(query=query, top_k=top_k, results=res, best_score=best_score, should_refuse=should_refuse, refusal_reason=refusal_reason)

def retrieve_bm25(query: str, top_k: int=3, refusal_threshold: float=1.0, path: str|Path=CHUNKS_PATH) -> RetrievalResult:
    chunks = load_chunks(path)
    return rank_chunks(query=query, chunks=chunks, top_k=top_k, refusal_threshold=refusal_threshold)







