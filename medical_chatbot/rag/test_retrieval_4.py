"""
The comparison is important bcz you can inspect:
- which chunks each method returns | their score behavior | which method has better result
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rag.retrieve_tfidf_4 import retrieve_tfidf
from rag.retrieval_bm25_4 import retrieve_bm25

def print_res(title, res) -> None:
    print("=" * 8)
    print(title)
    print(f"Query: {res.query}")
    print(f"Best score: {res.best_score:.3f}")
    print(f"Should refuse: {res.should_refuse}")
    if res.refusal_reason: print(f"Reason: {res.refusal_reason}")

    print("\nTop results:")
    for i, item in enumerate(res.results, start=1):
        print("-" * 80)
        print(f"Rank: {i}")
        print(f"Chunk ID: {item.chunk_id}")
        print(f"Doc ID: {item.doc_id}")
        print(f"Score: {item.score:.3f}")
        print(f"Text: {item.text[:300]}...")

if __name__=="__main__":
    query = "Can I take this medicine with food?"
    tfidf_res = retrieve_tfidf(query=query, top_k=3, refusal_threshold=0.15)
    bm25_res = retrieve_bm25(query=query, top_k=3, refusal_threshold=1.0)
    print_res("TF-IDF", tfidf_res)
    print_res("BM25", bm25_res)




