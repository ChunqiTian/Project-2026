# Step 1 - Medical guardrails + risk routing + response schema


Build the safety foundation: 
- take a user message -> classify it -> assign a risk level -> choose an action (anser/refuse/escalte) -> return a strict structured response

Goal:
1. intent classification - eg. answer low-risk general questions
2. risk detection - eg. avoid pretending to diagnose
3. routing logic - eg. escalte urgent or dangerous situations
4. structured response schema - eg. return consistent JSON-like output

Files included:
- schemas.py - BotResponse; type definitions; fixed structure that every output must follow
- intent_classifier.py - classify_intent()
- risk_detector.py - detect_risk(); flag logic
- router.py - route_action() | generate_anser()
- main.py - handle_message(); demo loop

Design
1. Intent classes - general_health_info | sympton_check | medication_question | administrative (appts, hours...) | 
    mental_health_support | self_harm_risk | emergency (escalation) | unknown (unclear requested)
2. Risk levels - low: general education, admin questions
    - medium: mild symptiom questions, routine medication qs
    - high: severe symptom language, vulnerable situations, possible medication danger
    - emergency: chest pain + short breath, stroke signs, unconsciousness, self-harm activity, overdose, bleeding
3. Rounting actions - choose from: answer: education response
    - answer_with_caution - limited general info + urge professional care if needed
    - refuse - unsafe to answer, outside scope
    - escalate_clinician | escalate_emergency | support_crisis: menal health crisis; self-harm supportive escalation

Important medical chatbot rule: 
- A medical chatbot should not behave like: a doctor | diagnosis engine | prescription engine | emergency substitute










