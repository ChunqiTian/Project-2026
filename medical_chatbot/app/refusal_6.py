# refusal_6_8.py

"""
retrieve evidence
↓
check refusal logic
↓
if refused: return refusal response
↓
else: generate grounded answer with citations
"""
from typing import Optional, List

from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.schemas_1 import RetrievedChunk
from app.guardrails_6 import apply_guardrails

DANGEROUS_DIAGNOSIS_PATTERNS = [
    "do i have",
    "am i having",
    "is this cancer",
    "is this a heart attack",
    "diagnose me",
    "what disease do i have",
    "what condition do i have",
]

TREATMENT_RECOMMENDATION_PATTERNS = [
    "what should i take",
    "what medicine should i take",
    "which medication should i use",
    "should i start taking",
    "should i stop taking",
    "should i take antibiotics",
]

MEDICATION_DOSE_PATTERNS = [
    "increase my dose",
    "decrease my dose",
    "change my dose",
    "double my dose",
    "skip my dose",
    "stop my medication",
    "how much should i take",
    "what dose should i take",
]

EMERGENCY_PATTERNS = [
    "chest pain",
    "can't breathe",
    "cannot breathe",
    "shortness of breath",
    "severe bleeding",
    "stroke",
    "suicidal",
    "overdose",
    "seizure",
    "loss of consciousness",
]


def contains_any(text: str, patterns: List[str]) -> bool:
    # Check whether the user text contains any risky phrase.
    text = text.lower()
    for pattern in patterns:
        if pattern in text: return True
    return False

def detect_hard_refusal_reason(user_text: str) -> Optional[str]:
    # Detect cases where the bot should refuse before using evidence (even before checking retrieved docs).
    if contains_any(user_text, EMERGENCY_PATTERNS): return "emergency_or_urgent_symptoms"
    if contains_any(user_text, DANGEROUS_DIAGNOSIS_PATTERNS): return "diagnosis_request"
    lowered_text = user_text.lower()
    if "dose" in lowered_text and contains_any(lowered_text, ["increase", "decrease", "change", "double", "skip", "stop"]):
        return "medication_dose_change"
    if contains_any(user_text, MEDICATION_DOSE_PATTERNS): return "medication_dose_change"
    if contains_any(user_text, TREATMENT_RECOMMENDATION_PATTERNS): return "treatment_recommendation"
    return None

def is_evidence_too_weak(retrieved_chunks: List[RetrievedChunk], min_score: float=0.30) -> bool:
    # Refuse if retrieval evidence is too weak. 
    if not retrieved_chunks: return True
    top_score = retrieved_chunks[0].score
    if top_score < min_score: return True
    return False

def is_question_ambiguous(user_text: str) -> bool:
     # Detect very short or unclear medical questions. eg. pain, medicine; These are too vague to answer
     words = user_text.strip().split()
     if len(words) <= 2: return True
     vague_terms = ["pain","medicine", "rash", "fever", "dose", "sick"]
     if user_text.lower().strip() in vague_terms: return True
     return False

def get_refusal_reason(user_text: str, retrieved_chunks: List[RetrievedChunk], min_score: float=0.30) -> Optional[str]:
    # Main refusal decision function. - A refusal reason string if the bot should refuse.
    hard_reason = detect_hard_refusal_reason(user_text)
    if hard_reason: return hard_reason
    safety_decision = apply_guardrails(user_text)
    if not safety_decision.allowed_to_answer:
        return safety_decision.reason
    if is_question_ambiguous(user_text): return "ambiguous_question"
    if is_evidence_too_weak(retrieved_chunks, min_score=min_score): return "insufficient_evidence"
    return None

def build_refusal_answer(refusal_reason: str) -> str:
    """
    Convert a refusal reason into a user-friendly answer.
    """

    if refusal_reason == "emergency_or_urgent_symptoms":
        return (
            "I’m not able to safely assess urgent or emergency symptoms here. "
            "Please seek immediate medical help or call emergency services if symptoms are severe, sudden, or worsening."
        )

    if refusal_reason == "diagnosis_request":
        return (
            "I can’t diagnose your condition. A diagnosis requires a qualified medical professional "
            "who can review your symptoms, medical history, and possibly examine you. "
            "I can share general educational information, but please contact a clinician for diagnosis."
        )

    if refusal_reason == "medication_dose_change":
        return (
            "I can’t recommend changing a medication dose. Dose changes can be unsafe without knowing your "
            "medical history, current medications, allergies, and lab results. Please contact your doctor or pharmacist."
        )

    if refusal_reason == "treatment_recommendation":
        return (
            "I can’t recommend a specific treatment or medication for you personally. "
            "Treatment depends on your diagnosis, health history, allergies, and other medications. "
            "Please ask a qualified clinician or pharmacist."
        )

    if refusal_reason == "ambiguous_question":
        return (
            "I don’t have enough detail to answer safely. Please provide more context, such as the symptom, "
            "how long it has been happening, age range, severity, and any related medical history."
        )

    if refusal_reason == "insufficient_evidence":
        return (
            "I don’t have enough reliable information in the knowledge base to answer that safely. "
            "Please ask a healthcare professional or provide more specific information."
        )
    
    if refusal_reason == "Medication-change request detected.":
        return (
            "I can’t tell you to stop, start, increase, decrease, skip, or switch a medication. "
            "Medication changes can be unsafe without knowing your full medical history, current medications, "
            "allergies, and lab results. Please contact your doctor or pharmacist."
        )

    if refusal_reason == "Child medication dosage question detected.":
        return (
            "I can’t provide medication dosing instructions for a child. "
            "Children’s dosing can depend on age, weight, the exact medication form, other health conditions, "
            "and other medicines being used. Please contact a pediatrician or pharmacist."
        )

    return (
        "I’m not able to answer that safely. Please contact a qualified healthcare professional."
    )




