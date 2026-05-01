Step 8 - Medication and special--population safety layer
Goal: Handle sensitive ppl and medication related cases more carefully
- Extra caution for: pregnancy | children | older adults | chronic disease | drug interactions | medication-change questions

Files
- app/guardrails_6.py - Add special rules for special ppl
- app/risk_detector_1.py - Detect phrases indicating these special ppl
- app/refusal_6.py - Add refusal / defer logic for medication change questions.
- kb/raw_docs/safety_policy.md - what medication qestions are allowed; what must be refused | escalated

Flow:
Before step 8:
User question
-> retrieve evidence
-> weak-evidence check
-> generate answer
-> citations

Now:
User question
-> detect special ppl / medication risk
-> apply medication safety guardrails 
-> refuse or caution if needed
-> retrieve evidence
-> weak-evidence check
-> generate answer
-> citation








