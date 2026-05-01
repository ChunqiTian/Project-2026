# This file connects everything together.

from app.schemas_1 import BotResponse
from app.intent_classifier_1 import classify_intent
from app.risk_detector_1 import detect_risk, collect_flags
from tester.router_1_obsolete import route_action, generate_answer, build_disclaimer
from kb.retrieve_2 import retrieve_relevant_chunks

def handle_message(user_text: str) -> BotResponse:
    intent, confidence = classify_intent(user_text)
    risk_level, reason = detect_risk(user_text, intent)
    action, needs_human, safe_to_answer = route_action(intent, risk_level)
    flags = collect_flags(user_text)

    # Step 2 retrieval only happens if step 1 says answering is allowed
    retrieval_res = []
    if safe_to_answer: retrieval_res = retrieve_relevant_chunks(user_text, top_k=3)

    answer = generate_answer(user_text=user_text, intent=intent, risk_level=risk_level, action=action, reason=reason)

    follow_up = None
    if action == "answer": follow_up="Would you like a simple general explanation?"
    elif action == "answer_with_caution": follow_up="If you'd like, I can give general info while staying on the safe side."

    return BotResponse(intent=intent, risk_level=risk_level, action=action, answer=answer, needs_human=needs_human, 
                       safe_to_answer=safe_to_answer, confidence=confidence, reason=reason, 
                       disclaimer=build_disclaimer(action), follow_up=follow_up, detected_flags=flags)

def main():
    examples = [
        "What is hyertension?",
        "I have a fever and cough for two days",
        "Can I take iburofen with antibiotics?",
        "I want to kill myself", 
        "I have chest pain and shortness of breath",
        "How do I book an appointment?",
        "My head feels stange",
    ]
    for text in examples:
        result = handle_message(text)
        print(f"\nUSER: {text}")
        print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    main()
    


