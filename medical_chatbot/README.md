# Medical Chatbot Demo

<img width="1710" height="992" alt="image" src="https://github.com/user-attachments/assets/ac6172ab-4af6-47fc-9fb7-5b060c85ed59" />

A portfolio project demonstrating a safety-aware, retrieval-based medical information chatbot built with Python and Streamlit.

The goal of this project is not to build a production medical assistant. The goal is to demonstrate practical engineering skills for AI application development: retrieval, structured response design, safety routing, evaluation, UI integration, and maintainable Python architecture.

## Portfolio Highlights

- Built an end-to-end chatbot workflow from user input to structured response display.
- Implemented a retrieval-augmented answer flow using a local curated knowledge base.
- Added safety guardrails for diagnosis requests, medication changes, emergencies, and ambiguous questions.
- Designed Pydantic schemas for consistent response, citation, retrieval, and conversation-memory objects.
- Created a Streamlit chat UI with risk/action/confidence badges, citations, and debug transparency controls.
- Added controlled multi-turn memory so vague follow-up questions can use limited prior context.
- Built an evaluation harness with test cases, metrics, and generated error-analysis reports.

## Skills Demonstrated

| Area | Demonstrated Through |
| --- | --- |
| Python application design | Modular files for routing, retrieval, schemas, safety, memory, response building, and UI helpers |
| Streamlit UI development | Chat interface, sidebar controls, session state, metadata panels, citations, and warnings |
| Retrieval / NLP | TF-IDF search over local medical knowledge-base chunks with title/topic/text matching |
| Safety engineering | Refusal rules, emergency escalation, risk detection, and conservative evidence thresholds |
| Data modeling | Pydantic models for structured chatbot responses, citations, retrieved chunks, and memory state |
| Evaluation | JSONL test cases, metrics computation, pass/fail reporting, and error-analysis output |
| Product thinking | Clear user boundaries, transparency controls, and safety-first behavior |
| Debugging and iteration | Improved retrieval matching, fixed session-state memory handling, and added troubleshooting docs |

## What The App Does

The chatbot answers general health-information questions only when the local knowledge base contains supporting evidence. It can show citations, confidence, risk level, and the action selected by the safety router.

The current knowledge base contains four source documents:

- Hypertension basics
- Wound care after stitches
- Amoxicillin general information
- Appointment scheduling

Example supported questions:

```text
What is hypertension?
Why are routine blood pressure checks important?
How should I care for stitches?
What are common side effects of amoxicillin?
How do I schedule a routine appointment?
```

Example questions the app should refuse or escalate:

```text
Do I have pneumonia?
Should I stop taking my medication?
How much medicine should I take?
I have chest pain and trouble breathing.
```

## Architecture

```text
User message
    |
    v
Streamlit UI
    |
    v
Router
    |-- intent classification
    |-- risk detection
    |-- guardrails and refusal checks
    |-- controlled conversation memory
    |
    v
Retriever
    |-- TF-IDF search over title, topic, source type, and chunk text
    |-- evidence threshold check
    |
    v
Answer builder
    |-- grounded answer
    |-- citations
    |-- confidence
    |-- safety metadata
    |
    v
Streamlit response display
```

## Key Design Decisions

- Evidence-first answering: the bot answers only when retrieved evidence is strong enough.
- Conservative medical safety: diagnosis, medication changes, dosing, and emergencies are refused or escalated.
- Structured outputs: all major responses use typed schemas instead of loose dictionaries.
- Transparent UI: users can see risk level, action, evidence strength, citations, and optional debug data.
- Limited memory: the app stores small controlled context such as symptom duration, not full medical history.
- Local-first prototype: the knowledge base is file-based and easy to inspect, rebuild, and test.

## Project Structure

```text
.
|-- streamlit_app_11.py          # Main Streamlit UI
|-- app/
|   |-- router_8.py              # Main chatbot routing flow
|   |-- guardrails_6.py          # Safety guardrails
|   |-- refusal_6.py             # Refusal logic
|   |-- escalation_7.py          # Emergency/crisis escalation
|   |-- memory_10.py             # Controlled conversation memory
|   |-- response_builder_7.py    # BotResponse construction
|   |-- schemas_1.py             # Pydantic response/state schemas
|   `-- ui_helpers_5.py          # Streamlit display helpers
|-- rag/
|   |-- retrieve_tfidf_4.py      # Active TF-IDF retriever
|   |-- retrieval_schema_4.py    # Retrieval result schemas
|   `-- answer_generator_5.py    # Evidence-based answer generation
|-- kb/
|   |-- raw_docs/                # Source knowledge-base text files
|   |-- processed/               # Generated JSON documents/chunks
|   `-- build_kb_2.py            # Knowledge-base build script
|-- eval/
|   |-- test_cases_9.jsonl       # Evaluation cases
|   |-- run_eval_9.py            # Evaluation runner
|   `-- reports/                 # Generated evaluation reports
|-- tester/                      # Script-style checks and demos
`-- docs/                        # Safety and evaluation notes
```

## Tech Stack

- Python 3.11
- Streamlit
- Pydantic
- scikit-learn TF-IDF retrieval
- rank-bm25 experimentation
- Local JSON knowledge base

## Setup

Create and activate an environment:

```bash
conda create -n ml_foundations python=3.11
conda activate ml_foundations
```

Install dependencies:

```bash
python -m pip install streamlit pydantic scikit-learn rank-bm25 requests
```

If VS Code underlines imports after installation, select the same interpreter:

```text
Cmd+Shift+P -> Python: Select Interpreter -> ml_foundations
```

## Run The App

From the project root:

```bash
streamlit run streamlit_app_11.py
```

To stop the Streamlit server:

```text
Ctrl+C
```

## Rebuild The Knowledge Base

If files under `kb/raw_docs/` change, rebuild the processed JSON:

```bash
python kb/build_kb_2.py
```

This writes:

```text
kb/processed/documents.json
kb/processed/chunks.json
```

## Run Evaluation

Run the evaluation harness:

```bash
python eval/run_eval_9.py
```

Generated reports:

```text
eval/reports/baseline_results.json
eval/reports/error_analysis.md
```

## Quick Checks

```bash
python tester/tester_memory_10.py
python app/router_8.py "blood pressure routine checks"
python app/router_8.py "How should I care for stitches?"
```

## Safety Scope

This project is intentionally conservative:

- It does not diagnose.
- It does not recommend personal treatment plans.
- It does not provide medication dosing.
- It does not replace a clinician, pharmacist, nurse, or emergency service.
- It escalates emergency or crisis-related language.
- It answers only from the small approved local knowledge base.

## Future Improvements

- Add a larger medical knowledge base with source metadata and versioning.
- Add unit tests and CI for router, retrieval, guardrails, and evaluation metrics.
- Add embedding-based retrieval and compare it against TF-IDF/BM25.
- Add a model-backed answer generator with stricter citation grounding.
- Add deployment instructions and a hosted demo.
- Add richer evaluation for false refusals, missed escalations, and citation quality.


## Important Disclaimer

This is a portfolio and learning project, not a medical device. It is not suitable for real clinical use and should not be used for diagnosis, treatment, medication decisions, or emergency care.
