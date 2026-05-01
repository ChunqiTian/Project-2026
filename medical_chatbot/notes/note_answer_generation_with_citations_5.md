Step 5 - Answer generation with citations

Generate grounded answers only from retrieved evidence:
- plain-language medical explanation
- no unsupported claims

File: answer_generator.py
- retrieved chunks -> grounded medical answer with citations
The bot can only answer using the retrieved evidence. 
If the evidence does not support the answer, it should say it does not have enough info.

Pipeline
1. Update schemas.py
2. Create answer_generator.py
3. Add citations
4. Add weak-evidence refusal
5. Add ui_helpers.py
6. Add prompts.py only if using an LLM









