import json
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from rag.retrieval_schema_4 import RetrievedChunk, RetrievalResult

CHUNKS_PATH = Path("kb/processed/chunks.json")

def load_chunks(path: str | Path = CHUNKS_PATH) -> list[dict[str, Any]]:
    # load chunk records from JSON; Format: {"chunk_id":"..."", "doc_id":"...",...}
    with open(path, "r", encoding="utf-8") as f: 
        return json.load(f)

def build_search_text(chunk: dict[str, Any]) -> str:
    # Include controlled metadata so questions can match titles/topics as well as body text.
    fields = [
        chunk.get("title", ""),
        chunk.get("topic", ""),
        chunk.get("source_type", ""),
        chunk.get("text", ""),
    ]
    return "\n".join(field for field in fields if field)


def build_tfidf_index(chunks: list[dict[str, Any]]) -> tuple[TfidfVectorizer, Any]:
    """
    Fit a TF-IDF vectorizer on all chunk texts and return: fitted vectorizer | chunk matrix
    """
    texts = [build_search_text(chunk) for chunk in chunks]
    vectorizer = TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1,2)) #use unigrams + bigrams
    chunk_matrix = vectorizer.fit_transform(texts) # conver each text chunk into numbers
    return vectorizer, chunk_matrix

def score_query(query: str, vectorizer: TfidfVectorizer, chunk_matrix: Any) -> list[float]: # Same vectorizer from above
    # Convert the user query into TF-IDF space and compute cosine smilarity against every chunk. 
    query_vector = vectorizer.transform([query])
    scores = cosine_similarity(query_vector, chunk_matrix).flatten()
    return scores.tolist()

def rank_chunks(query: str, chunks: list[dict[str, Any]], top_k: int=3, refusal_threshold: float=0.15) -> RetrievalResult:
    # Retrieve top-k chunks for a query and decide whether evidence is too weak.
    if not chunks:
        return RetrievalResult(query=query, top_k=top_k, results=[], best_score=0.0, should_refuse=True, 
                               refusal_reason="No chunks available for retrieval.")
    vectorizer, chunk_matrix = build_tfidf_index(chunks)
    scores = score_query(query, vectorizer, chunk_matrix)
    ranked_pairs = sorted(zip(chunks, scores), key=lambda x:x[1], reverse=True)
    top_pairs = ranked_pairs[:top_k]
    res = [RetrievedChunk(chunk_id=chunk["chunk_id"], doc_id=chunk["doc_id"], text=chunk["text"], score=float(score)) for chunk, score in top_pairs]
    best_score = float(top_pairs[0][1]) if top_pairs else 0.0
    
    should_refuse = best_score < refusal_threshold
    refusal_reason = None
    if should_refuse:
        refusal_reason = (f"Best retrieval score {best_score:.3f} is below threshold {refusal_threshold:.3f}")
    return RetrievalResult(query=query, top_k=top_k, results=res, best_score=best_score, 
                           should_refuse=should_refuse, refusal_reason=refusal_reason)

def retrieve_tfidf(query: str, top_k: int=3, refusal_threshold: float=0.15, path: str | Path=CHUNKS_PATH) -> RetrievalResult:
    """
    Full retrieval entry point: load chunks | rank chunks | return structred result
    """
    chunks = load_chunks(path)
    return rank_chunks(query=query, chunks=chunks, top_k=top_k, refusal_threshold=refusal_threshold)








