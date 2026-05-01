Step 7 - Emergency and crisis escalation
Emergency detection must happen before normal answering, retrieval, citations, or LLM generation. 

Flow:
user message
    ↓
Emergency / crisis escalation check
    ↓
If emergency -> hard-stop emergency response
    ↓
Otherwise -> refusal logic / retrieval / answer generation


File
- schemas.py - update - Add escalation
- escalation.py - central emergency router
- guardrails.py - update - hard stop layer











