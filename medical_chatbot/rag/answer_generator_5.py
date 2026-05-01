#answer_generator_5_6_7_8.py
"""
Step 7:
1. Validate inputs
2. Convert evidence/results
3. Check emergency escalation
4. If emergency → return emergency response immediately
5. Else run refusal logic
6. Else build grounded answer with citations
"""
from typing import Any
from app.schemas_1 import AnswerResponse, Citation, RetrievedChunk
from app.refusal_6 import get_refusal_reason, build_refusal_answer
from app.escalation_7 import detect_escalation
from app.guardrails_6 import apply_guardrails

def get_score(item: dict[str, Any] | RetrievedChunk) -> float:
    if isinstance(item, RetrievedChunk):
        return float(item.score)
    return float(item["score"])

def get_chunk_fields(item: dict[str, Any] | RetrievedChunk) -> dict[str, Any]:
    if isinstance(item, RetrievedChunk):
        return {
            "doc_id": item.doc_id,
            "chunk_id": item.chunk_id,
            "text": item.text,
        }
    return item["chunk"]

def calculate_confidence(res: list[dict[str, Any] | RetrievedChunk]) -> float:
    # Use the top retrieval score as the answer confidence.
    # If there are no retrieved chunks, confidence is 0.
    if not res: return 0.0
    top_score = get_score(res[0])
    return round(float(top_score), 2)

def build_plain_answer(res: list[dict[str, Any] | RetrievedChunk]) -> str:
    # Build a simple answer directly from retrieved evidence
    # For now, we are not using an LLM. We simply combine the retrieved chunk text
    answer_parts=[]
    for item in res:
        chunk = get_chunk_fields(item)
        text = chunk["text"]
        answer_parts.append(text)
    combined_answer = "\n\n".join(answer_parts)
    return combined_answer


# Add citations
def format_citation(citation: Citation) -> str:
    """
    Convert a Citation obj into display text. 
    eg. Citation(doc_id="fever_care", chunk_id="chunk_0") becomes: [fever_care: chunk_0]
    """
    return f"[{citation.doc_id}:{citation.chunk_id}]"

def build_citations(results: list[dict[str, Any] | RetrievedChunk]) -> list[Citation]:
    # Build citation obj from retrieved chunks. Each retrieved chunk should contain: doc_id, chunk_id
    citations = []
    seen=set()
    for item in results: 
        chunk = get_chunk_fields(item)
        citation_key = (chunk["doc_id"], chunk["chunk_id"])

        if citation_key not in seen:
            citation = Citation(doc_id=chunk["doc_id"], chunk_id=chunk["chunk_id"])
            citations.append(citation)
            seen.add(citation_key)
    return citations

def format_citations_for_display(citations: list[Citation]) -> list[str]:
    return [format_citation(citation) for citation in citations]


def to_retrieved_chunks(results: list[dict[str, Any] | RetrievedChunk]) -> list[RetrievedChunk]:
    retrieved_chunks = []
    for item in results:
        if isinstance(item, RetrievedChunk):
            retrieved_chunks.append(item)
            continue
        chunk = item["chunk"]
        retrieved_chunks.append(
            RetrievedChunk(
                doc_id=chunk["doc_id"],
                chunk_id=chunk["chunk_id"],
                text=chunk["text"],
                score=float(item["score"]),
            )
        )
    return retrieved_chunks

# Generate answer
def generate_answer(
    user_text: str,
    retrieved_chunks: list[dict[str, Any] | RetrievedChunk] | None = None,
    min_score: float=0.30,
) -> AnswerResponse:
    """
    Return an AnswerResponse from retrieved result dicts.
    Refusal logic runs before answer generation; citations are added only when answering.
    order: (step 7)
    Emergency escalation -> Refusal logic  -> Answer generation from retrieved evidence -> Citations
    Step 8:
    Emergency escal -> Refusal -> Medication/special ppl cation -> answer with citations
    """
    if retrieved_chunks is None: retrieved_chunks=[]

    # Step 7: Emergency and crisis escalation - must run before normal refusal or answer generation
    escalation = detect_escalation(user_text)
    if escalation.should_escalate:
        return AnswerResponse(answer=escalation.message, citations=[], confidence=escalation.confidence, 
                              grounded=False, reason=escalation.reason)

    confidence = calculate_confidence(retrieved_chunks)

    # Step 6: Refusal logic
    refusal_chunks = to_retrieved_chunks(retrieved_chunks)
    refusal_reason = get_refusal_reason(user_text=user_text, retrieved_chunks=refusal_chunks, min_score=min_score)

    if refusal_reason:
        return AnswerResponse(
            answer=build_refusal_answer(refusal_reason),
            citations=[],
            confidence=confidence,
            grounded=False,
            reason=refusal_reason,
        )
    # Step 8: allowed but sensitive medication / special-population questions
    safety_decision = apply_guardrails(user_text)
    plain_answer = build_plain_answer(retrieved_chunks)
    if safety_decision.action == "answer_with_caution":
        final_answer = safety_decision.user_message + "\n\n" + plain_answer
        response_reason = safety_decision.reason
    else:
        final_answer = plain_answer
        response_reason = "answered_from_retrieved_evidence"

    # Step 5: grounded answer with citations
    return AnswerResponse(
        answer=final_answer,
        citations=build_citations(retrieved_chunks),
        confidence=confidence,
        grounded=True,
        reason=response_reason,
    )







