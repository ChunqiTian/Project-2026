# risk_detector_1_8.py
# This file decides how risky the message is.

from app.schemas_1 import IntentType, RiskLevel
from app.intent_classifier_1 import (contains_any_pattern, EMERGENCY_PATTERNS, SELF_HARM_PATTERNS, 
                                 MENTAL_HEALTH_PATTERNS, MEDICATION_PATTERNS, SYMPTOM_PATTERNS)
"""
def collect_flags(text: str) -> list[str]:
    flags=[]
    if contains_any_pattern(text, EMERGENCY_PATTERNS): flags.append("emergency_signal")
    if contains_any_pattern(text, SELF_HARM_PATTERNS): flags.append("self_harm_signal")
    if contains_any_pattern(text, MENTAL_HEALTH_PATTERNS): flags.append("mental_health_signal")
    if contains_any_pattern(text, MEDICATION_PATTERNS): flags.append("medication_signal")
    if contains_any_pattern(text, SYMPTOM_PATTERNS): flags.append("symptom_signal")
    return flags

def detect_risk(user_text: str, intent: IntentType) -> tuple[RiskLevel, str]:
    text = user_text.lower()
    # First check if the actual words contain red-flag danger signals
    if contains_any_pattern(text, SELF_HARM_PATTERNS): return "emergency", "Self-harm or suicide risk detected"
    if contains_any_pattern(text, EMERGENCY_PATTERNS): return "emergency", "Possible emergency symptoms detected"
    # If there is no obvious emergency phrase, then use the intent category to assign the default risk level
    if intent == "mental_health_support": return "high", "Mental health distress requires cautions handling"
    if intent == "medication_question": return "medium", "Medication questions can be clinically sensitive"
    if intent == "symptom_check": return "medium", "Symptoms mentioned; avoid diagnosis and use caution"
    if intent == "general_health_info": return "low", "General educational health question"
    if intent == "administrative": return "low", "Administrative question"
    return "medium", "Unknown request in medical setting; cautious default"
"""

# Step 8 - special-population patterns
PREGNANCY_PATTERNS = [
    r"\bpregnant\b",
    r"\bpregnancy\b",
    r"\bexpecting\b",
    r"\btrying to conceive\b",
    r"\bttc\b",
]

BREASTFEEDING_PATTERNS = [
    r"\bbreastfeeding\b",
    r"\bnursing\b",
    r"\blactating\b",
]

CHILD_PATTERNS = [
    r"\bchild\b",
    r"\bchildren\b",
    r"\bkid\b",
    r"\bkids\b",
    r"\bbaby\b",
    r"\binfant\b",
    r"\btoddler\b",
    r"\bnewborn\b",
    r"\b\d+[-\s]?(year|yr)[-\s]?old\b",
    r"\b\d+[-\s]?(month|mo)[-\s]?old\b",
]

OLDER_ADULT_PATTERNS = [
    r"\belderly\b",
    r"\bsenior\b",
    r"\bolder adult\b",
    r"\bgrandma\b",
    r"\bgrandpa\b",
    r"\bmy dad\b",
    r"\bmy mom\b",
]

CHRONIC_DISEASE_PATTERNS = [
    r"\bdiabetes\b",
    r"\bhigh blood pressure\b",
    r"\bhypertension\b",
    r"\bkidney disease\b",
    r"\bliver disease\b",
    r"\bheart disease\b",
    r"\bheart failure\b",
    r"\basthma\b",
    r"\bcopd\b",
    r"\bcancer\b",
    r"\bimmunocompromised\b",
    r"\bautoimmune\b",
]

DRUG_INTERACTION_PATTERNS = [
    r"\binteract\b",
    r"\binteraction\b",
    r"\bmix\b",
    r"\bcombine\b",
    r"\btake .* with\b",
    r"\bwith alcohol\b",
    r"\balcohol\b",
]

MEDICATION_CHANGE_PATTERNS = [
    r"\bstop taking\b",
    r"\bquit taking\b",
    r"\bdiscontinue\b",
    r"\bincrease my dose\b",
    r"\bdecrease my dose\b",
    r"\blower my dose\b",
    r"\braise my dose\b",
    r"\bdouble my dose\b",
    r"\bskip my dose\b",
    r"\bchange my medication\b",
    r"\bswitch medication\b",
]

DOSAGE_PATTERNS = [
    r"\bdose\b",
    r"\bdosage\b",
    r"\bhow much\b",
    r"\bhow many mg\b",
    r"\bmilligram\b",
    r"\bmg\b",
    r"\btake \d+",
]


def collect_flags(text: str) -> list[str]:
    flags = []

    # Existing flags
    if contains_any_pattern(text, EMERGENCY_PATTERNS):
        flags.append("emergency_signal")

    if contains_any_pattern(text, SELF_HARM_PATTERNS):
        flags.append("self_harm_signal")

    if contains_any_pattern(text, MENTAL_HEALTH_PATTERNS):
        flags.append("mental_health_signal")

    if contains_any_pattern(text, MEDICATION_PATTERNS):
        flags.append("medication_signal")

    if contains_any_pattern(text, SYMPTOM_PATTERNS):
        flags.append("symptom_signal")

    # Step 8 special-population flags
    if contains_any_pattern(text, PREGNANCY_PATTERNS):
        flags.append("pregnancy_signal")

    if contains_any_pattern(text, BREASTFEEDING_PATTERNS):
        flags.append("breastfeeding_signal")

    if contains_any_pattern(text, CHILD_PATTERNS):
        flags.append("child_signal")

    if contains_any_pattern(text, OLDER_ADULT_PATTERNS):
        flags.append("older_adult_signal")

    if contains_any_pattern(text, CHRONIC_DISEASE_PATTERNS):
        flags.append("chronic_disease_signal")

    # Step 8 medication-safety flags
    if contains_any_pattern(text, DRUG_INTERACTION_PATTERNS):
        flags.append("drug_interaction_signal")

    if contains_any_pattern(text, MEDICATION_CHANGE_PATTERNS):
        flags.append("medication_change_signal")

    if contains_any_pattern(text, DOSAGE_PATTERNS):
        flags.append("dosage_signal")

    return flags


def detect_risk(user_text: str, intent: IntentType) -> tuple[RiskLevel, str]:
    text = user_text.lower()

    # First check if the actual words contain red-flag danger signals.
    # Emergency overrides everything else.
    if contains_any_pattern(text, SELF_HARM_PATTERNS):
        return "emergency", "Self-harm or suicide risk detected"

    if contains_any_pattern(text, EMERGENCY_PATTERNS):
        return "emergency", "Possible emergency symptoms detected"

    # Step 8: medication-change questions should be high risk.
    # Example:
    # "Can I stop taking my blood pressure medication?"
    # "Should I double my dose?"
    if contains_any_pattern(text, MEDICATION_CHANGE_PATTERNS):
        return "high", "Medication-change request detected; needs clinician or pharmacist guidance"

    # Step 8: child dosage questions should be high risk.
    # Example:
    # "How much Tylenol should I give my 3-year-old?"
    if contains_any_pattern(text, CHILD_PATTERNS) and contains_any_pattern(text, DOSAGE_PATTERNS):
        return "high", "Child medication dosage question detected"

    # Step 8: pregnancy/breastfeeding + medication should be high risk.
    # Example:
    # "Can I take ibuprofen while pregnant?"
    if (
        contains_any_pattern(text, PREGNANCY_PATTERNS)
        or contains_any_pattern(text, BREASTFEEDING_PATTERNS)
    ) and contains_any_pattern(text, MEDICATION_PATTERNS):
        return "high", "Medication question during pregnancy or breastfeeding requires extra caution"

    # Step 8: drug interaction questions are clinically sensitive.
    # Example:
    # "Can I mix metformin with alcohol?"
    if contains_any_pattern(text, DRUG_INTERACTION_PATTERNS):
        return "high", "Possible medication interaction question detected"

    # Step 8: chronic disease / older adult + medication should be more cautious.
    if (
        contains_any_pattern(text, CHRONIC_DISEASE_PATTERNS)
        or contains_any_pattern(text, OLDER_ADULT_PATTERNS)
    ) and contains_any_pattern(text, MEDICATION_PATTERNS):
        return "high", "Medication question involving chronic disease or older adult detected"

    # Existing intent-based default risk levels
    if intent == "mental_health_support":
        return "high", "Mental health distress requires cautious handling"

    if intent == "medication_question":
        return "medium", "Medication questions can be clinically sensitive"

    if intent == "symptom_check":
        return "medium", "Symptoms mentioned; avoid diagnosis and use caution"

    if intent == "general_health_info":
        return "low", "General educational health question"

    if intent == "administrative":
        return "low", "Administrative question"

    return "medium", "Unknown request in medical setting; cautious default"






