# Build_kb_2_3.py
# Build the knowledge base
# Run everything in one script
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kb.load_docs_2 import load_documents
#from kb.chunk_2 import chunk_doc

from kb.ingest_3 import ingest_docs # Step 3 update

def save_json(data, path:str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def build_knowledge_base() -> None:
    documents = load_documents()
    all_chunks = ingest_docs(documents)
    save_json([doc.model_dump() for doc in documents], "kb/processed/documents.json")
    save_json([chunk.model_dump() for chunk in all_chunks], "kb/processed/chunks.json")
    print(f"Loaded {len(documents)} documents")
    print(f"Created {len(all_chunks)} chunks")
    if all_chunks: # Print for review and debugging
        print("\nFirst chunk preview:")
        print(all_chunks[0].model_dump())

if __name__ =="__main__":
    build_knowledge_base()





