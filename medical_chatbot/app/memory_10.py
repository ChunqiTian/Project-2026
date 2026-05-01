import re
from app.schemas_1 import ConversationState, MemorySlot

MAX_MEMORY_SLOTS = 10

def extract_symptom_duration(user_text: str) -> str | None:
    """
    eg. for 2 days | since yesterday | about 1 month
    """
    patterns = [
            r"\bfor\s+\d+\s+(day|days|week|weeks|month|months|hour|hours)\b",
            r"\bfor\s+(one|two|three|four|five|six|seven|eight|nine|ten)\s+(day|days|week|weeks|month|months|hour|hours)\b",
            r"\bsince\s+(yesterday|last night|this morning|last week)\b",
            r"\babout\s+\d+\s+(day|days|week|weeks|month|months|hour|hours)\b",
        ]
        # d+ - digits | s+ - spaces

    for pattern in patterns:
        match = re.search(pattern, user_text, flags=re.IGNORECASE)
        if match: return match.group(0) # group(0) - the entire string the regex caught
    return None

def extract_mentioned_age(user_text: str) -> str | None:
    """
    Extract age only if the user clearly provides it. 
    eg. "I am 35" | "I'm 42 years old" | "my 5 year old child"
    """
    patterns = [
        r"\bI am\s+(\d{1,3})\b",
        r"\bI'm\s+(\d{1,3})\b",
        r"\b(\d{1,3})\s+years old\b",
        r"\bmy\s+(\d{1,2})\s+year old\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, user_text, flags=re.IGNORECASE)
        if match: return match.group(0)
    return None

def extract_prior_visit_context(user_text: str) -> str | None:
    # Store very small visit context only. 
    # Do not store detailed diagnosis, medication history, or full clinical notes.
    patterns = [
        r"\bdoctor said\b",
        r"\bclinic said\b",
        r"\bI went to urgent care\b",
        r"\bI went to the ER\b",
        r"\bI saw my doctor\b",
        r"\bmy appointment\b",
    ]

    for pattern in patterns:
        if re.search(pattern, user_text, flags=re.IGNORECASE):
            return "User mentioned prior medical visit or clinician advice."
    return None

def extract_prior_visit_context(user_text: str) -> str | None:
    # Store very small visit context only. 
    # Do not store detailed diagnosis, medication history, or full clinical notes. 
    patterns = [
        r"\bdoctor said\b",
        r"\bclinic said\b",
        r"\bI went to urgent care\b",
        r"\bI went to the ER\b",
        r"\bI saw my doctor\b",
        r"\bmy appointment\b",
    ]
    for pattern in patterns:
        if re.search(pattern, user_text, flags=re.IGNORECASE):
            return "User mentioned prior medical visit or clinician advice."
    return None

def extract_previous_question_context(user_text: str) -> str | None:
    # Store a short previous-question topic. 
    # This helps with follow-ups like: "What about this symptom?" | "Can you explain that medicine too?"
    text = user_text.lower()
    if "medicine" in text or "medication" in text or "drug" in text: return "medication question"
    if "symptom" in text or "pain" in text or "fever" in text or "cough" in text: return "symptom question"
    if "doctor" in text or "clinic" in text or "appointment" in text: return "care navigation question"
    return None

def add_memory_slot(state: ConversationState, slot_type: str, value: str, source: str="user_message") -> ConversationState:
    # Add one memory slot while keeping memory small. 
    # If the same slot_type already exists, we replace it - to avoid storing repeated sensitive info.
    new_slots = [slot for slot in state.slots if slot.slot_type != slot_type]
    new_slots.append(MemorySlot(slot_type=slot_type, value=value, source=source))
    if len(new_slots) > MAX_MEMORY_SLOTS: new_slots = new_slots[-MAX_MEMORY_SLOTS:]
    state.slots = new_slots # Keep the most recent n MemorySlot objects total.
    return state

def update_conversation_memory(user_text: str, state: ConversationState | None=None) -> ConversationState:
    # Main memory update funciton.
    # This reads the latest user message and extracts only allowed memory. 
    if state is None: state = ConversationState()
    duration = extract_symptom_duration(user_text)
    if duration: state = add_memory_slot(state=state, slot_type="symptom_duration", value=duration, source="user_message")
    age = extract_mentioned_age(user_text)
    if age: state=add_memory_slot(state=state, slot_type="mentioned_age", value=age, source="user_message")
    prior_visit = extract_prior_visit_context(user_text)
    if prior_visit: state=add_memory_slot(state=state, slot_type="prior_visit_context", value=prior_visit, source="user_message")
    question_context = extract_previous_question_context(user_text)
    if question_context: state=add_memory_slot(state=state, slot_type="previous_question_context", value=question_context, source="user_message")
    state.last_user_question = user_text
    return state

def summarize_memory_for_router(state: ConversationState) -> dict[str, str | None]:
    # Give router a safe summary. 
    # The router should not need the full conversation. It only needs small controlled slots. 
    return {
        "symptom_duration": state.get_slot("symptom_duration"),
        "mentioned_age": state.get_slot("mentioned_age"),
        "prior_visit_context": state.get_slot("prior_visit_context"),
        "previous_question_context": state.get_slot("previous_question_context"),
    }

def is_follow_up_question(user_text: str) -> bool:
    # Detect vague follow-up questions that need memory. 
    # eg. what about this symptom? | what should I do about it? | Can you explain that too?
    patterns = [
        r"\bwhat about\b",
        r"\bwhat should I do about it\b",
        r"\bcan you explain that\b",
        r"\bwhat does that mean\b",
        r"\bis that serious\b",
        r"\bhow about this\b",
        r"\bthat medicine\b",
        r"\bthis symptom\b",
    ]

    for pattern in patterns:
        if re.search(pattern, user_text, flags=re.IGNORECASE): return True
    return False


"""
User_text: I have had a cough for 3 days.
memory layer stores: 
MemorySlot(
    slot_type="symptom_duration",
    value="for 3 days",
    source="user_message"
)
Then the user says: Is that serious?
Without memory, the bot may not know what "that" mean.
With memory, the router can see:
{
    "symptom_duration": "for 3 days",
    "previous_question_context": "symptom question"
}
Then the bot can interpret the follow-up more safely.
"""





