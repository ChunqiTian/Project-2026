# guardrails_6_7_8.py
"""
This file decides whether the bot should:
answer generally | answer with caution | refuse | escalate
"""

from typing import List

OUT_OF_SCOPE_PATTERNS = ["legal advice", "financial advice", "investment advice"]

def is_out_of_scope(user_text: str) -> bool:
    # Detect questions outside the medical chatbot scope.
    text = user_text.lower()
    for pattern in OUT_OF_SCOPE_PATTERNS:
        if pattern in text: return True

    return False


# Step 7 - update - hard stop layer
from app.escalation_7 import detect_escalation

def should_hard_stop(user_text: str) -> bool:
    # Returns True if the bot must not contnue to normal answering. 
    escalation = detect_escalation(user_text)
    return escalation.should_escalate

def get_hard_stop_reason(user_text: str) -> str | None:
    # Returns the reason for hard-stop escaltion.
    escalation = detect_escalation(user_text)
    if escalation.should_escalate: 
        return escalation.reason
    return None

# step 8 - safety layer for special ppl
from typing import Literal
from pydantic import BaseModel

from app.escalation_7 import detect_escalation
from app.risk_detector_1 import collect_flags

SafetyAction = Literal["answer", "answer_with_caution", "refuse", "escalate"]

class SafetyDecision(BaseModel):
    """
    Final guardrail decision
    Actions: answer | answer with caution | refuse | escalate
    For allowed_to_answer: True - answer generation may continue | False - answer generation should stop

    """
    action: SafetyAction
    allowed_to_answer: bool
    needs_human: bool
    reason: str
    user_message: str

def apply_medication_special_population_guardrails(user_text: str) -> SafetyDecision:
    """
    This func uses collect_flags() from risk_detector.py
    Your risk_detector_1.py returns flags like:
    - pregnancy_signal | breastfeeding_signal | child_signal | older_adult_signal | chronic_disease_signal | 
        medication_signal | drug_interaction_signal | medication_change_signal | dosage_signal
    This guardrail turns those flags into an answer/refuse/escalate decision.
    """
    flags = collect_flags(user_text)
    has_medication = "medication_signal" in flags
    has_dosage = "dosage_signal" in flags
    has_medication_change = "medication_change_signal" in flags
    has_drug_interaction = "drug_interaction_signal" in flags

    has_pregnancy = "pregnancy_signal" in flags
    has_breastfeeding = "breastfeeding_signal" in flags
    has_child = "child_signal" in flags
    has_older_adult = "older_adult_signal" in flags
    has_chronic_disease = "chronic_disease_signal" in flags

    has_special_population = (has_pregnancy or has_breastfeeding or has_child or has_older_adult or has_chronic_disease)

    # 1. Medication-change questions should be refused/deferred.
    # Example:
    # "Can I stop taking my blood pressure medication?"
    # "Should I double my dose?"
    if has_medication_change:
        return SafetyDecision(
            action="refuse",
            allowed_to_answer=False,
            needs_human=True,
            reason="Medication-change request detected.",
            user_message=(
                "I can’t tell you to stop, start, increase, decrease, skip, or switch a medication. "
                "Please contact a licensed clinician or pharmacist for guidance. "
                "If you have severe symptoms or feel unsafe, seek urgent medical care."
            ),
        )

    # 2. Child dosage questions should be refused.
    # Example:
    # "How much Tylenol should I give my 3-year-old?"
    if has_child and has_dosage:
        return SafetyDecision(
            action="refuse",
            allowed_to_answer=False,
            needs_human=True,
            reason="Child medication dosage question detected.",
            user_message=(
                "I can’t provide medication dosing instructions for a child. "
                "Children’s dosing depends on age, weight, medication form, medical history, and other factors. "
                "Please contact a pediatrician or pharmacist."
            ),
        )

    # 3. Pregnancy/breastfeeding + medication needs extra caution.
    # Example:
    # "Can I take ibuprofen while pregnant?"
    if (has_pregnancy or has_breastfeeding) and has_medication:
        return SafetyDecision(
            action="answer_with_caution",
            allowed_to_answer=True,
            needs_human=True,
            reason="Medication question during pregnancy or breastfeeding.",
            user_message=(
                "This involves medication use during pregnancy or breastfeeding, so it needs extra caution. "
                "I can share general educational information from trusted sources, but you should confirm "
                "with your clinician or pharmacist before taking or changing any medication."
            ),
        )

    # 4. Drug interaction questions should be answered only generally.
    # Example:
    # "Can I mix metformin with alcohol?"
    if has_drug_interaction:
        return SafetyDecision(
            action="answer_with_caution",
            allowed_to_answer=True,
            needs_human=True,
            reason="Possible medication interaction question detected.",
            user_message=(
                "Drug interactions can depend on dose, timing, medical history, and other medications. "
                "I can provide general information from retrieved sources, but a pharmacist or clinician "
                "should confirm what is safe for you personally."
            ),
        )

    # 5. Older adult/chronic disease + medication requires caution.
    # Example:
    # "Can my grandma with kidney disease take this medicine?"
    if (has_older_adult or has_chronic_disease) and has_medication:
        return SafetyDecision(
            action="answer_with_caution",
            allowed_to_answer=True,
            needs_human=True,
            reason="Medication question involving older adult or chronic disease.",
            user_message=(
                "This question involves medication use with age-related or chronic-health factors. "
                "I can provide general information, but medication safety should be confirmed with "
                "a clinician or pharmacist."
            ),
        )

    # 6. General dosage questions should not give personal dosing instructions.
    # Example:
    # "How much ibuprofen should I take?"
    if has_medication and has_dosage:
        return SafetyDecision(
            action="answer_with_caution",
            allowed_to_answer=True,
            needs_human=True,
            reason="Medication dosage question detected.",
            user_message=(
                "I can share general medication information from reliable sources, but I can’t give "
                "personal dosing instructions. Please follow the medication label or ask a clinician "
                "or pharmacist."
            ),
        )

    # 7. General medication info can be answered carefully.
    # Example:
    # "What is ibuprofen used for?"
    if has_medication:
        return SafetyDecision(
            action="answer_with_caution",
            allowed_to_answer=True,
            needs_human=False,
            reason="General medication information question.",
            user_message=(
                "I can provide general medication information from reliable sources, but this should not "
                "replace advice from a clinician or pharmacist."
            ),
        )

    # 8. Special population but no clear medication risk.
    # Example:
    # "What should pregnant people know about exercise?"
    if has_special_population:
        return SafetyDecision(
            action="answer_with_caution",
            allowed_to_answer=True,
            needs_human=False,
            reason="Special population detected.",
            user_message=(
                "Because this question involves a special population, I’ll keep the answer general and cautious."
            ),
        )

    # 9. No Step 8 safety issue detected.
    return SafetyDecision(
        action="answer",
        allowed_to_answer=True,
        needs_human=False,
        reason="No medication or special-population safety issue detected.",
        user_message="No extra medication or special-population safety restriction detected.",
    )

def apply_guardrails(user_text: str) -> SafetyDecision:
    """
    Main function your answer_generator.py can call.

    Order matters:
    1. Hard-stop escalation
    2. Out-of-scope refusal
    3. Medication/special-population safety
    4. Normal answer
    """

    # 1. Step 7 hard stop comes first.
    if should_hard_stop(user_text):
        reason = get_hard_stop_reason(user_text)

        return SafetyDecision(
            action="escalate",
            allowed_to_answer=False,
            needs_human=True,
            reason=reason or "Hard-stop escalation detected.",
            user_message=(
                "This may be urgent or unsafe to handle in a chatbot. "
                "Please contact emergency services, a crisis line, or a licensed medical professional right away."
            ),
        )

    # 2. Step 6 out-of-scope refusal.
    if is_out_of_scope(user_text):
        return SafetyDecision(
            action="refuse",
            allowed_to_answer=False,
            needs_human=False,
            reason="Out-of-scope request detected.",
            user_message=(
                "I can only help with general medical or clinic-related information. "
                "I can’t provide legal, financial, or investment advice."
            ),
        )

    # 3. Step 8 medication/special-population layer.
    return apply_medication_special_population_guardrails(user_text)
