# This file creates retrieval-ready chunk objects.
# Each chunk keeps the parent metadata.

from app.kb_types_2 import MedicalDoc, MedicalChunk
from kb.chunk_2 import chunk_doc


def build_chunks(doc: MedicalDoc) -> list[MedicalChunk]:
    return chunk_doc(doc)


def ingest_docs(docs: list[MedicalDoc]) -> list[MedicalChunk]:
    all_chunks: list[MedicalChunk] = []
    for doc in docs:
        all_chunks.extend(build_chunks(doc))
    return all_chunks





