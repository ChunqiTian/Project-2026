# Add a simple retrieval function
"""
Before embeddings, we can start with a simple keyword-overlap retriever. 
This is a good first step bcz it lets you test the pipeline before adding vector search later. 
"""
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1] #find the project root
    #__file__ = the current file’s path
    #Path(__file__) = turns that string into a Path object
    #.resolve() = converts it to an absolute path
    #.parents[1] = goes up 2 levels from this file
if str(ROOT) not in sys.path: # This line checks whether the proj root is already in Python's import search path
    sys.path.insert(0, str(ROOT)) #If the project root is missing, add it to sys.path
        #insert(0, ...) puts it at the front, so Python checks that folder first when importing

from app.kb_types_2 import MedicalChunk, RetrievalResult

def tokenize(text: str) -> set[str]:
    return set(re.findall(r"\b[a-zA-Z]+\b", text.lower()))

def load_chunks(path: str="kb/processed/chunks.json") -> list[MedicalChunk]:
    with open(path, "r", encoding="utf-8") as f:
        raw_chunks = json.load(f)
    return [MedicalChunk(**item) for item in raw_chunks]

def score_chunk(query: str, chunk_text: str) -> float:
    query_tokens = tokenize(query)
    chunk_tokens = tokenize(chunk_text)
    if not query_tokens or not chunk_tokens: return 0.0
    overlap = query_tokens.intersection(chunk_tokens)
    return len(overlap)/len(query_tokens)

def retrieve_relevant_chunks(query: str, top_k: int=3) -> list[RetrievalResult]:
    chunks = load_chunks()
    scored_res=[]
    for chunk in chunks:
        score = score_chunk(query, chunk.text)
        if score > 0: scored_res.append(RetrievalResult(chunk=chunk, score=score))
    scored_res.sort(key=lambda x: x.score, reverse=True)
    return scored_res[:top_k]




