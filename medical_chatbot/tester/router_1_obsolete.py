# This file decide what the bot should do

from app.schemas_1 import IntentType, RiskLevel, ActionType

def route_action(intent: IntentType, risk_level: RiskLevel) -> tuple[ActionType, bool, bool]:
    if intent == "self_harm_risk": return "support_crisis", True, False # (action, human_needed, safe_to_answer)
    if intent == "emergency" or risk_level == "emergency": return "escalate_emergency", True, False
    if risk_level == "high": return "escalate_clinician", True, False
    if intent in {"general_health_info", "administrative"} and risk_level == "low": return "answer", False, True
    if intent in {"symptom_check", "medication_question", "mental_health_support", "unknown"}: return "answer_with_caution", False, True
    return "refuse", False, False

def generate_answer(user_text: str, intent: IntentType, risk_level: RiskLevel, action: ActionType, reason: str) -> str:
    if action == "escalate_emergency": 
        return (
            "Your symptoms may need urgent medical attention. "
            "Please call emergency services now or go to the nearest emergency department immediately.")
    
    if action == "support_crisis":
        return (
            "I'm really sorry you're dealing with this. "
            "Please contact emergency services now if you may act on these thoughts, "
            "or reach out immediately to a crisis hotline or a trusted person near you.")
    
    if action == "escalate_clinician":
        return(
            "I can't safely assess this situation here. "
            "Please contact a licensed clinician or urgent care as soon as possible.")
    
    if action == "answer":
        if intent == "general_health_info":
            return "I can provide general health information, but not diagnosis or personal medical treatment advice."
        if intent == "administrative": 
            return (
                "This sounds like an administrative healthcare question. "
                "I can help with general guidance if you share the details."
            )
        
    if action == "answer_with_caution":
        if intent == "symptom_check": 
            return (
                "I can give general information about symptoms, but I can't diagnose you. "
                "If symptoms are worsening, severe, or concerning, please seek medical care promptly."
            )
        if intent == "medication_question":
            return (
                "I can provide only general information about medication questions. "
                "A pharmacist or licensed clinician should confirm interactions, dosing, and safety for your situation."
            )
        if intent == "mental_health_support":
            return (
                "I'm sorry you're going through that. I can offer general support and grounding suggestions, "
                "but I'm not a substitute for a mental health professional."
            )
        
        return (
            "I can provide only general health information here. "
            "I can't verify diagnosis, emergency severity, or personalized treatment."
        )
    return "I'm not able to help safely with that request."

def build_disclaimer(action: ActionType) -> str:
    if action in {"escalate_emergency", "support_crisis"}:
        return "This chatbot does not provide diagnosis or emergency care."
    return "This chatbot provides general information only and does not replace a licensed clinician."




