# This file decides what kind of request the user is making. 

import re
from app.schemas_1 import IntentType

EMERGENCY_PATTERNS = [
    r"\bchest pain\b",
    r"\bshortness of breath\b",
    r"\bcan't breathe\b",
    r"\btrouble breathing\b",
    r"\bseizure\b",
    r"\bunconscious\b",
    r"\bpassed out\b",
    r"\bstroke\b",
    r"\bface drooping\b",
    r"\bone-sided weakness\b",
    r"\bsevere bleeding\b",
    r"\bbleeding won't stop\b",
    r"\boverdose\b",
    r"\bpoison(ed|ing)?\b",
]

SELF_HARM_PATTERNS = [
    r"\bkill myself\b",
    r"\bsuicide\b",
    r"\bsuicidal\b",
    r"\bwant to die\b",
    r"\bhurt myself\b",
    r"\bself harm\b",
    r"\boverdose on purpose\b",
]

MENTAL_HEALTH_PATTERNS = [
    r"\banxiety\b",
    r"\bpanic attack\b",
    r"\bdepressed\b",
    r"\bdepression\b",
    r"\bfeeling hopeless\b",
    r"\bstressed\b",
]

MEDICATION_PATTERNS = [
    r"\bmedication\b",
    r"\bmedicine\b",
    r"\bdose\b",
    r"\bside effect\b",
    r"\binteraction\b",
    r"\bdrug\b",
    r"\bcan i take\b",
    r"\bmissed dose\b",
    r"\bibuprofen\b",
    r"\badvil\b",
    r"\btylenol\b",
    r"\bacetaminophen\b",
    r"\bmetformin\b",
    r"\baspirin\b",
]

ADMIN_PATTERNS = [
    r"\bappointment\b",
    r"\bclinic hours\b",
    r"\binsurance\b",
    r"\bbilling\b",
    r"\breferral\b",
    r"\bmedical record\b",
]

SYMPTOM_PATTERNS = [
    r"\bpain\b",
    r"\bfever\b",
    r"\bcough\b",
    r"\bnausea\b",
    r"\bvomiting\b",
    r"\bheadache\b",
    r"\bdizzy\b",
    r"\brush\b",
    r"\bsymptom\b",
    r"\bdiarrhea\b",
]

GENERAL_INFO_PATTERNS = [
    r"\bwhat is\b",
    r"\bhow does\b",
    r"\bcauses of\b",
    r"\bmeaning of\b",
    r"\bdefine\b",
    r"\bexplain\b",
]

def contains_any_pattern(text: str, patterns: list[str]) -> bool:
    for pattern in patterns: 
        if re.search(pattern, text, flags=re.IGNORECASE): return True
    return False

def classify_intent(user_text: str) -> tuple[IntentType, float]:
    text = user_text.lower()
    if contains_any_pattern(text, SELF_HARM_PATTERNS): return "self_harm_risk", 0.98
    if contains_any_pattern(text, EMERGENCY_PATTERNS): return "emergency", 0.97
    if contains_any_pattern(text, ADMIN_PATTERNS): return "administrative", 0.90
    if contains_any_pattern(text, MEDICATION_PATTERNS): return "medication_question", 0.88
    if contains_any_pattern(text, MENTAL_HEALTH_PATTERNS): return "mental_health_support", 0.86
    if contains_any_pattern(text, SYMPTOM_PATTERNS): return "symptom_check", 0.84
    if contains_any_pattern(text, GENERAL_INFO_PATTERNS): return "general_health_info", 0.80
    return "unknown", 0.50




