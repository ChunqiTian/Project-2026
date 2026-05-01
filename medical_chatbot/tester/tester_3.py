from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kb.load_docs_2 import load_documents
from kb.ingest_3 import ingest_docs

def main():
    docs = load_documents("kb/raw_docs")
    chunks = ingest_docs(docs)
    print(f"Docs loaded: {len(docs)}")
    print(f"Chunks created: {len(chunks)}")

    if chunks:
        print("\nFirst chunk example:")
        print(chunks[0].model_dump())
    else:
        print("\nNo chunks were created. Add .txt files under kb/raw_docs/<source_folder>/")

if __name__ == "__main__":
    main()

