Step 2: Curated medical knowledge base

Step 1: build the safety/routing foundation
Step 2: focus on safe doc ingestion + chunking + retrieval-ready structure

Pipeline: clean text -> split into chunks -> attach metadata -> store in a local knowledge base 
    -> retrieve relevant chunks for a question -> answer only from those chunks

Goal - By the end of this step, you should have
- a folder of trusted medical docs
- a script that reads them
- a chunking function that splits long docs into smaller pieces
- metadata attached to every chunk
- a simple searchable knowledge base saved as JSON
- a retrieval function that can find the most relevant chunks for a user question

What docs belong here?
- Patient edu docs (general): eg. what is high blood pressure? | How to manage diabetes at home?
- Discharge instructions (time-sensitive): eg. post-surgery home care | wound care instructions
- Medication guide (higher risk): eg. how to take the medication | common side effects 
- Clinic policies (admin): eg. office hrs | appt cancellation policy | refill request rules

Since diff piroities, every doc should carry metadata like:
- source_type | title | topic | risk_level | audience | last_reviewed | version

folder structure
medical_chatbot/
│
├── app/
│   ├── schemas.py
│   ├── kb_types.py - full doc | chunk | retrieval result
│   └── settings.py
│
├── kb/
│   ├── raw_docs/
│   │   ├── patient_education/
│   │   ├── discharge_instructions/
│   │   ├── medication_guides/
│   │   └── clinic_policies/
│   │
│   ├── processed/
│   │   ├── documents.json
│   │   └── chunks.json
│   │
│   ├── load_docs.py
│   ├── chunk.py.    - split doc text into chunks
│   ├── build_kb.py - runs the whole pipeline: load docs -> chunk -> JSON
│   └── retrieve.py
│
└── main.py -> test the pipeline

Flow: load_docs.py -> doc objs -> chunk.py -> chunk objs -> build_kb.py -> chunks.json -> retrieve.py -> top matching chunks

Medical-specific precautions for step 2
1. Only ingest reviewed docs - Do not mix trusted medical content with random internet text.
2. Keep review metadata - Add fields like: last_reviewed, approved_by, organizaion, version
3. Separate admin vs clinical content - This helps later bcz bot can answer clinic hrs more freely than medication safety questions. 
4. Mark high-risk content - Medication guides and discharge instructions should often be treated as higher-risk sources
5. Plan for expiration - Medical guidance can become outdated. Later you may want the bot to refuse content whose review date is too old. 






