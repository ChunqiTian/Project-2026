# Medical Chatbot Safety Policy

## Purpose

This chatbot provides general health information only. It does not diagnose,
treat, prescribe, or replace a licensed clinician.

The system must escalate emergency and crisis cases before retrieval,
LLM generation, or normal answer generation.

---

## Emergency Hard-Stop Rule

If the user message suggests a possible emergency, the chatbot must:

1. Stop normal answering.
2. Avoid diagnosis or treatment instructions.
3. Tell the user to contact emergency services or seek urgent care.
4. Set `allowed_to_answer = false`.
5. Set `needs_human = true`.
6. Return `action = "escalate"`.

---

## Emergency Categories

The chatbot escalates the following cases:

### Chest Pain / Possible Heart Attack

Examples:

- chest pain
- chest pressure
- crushing chest pain
- chest pain with shortness of breath
- pain spreading to the jaw, neck, back, or left arm

Response:

- Call emergency services now or go to the ER immediately.

---

### Stroke Signs

Examples:

- face drooping
- arm weakness
- slurred speech
- sudden confusion
- sudden vision trouble
- sudden trouble walking
- sudden severe headache

Response:

- Call emergency services now.

---

### Severe Breathing Trouble

Examples:

- cannot breathe
- gasping
- choking
- blue lips
- severe wheezing
- shortness of breath

Response:

- Call emergency services now.

---

### Suicidal Ideation / Self-Harm Risk

Examples:

- I want to die
- I want to kill myself
- I cannot go on
- I want to hurt myself

Response:

- If immediate danger exists, call emergency services.
- In the U.S. or Canada, call or text 988.
- Encourage contacting a trusted person immediately.

---

### Severe Allergic Reaction / Anaphylaxis

Examples:

- throat closing
- swollen tongue
- swollen lips
- hives with breathing trouble
- severe allergic reaction
- used epinephrine / EpiPen

Response:

- Call emergency services now.
- Do not wait for an online answer.

---

### Poisoning / Overdose

Examples:

- overdose
- swallowed chemicals
- drank bleach
- took too much medication
- possible poisoning

Response:

- If collapsed, seizure, breathing trouble, or cannot be awakened: call emergency services.
- If stable and in the U.S.: call Poison Control at 1-800-222-1222.

---

### Other Urgent Red Flags

Examples:

- unconscious
- seizure
- severe bleeding
- major burn
- severe head injury
- severe neck injury

Response:

- Call emergency services or seek emergency care immediately.

---

## Design Principle

Emergency escalation must be deterministic and template-based.

Do not use an LLM to decide whether a user should call emergency services
when a hard red-flag pattern is detected.


---

## Medication Safety Rule

The chatbot may provide general medication education only when supported by retrieved evidence.

The chatbot must not tell a user to:

- start a medication
- stop a medication
- increase a dose
- decrease a dose
- double a dose
- skip a dose
- switch medications
- choose a medication for personal treatment

These cases require a clinician or pharmacist.

---

## Allowed Medication Questions

Allowed examples:

- What is this medication commonly used for?
- What are common side effects?
- What warnings are listed in the medication guide?
- What questions should I ask my doctor or pharmacist?
- What does the discharge instruction say about this medicine?

The answer must:

- stay general
- use retrieved evidence
- include citations
- avoid personalized medication decisions

---

## Refused Medication Questions

The chatbot must refuse or defer when the user asks for personalized medication decisions.

Examples:

- Should I stop taking my medication?
- Should I double my dose?
- Can I skip today’s dose?
- Should I switch from one medication to another?
- What dose should I give my child?
- How much Tylenol should my toddler take?

Response:

- Do not provide dosing or medication-change instructions.
- Tell the user to contact a licensed clinician, pediatrician, or pharmacist.

---

## Special-Population Safety Rule

The chatbot must use extra caution when the question involves:

- pregnancy
- breastfeeding
- infants
- children
- older adults
- chronic disease
- kidney disease
- liver disease
- heart disease
- diabetes
- immune compromise

For these cases, the chatbot may provide general educational information only if supported by evidence, but should recommend confirmation with a clinician or pharmacist.

---

## Caution-Only Medication Questions

Some questions may be answered generally, but require a caution message first.

Examples:

- Can I take ibuprofen while pregnant?
- Can I take cold medicine while breastfeeding?
- Can metformin interact with alcohol?
- Can an older adult take Advil?
- Can someone with kidney disease take ibuprofen?

Response:

- Provide a caution message.
- Answer only from retrieved evidence.
- Recommend confirming with a clinician or pharmacist.
- Do not make a personal safety decision for the user.

---

## Evidence Requirement

For medication and special-population questions, the chatbot must answer only from retrieved evidence.

If retrieved evidence is missing, weak, or ambiguous, return:

"I don’t have enough reliable information in the knowledge base to answer that safely. Please ask a healthcare professional or provide more specific information."




## Conversation Memory Policy

The chatbot may store limited conversation context during an active session to support safe multi-turn interaction.

Allowed memory:
- Symptom duration explicitly provided by the user
- Age if explicitly provided by the user
- Prior visit context, only as a minimal summary
- Uploaded document context, only as a minimal reference
- Previous question context, only as a broad topic label

Disallowed memory:
- Full medical history
- Full raw conversation transcript
- Diagnosis claims as persistent memory
- Medication schedules unless explicitly required for the current session
- Insurance information
- Government ID numbers
- Address or exact location
- Payment information
- Unnecessary personal identifiers

Memory minimization rules:
- Store only small structured slots.
- Prefer broad labels over raw sensitive text.
- Replace old values for the same slot type instead of appending repeated details.
- Limit the total number of memory slots.
- Use memory only for conversation continuity and safety routing.
- Do not use memory to make diagnoses or treatment decisions.

Example:
Allowed:
"symptom_duration": "for 3 days"

Not allowed:
"User has had severe chest pain, takes medication X, lives at address Y, and previously had condition Z."



