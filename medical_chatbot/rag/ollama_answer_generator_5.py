# question -> retriever -> evidence -> LLM answer from evidence only
"""
confidence = how strong the retrieval signal is (a number) - a measurement
grounded   = whether we are allowed to answer (a decision - bool) - a decision
"""


from typing import Any
import requests

from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.schemas_1 import AnswerResponse
from rag.answer_generator_5 import (
    calculate_confidence,
    build_citations,
    get_chunk_fields,
    to_retrieved_chunks,
)
from app.refusal_6 import get_refusal_reason, build_refusal_answer
from config.prompts_5 import ANSWER_GENERATION_PROMPT
from app.guardrails_6 import apply_guardrails
from app.escalation_7 import detect_escalation

OLLAMA_URL = "http://localhost:11434/api/chat"

def build_evidence_for_prompt(results: list[dict[str, Any]]) -> str:
    evidence_parts = []
    
    for item in results:
        chunk = get_chunk_fields(item)
        doc_id = chunk["doc_id"]
        chunk_id = chunk["chunk_id"]
        text = chunk["text"]
        evidence_parts.append(f"Source: [{doc_id}:{chunk_id}]\n{text}")
    return "\n\n".join(evidence_parts)

def call_ollama(prompt: str, model: str="llama3.2:3b") -> str:
    payload = {
        "model": model, 
        "messages": [{"role": "user", "content": prompt}], 
        "stream": False, 
        "options": {"temperature": 0}
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()
        # This method checks the HTTP status code. If the request returned an unsuccessful 
        # status code (4xx or 5xx, like a "404 Not Found" or "500 Internal Server Error"), 
        # it will automatically raise an HTTPError exception. 
    data = response.json()
    return data["message"]["content"]

def generate_ollama_answer(
        user_text: str,
        retrieved_chunks: list | None = None,
        min_score: float=0.30,
        model: str="llama3.2:3b",
) -> AnswerResponse:
    if retrieved_chunks is None:
        retrieved_chunks = []

    escalation = detect_escalation(user_text)
    if escalation.should_escalate:
        return AnswerResponse(
            answer=escalation.message,
            citations=[],
            confidence=escalation.confidence,
            grounded=False,
            reason=escalation.reason,
        )
    
    conf = calculate_confidence(retrieved_chunks)
    refusal_chunks = to_retrieved_chunks(retrieved_chunks)
    refusal_reason = get_refusal_reason(user_text=user_text, retrieved_chunks=refusal_chunks, min_score=min_score)

    if refusal_reason:
        return AnswerResponse(
            answer=build_refusal_answer(refusal_reason),
            citations=[],
            confidence=conf,
            grounded=False,
            reason=refusal_reason,
        )

    # Step 8: allowed but sensitive medication / special-population questions
    safety_decision = apply_guardrails(user_text)

    evidence = build_evidence_for_prompt(retrieved_chunks)
    prompt = ANSWER_GENERATION_PROMPT.format(question=user_text, evidence=evidence)
    answer = call_ollama(prompt=prompt, model=model)
    if safety_decision.action == "answer_with_caution":
        final_answer = safety_decision.user_message + "\n\n" + answer
        response_reason = safety_decision.reason
    else:
        final_answer = answer
        response_reason = "answered_from_ollama_with_retrieved_evidence"

    citations = build_citations(retrieved_chunks)
    return AnswerResponse(
        answer=final_answer,
        citations=citations,
        confidence=conf,
        grounded=True,
        reason=response_reason,
    )




