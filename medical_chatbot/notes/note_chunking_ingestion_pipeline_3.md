Step 3 - Chunking + ingestion pipeline
We will take raw medical docs and turn them into clean, retrieval-ready chunks with metadata, so later the retriever can search them reliably.
In step 2, the goal was mostly about what docs you will use. 
In step 3, we build the system that turns those docs into a format the chatbot can actually search.
Pipeline: Load raw docs -> clean the text -> split text into chunks ->attach metadata to each chunk -> save the chunks for retrieval later

Goal output of this step
{
    "chunk_id": "med_guide_001:chunk_0",
    "doc_id": "med_guide_001",
    "title": "Ibuprofen Medication Guide",
    "source_type": "medication_guide",
    "section": "Warnings",
    "text": "Do not take ibuprofen if you have a history of stomach bleeding...",
    "char_count": 78
}

File structure for Step 3
medical_chatbot/
│
├── app/
│   ├── schemas.py
│   ├── ingest.py
│   ├── chunker.py
│   ├── loader.py
│   └── build_kb.py
│
├── data/
│   ├── raw/
│   │   ├── clinic_policy.txt
│   │   ├── ibuprofen_guide.txt
│   │   └── discharge_fever.txt
│   │
│   └── processed/
│       └── chunks.jsonl
│
└── main.py

What each file does
- schemas.py - Defines the data shape for: raw medical doc | chuned doc
- loader.py - Loads raw files from disk
- chunker.py - Splits each doc into chunks
- ingest.py - Turns raw docs into chunk records with metadata
- build_kb.py - Runs the full pipeline and saves the results

Design idea
For the first version, use simple, reliable chunking.
For medical content, a good starting choice is:
- split by blank lines / paragraphs
- keep section-like text together when possible
- avoid making chunks too tiny
- avoid making chunks too large

Improvement
First version - Use what we built above:
- paragraph splitting
- small-merge
- large-split
- metadata

Later improved version - You may add:
- section-aware chunking
- heading detection
- overlap between chunks
- token-based chunk sizes
- source URL metadata
- trust level metadata
- publication date metadata

Later we may add: source_name | source_url | audience | last_updated | trust_level
eg.
{
    "chunk_id": "discharge_fever:chunk_2",
    "doc_id": "discharge_fever",
    "title": "Discharge Instructions for Fever",
    "source_type": "discharge_instruction",
    "section": "When to seek urgent care",
    "source_url": "internal_clinic_handout_v1",
    "text": "...",
    "char_count": 182
}

Takeaways:
- A raw medical doc is too big for retrieval, so we break it into small meaningful chunks
- Each chunk needs metadata, so later we know: where it came from | what kind oof source it is | how to cite it
- Ingestion means preparing data for retrieval, it is the pipeline from raw files to searchcable chunk records





