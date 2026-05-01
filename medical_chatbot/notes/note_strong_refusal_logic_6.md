Step 6 - Strong refusal logic

Goal - Refuse when the bot should not answer. 

Files to create: app/refusal.py

Centralizes refusal logic.
eg. diagnosis request | treatment recommendation | medication does changes | insufficient evidence 
    ambiguous question | 
    
- app/guardrails.py - You many add more hard rules here.
- rag/update answer_generator.py - Should call refusal logic before generating final respponse
- app/schemas.py - may include: refusal_reason | needs_human | allowed_to_answer






