import re
from typing import Optional
from pydantic import BaseModel

from app.schemas_1 import EscalationType

class EscalationResult(BaseModel):
    should_escalate: bool
    escalation_type: EscalationType
    reason: str
    message: str
    confidence: float

def contains_any_pattern(text: str, patterns: list[str]) -> bool:
    # Return True if any regex pattern matches the user's text. 
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE): return True
    return False

CHEST_PAIN_PATTERNS = [
    r"\bchest pain\b",
    r"\bchest pressure\b",
    r"\bchest tightness\b",
    r"\bcrushing chest\b",
    r"\bpain.*left arm\b",
    r"\bpain.*jaw\b",
    r"\bpain.*neck\b",
    r"\bshortness of breath.*chest\b",
    r"\bheart attack\b",
]


STROKE_PATTERNS = [
    r"\bstroke\b",
    r"\bface droop",
    r"\bface.*droop",
    r"\bfacial droop",
    r"\bspeech.*slurred\b",
    r"\bslurred speech\b",
    r"\btrouble speaking\b",
    r"\bcannot speak\b",
    r"\bweakness.*one side\b",
    r"\bnumbness.*one side\b",
    r"\bsudden confusion\b",
    r"\bsudden vision\b",
    r"\bsudden severe headache\b",
    r"\bloss of balance\b",
]


BREATHING_TROUBLE_PATTERNS = [
    r"\bcan't breathe\b",
    r"\bcannot breathe\b",
    r"\btrouble breathing\b",
    r"\bdifficulty breathing\b",
    r"\bshortness of breath\b",
    r"\bgasping\b",
    r"\bchoking\b",
    r"\bwheezing badly\b",
    r"\blips.*blue\b",
    r"\bblue lips\b",
]


SUICIDAL_IDEATION_PATTERNS = [
    r"\bi want to die\b",
    r"\bi want to kill myself\b",
    r"\bi'm going to kill myself\b",
    r"\bi am going to kill myself\b",
    r"\bsuicidal\b",
    r"\bend my life\b",
    r"\bno reason to live\b",
    r"\bcan't go on\b",
    r"\bcannot go on\b",
    r"\bself harm\b",
    r"\bhurt myself\b",
]


SEVERE_ALLERGIC_REACTION_PATTERNS = [
    r"\banaphylaxis\b",
    r"\bsevere allergic reaction\b",
    r"\ballergic reaction.*trouble breathing\b",
    r"\ballergic reaction.*throat\b",
    r"\bthroat.*closing\b",
    r"\bswollen tongue\b",
    r"\bswollen lips\b",
    r"\bswelling.*face\b",
    r"\bhives.*trouble breathing\b",
    r"\bused epipen\b",
    r"\bepi pen\b",
    r"\bepinephrine\b",
]


POISONING_PATTERNS = [
    r"\bpoison\b",
    r"\bpoisoning\b",
    r"\boverdose\b",
    r"\btook too much\b",
    r"\bswallowed.*bleach\b",
    r"\bswallowed.*chemical\b",
    r"\bswallowed.*cleaner\b",
    r"\bdrank.*bleach\b",
    r"\bingested\b",
]


OTHER_URGENT_PATTERNS = [
    r"\bunconscious\b",
    r"\bpassed out\b",
    r"\bcan't wake\b",
    r"\bcannot wake\b",
    r"\bseizure\b",
    r"\bsevere bleeding\b",
    r"\bbleeding won't stop\b",
    r"\bbleeding will not stop\b",
    r"\bmajor burn\b",
    r"\bhead injury\b",
    r"\bneck injury\b",
    r"\bsevere pain\b",
]

def emergency_services_message(reason: str) -> str:
    return (
        "This may be a medical emergency. Please call emergency services now "
        "or go to the nearest emergency department immediately. "
        "Do not wait for an online answer.\n\n"
        f"Reason detected: {reason}"
    )


def poison_control_message() -> str:
    return (
        "This may involve poisoning or overdose. If the person has collapsed, "
        "has a seizure, has trouble breathing, or cannot be awakened, call emergency "
        "services now.\n\n"
        "If you are in the United States and the person is stable, contact Poison Control "
        "at 1-800-222-1222 or use the official Poison Control online tool.\n\n"
        "Do not wait for an online answer."
    )


def crisis_message() -> str:
    return (
        "I'm really sorry you're feeling this way. Your safety matters. "
        "If you might hurt yourself or someone else, call emergency services now "
        "or go to the nearest emergency department.\n\n"
        "If you are in the United States or Canada, call or text 988 to reach the Suicide "
        "and Crisis Lifeline. If you are outside the U.S. or Canada, contact your local "
        "emergency number or a local crisis hotline now.\n\n"
        "Please move away from anything you could use to harm yourself and contact someone "
        "you trust immediately."
    )

def detect_escalation(user_text: str) -> EscalationResult:
    """
    Detect emergency or crisis cases.

    This function should run before:
    - retrieval
    - normal answer generation
    - LLM calls
    - weak-evidence refusal
    """

    text = user_text.lower()

    if contains_any_pattern(text, SUICIDAL_IDEATION_PATTERNS):
        return EscalationResult(
            should_escalate=True,
            escalation_type="crisis_line",
            reason="Possible suicidal ideation or self-harm risk.",
            message=crisis_message(),
            confidence=0.98,
        )

    if contains_any_pattern(text, CHEST_PAIN_PATTERNS):
        return EscalationResult(
            should_escalate=True,
            escalation_type="emergency_services",
            reason="Possible heart attack or serious chest-pain emergency.",
            message=emergency_services_message(
                "possible heart attack or serious chest-pain emergency"
            ),
            confidence=0.95,
        )

    if contains_any_pattern(text, STROKE_PATTERNS):
        return EscalationResult(
            should_escalate=True,
            escalation_type="emergency_services",
            reason="Possible stroke symptoms.",
            message=emergency_services_message("possible stroke symptoms"),
            confidence=0.95,
        )

    if contains_any_pattern(text, BREATHING_TROUBLE_PATTERNS):
        return EscalationResult(
            should_escalate=True,
            escalation_type="emergency_services",
            reason="Possible severe breathing emergency.",
            message=emergency_services_message("possible severe breathing emergency"),
            confidence=0.95,
        )

    if contains_any_pattern(text, SEVERE_ALLERGIC_REACTION_PATTERNS):
        return EscalationResult(
            should_escalate=True,
            escalation_type="emergency_services",
            reason="Possible severe allergic reaction or anaphylaxis.",
            message=emergency_services_message(
                "possible severe allergic reaction or anaphylaxis"
            ),
            confidence=0.95,
        )

    if contains_any_pattern(text, POISONING_PATTERNS):
        return EscalationResult(
            should_escalate=True,
            escalation_type="poison_control",
            reason="Possible poisoning, overdose, or toxic ingestion.",
            message=poison_control_message(),
            confidence=0.93,
        )

    if contains_any_pattern(text, OTHER_URGENT_PATTERNS):
        return EscalationResult(
            should_escalate=True,
            escalation_type="emergency_services",
            reason="Possible urgent red-flag symptom.",
            message=emergency_services_message("possible urgent red-flag symptom"),
            confidence=0.90,
        )

    return EscalationResult(
        should_escalate=False,
        escalation_type="none",
        reason="No emergency escalation pattern detected.",
        message="",
        confidence=0.0,
    )








