"""
Flow
User asks a question
   ↓
Should we escalate?
   ↓
Should we refuse?
   ↓
Should we retrieve from KB?
   ↓
Should we answer with caution?
   ↓
Build final response

"""

from pathlib import Path
import sys

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.escalation_7 import detect_escalation
from app.guardrails_6 import apply_guardrails
from app.intent_classifier_1 import classify_intent
from app.refusal_6 import detect_hard_refusal_reason
from app.response_builder_7 import build_bot_response_from_answer
from app.risk_detector_1 import collect_flags, detect_risk
from app.schemas_1 import AnswerResponse, BotResponse, RetrievedChunk, ConversationState
from rag.answer_generator_5 import generate_answer
from rag.retrieve_tfidf_4 import retrieve_tfidf
from app.memory_10 import is_follow_up_question, summarize_memory_for_router, update_conversation_memory


CHUNKS_PATH = PROJECT_ROOT / "kb" / "processed" / "chunks.json"
DEFAULT_TOP_K = 3
DEFAULT_MIN_SCORE = 0.30
REFUSALS_REQUIRING_HUMAN = {
    "diagnosis_request",
    "treatment_recommendation",
    "medication_dose_change",
    "Medication-change request detected.",
    "Child medication dosage question detected.",
}


def build_disclaimer(action: str) -> str:
    if action in {"escalate_emergency", "support_crisis"}:
        return "This chatbot does not provide diagnosis or emergency care."
    return "This chatbot provides general information only and does not replace a licensed clinician."


def build_follow_up(action: str, answer_response: AnswerResponse) -> str | None:
    if action == "answer":
        return "Would you like a shorter summary or more detail from the retrieved source?"
    if action == "answer_with_caution":
        return "You can ask for general source-based information, but personal guidance should come from a clinician or pharmacist."
    if action == "refuse" and answer_response.reason == "insufficient_evidence":
        return "Try asking about a topic that exists in the knowledge base, such as hypertension, amoxicillin, wound care, or appointments."
    return None


def should_retrieve(user_text: str) -> bool:
    escalation = detect_escalation(user_text)
    if escalation.should_escalate:
        return False

    safety_decision = apply_guardrails(user_text)
    if not safety_decision.allowed_to_answer:
        return False

    hard_refusal_reason = detect_hard_refusal_reason(user_text)
    if hard_refusal_reason:
        return False

    return True


def retrieve_answer_chunks(
    user_text: str,
    top_k: int = DEFAULT_TOP_K,
    min_score: float = DEFAULT_MIN_SCORE,
) -> list[RetrievedChunk]:
    retrieval_result = retrieve_tfidf(
        query=user_text,
        top_k=top_k,
        refusal_threshold=min_score,
        path=CHUNKS_PATH,
    )

    answer_chunks = [
        RetrievedChunk(
            doc_id=item.doc_id,
            chunk_id=item.chunk_id,
            text=item.text,
            score=item.score,
        )
        for item in retrieval_result.results
    ]

    strong_chunks = [chunk for chunk in answer_chunks if chunk.score >= min_score]
    if strong_chunks:
        return strong_chunks

    # Keep only the best weak chunk so the refusal response can still show confidence.
    return answer_chunks[:1]


def choose_action(user_text: str, answer_response: AnswerResponse) -> str:
    escalation = detect_escalation(user_text)
    if escalation.should_escalate:
        if escalation.escalation_type == "crisis_line":
            return "support_crisis"
        return "escalate_emergency"

    if not answer_response.grounded:
        return "refuse"

    safety_decision = apply_guardrails(user_text)
    if safety_decision.action == "answer_with_caution":
        return "answer_with_caution"

    intent, _ = classify_intent(user_text)
    if intent in {"symptom_check", "medication_question", "mental_health_support", "unknown"}:
        return "answer_with_caution"

    return "answer"

def enrich_question_with_memory(user_text: str, state: ConversationState | None) -> str:
    # Use memory only to clarify vague follow-up questions. 
    # We do not add a full medical history, only add small controlled context. 
    if state is None: return user_text
    if not is_follow_up_question(user_text): return user_text
    memory_summary = summarize_memory_for_router(state)
    symptom_duration = memory_summary.get("symptom_duration")
    mentioned_age = memory_summary.get("mentioned_age")
    prior_visit_context = memory_summary.get("prior_visit_context")
    previous_context = memory_summary.get("previous_question_context")
    extra_context = []
    if previous_context: extra_context.append(f"Previous context: {previous_context}")
    if mentioned_age: extra_context.append(f"Age mentioned earlier: {mentioned_age}")
    if prior_visit_context: extra_context.append(f"Prior visited: {prior_visit_context}")
    if symptom_duration: extra_context.append(f"Symptom duration mentioned earlier: {symptom_duration}")
    if not extra_context: return user_text
    return user_text + "\n\nControlled conversation context: \n" + "\n".join(extra_context)
"""
eg. Is that serious?

Controlled conversation context:
Previous context: symptom question
Symptom duration mentioned earlier: for 3 days
"""




def handle_message(
    user_text: str,
    top_k: int = DEFAULT_TOP_K,
    min_score: float = DEFAULT_MIN_SCORE,
    state: ConversationState | None = None,
    return_state: bool = False,
) -> BotResponse | tuple[BotResponse, ConversationState]:
    state = update_conversation_memory(user_text=user_text, state=state)
    enriched_text = enrich_question_with_memory(user_text=user_text, state=state)

    intent, intent_confidence = classify_intent(user_text)
    risk_level, risk_reason = detect_risk(user_text, intent)
    flags = collect_flags(user_text)

    retrieved_chunks: list[RetrievedChunk] = []
    safety_note = None

    if should_retrieve(user_text):
        retrieved_chunks = retrieve_answer_chunks(
            user_text=enriched_text,
            top_k=top_k,
            min_score=min_score,
        )
    else:
        safety_note = "Retrieval skipped because a hard safety rule or refusal rule applied first."

    answer_response = generate_answer(
        user_text=user_text,
        retrieved_chunks=retrieved_chunks,
        min_score=min_score,
    )

    action = choose_action(user_text=user_text, answer_response=answer_response)
    escalation = detect_escalation(user_text)
    safety_decision = apply_guardrails(user_text)

    safe_to_answer = answer_response.grounded and action in {"answer", "answer_with_caution"}
    needs_human = (
        escalation.should_escalate
        or safety_decision.needs_human
        or answer_response.reason in REFUSALS_REQUIRING_HUMAN
    )
    refusal_reason = None if answer_response.grounded or escalation.should_escalate else answer_response.reason
    escalation_type = escalation.escalation_type if escalation.should_escalate else "none"

    follow_up = None
    if action == "answer": follow_up = "Would you like a simple general explanation?"
    elif action == "answer_with_caution": follow_up = "I can give general information, " \
    "but for personal medical decisions you should contact a qualified clinician."

    response = build_bot_response_from_answer(
        answer_response=answer_response,
        intent=intent,
        risk_level=risk_level,
        action=action,
        needs_human=needs_human,
        safe_to_answer=safe_to_answer,
        detected_flags=flags,
        disclaimer=build_disclaimer(action),
        follow_up=build_follow_up(action, answer_response),
        refusal_reason=refusal_reason,
        escalation_type=escalation_type,
        safety_note=safety_note or risk_reason,
    )
    if return_state:
        return response, state
    return response


def run_examples() -> None:
    examples = [
        "blood pressure routine checks",
        "common side effects include nausea mild diarrhea stomach upset",
        "request routine appointments phone business hours portal",
        "How much Tylenol should I give my 3-year-old?",
        "Can I stop taking my blood pressure medication?",
        "I have chest pain and trouble breathing.",
    ]

    for text in examples:
        result = handle_message(text)
        print("=" * 80)
        print(f"USER: {text}")
        print(result.model_dump_json(indent=2))


def main() -> None:
    if len(sys.argv) > 1: # see note below
        user_text = " ".join(sys.argv[1:]).strip()
        result = handle_message(user_text)
        print(result.model_dump_json(indent=2))
        return

    run_examples()


if __name__ == "__main__":
    main()


"""
The line if len(sys.argv) > 1: is a check to see if the user provided any extra information when they ran the script from the terminal.
- sys.argv[0]: This is always the name of the script itself (e.g., myscript.py).
- sys.argv[1]: This is the first argument provided after the script name.
- len(sys.argv) > 1: Since the script name is always index 0, the length is always at least 1. If the length is greater than 1, it means the user typed something extra.

eg: python run.py "for 5 days"
len(sys.argv) is 2.
The if statement is True.
sys.argv[1] is "for 5 days".

"""
