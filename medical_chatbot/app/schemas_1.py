# schemas_1_3_5_6_7_10.py
# This file stores the response schema and the allowed label types.

from typing import Literal, Optional

from pydantic import BaseModel, Field

IntentType = Literal[
    "general_health_info",
    "symptom_check",
    "medication_question",
    "administrative",
    "mental_health_support",
    "self_harm_risk",
    "emergency",
    "unknown",
]
RiskLevel = Literal["low", "medium", "high", "emergency"]

ActionType = Literal[
    "answer",
    "answer_with_caution",
    "refuse",
    "escalate_clinician",
    "escalate_emergency",
    "support_crisis",
]




"""
# Step 3 
MedicalDoc - Represents the whole raw doc
    eg. full medication guide | full clinic policy | full discharge instruction page
MedicalChunk - Represents one small searchable piece of that doc
    eg. one paragraph on dosage | one paragraph on warning signs | one policy section on appointments

"""

class MedicalDocument(BaseModel):
    doc_id: str = Field(..., description="Unique ID for the source document")
    title: str = Field(..., description="Human-readable title of the document")
    source_type: str = Field(..., description="Type of medical source, e.g. discharge_instruction")
    text: str = Field(..., description="Full raw text of the document")
    section: Optional[str] = Field(default=None, description="Optional section label")


class MedicalChunk(BaseModel):
    chunk_id: str = Field(..., description="Unique ID for this chunk")
    doc_id: str = Field(..., description="ID of the parent document")
    title: str = Field(..., description="Title of the parent document")
    source_type: str = Field(..., description="Type of source document")
    section: Optional[str] = Field(default=None, description="Section label if known")
    text: str = Field(..., description="Chunk text")
    char_count: int = Field(..., description="Character length of the chunk")


# step 5 Generate answers with citation - update
# We want answer in structure: answer | citations | confidence | grounded | reason

class Citation(BaseModel): # this stores where answer came from
    doc_id: str = Field(..., description="The source document ID")
    chunk_id: str = Field(..., description="The retrieved chunk ID")
    

class AnswerResponse(BaseModel): # This is the final structured output
    answer: str = Field(..., description="The generated answer shown to the user")
    citations: list[Citation] = Field(default_factory=list, description="List of citations used to support the answer")
        # If you used default=[], every instance of your class would share the exact same list in memory. 
        # By using default_factory=list, Python calls the list() function to create a brand-new, empty list every time you create a new object.
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    grounded: bool = Field(..., description="Whether the answer is supported by retrieved evidence")
    reason: str = Field(..., description="Reason for answering or refusing")


# Step 6 - add refusal-related fields to your response schema
class RetrievedChunk(BaseModel):
    doc_id: str
    chunk_id: str
    text: str
    score: float


# Step 7 - escalation
# Add escalation fields to your structured response
EscalationType = Literal["none", "emergency_services", "er_now", "poison_control", "crisis_line", "immediate_clinician"]

class BotResponse(BaseModel):
    intent: IntentType
    risk_level: RiskLevel
    action: ActionType

    answer: str
    citations: list[Citation] = Field(default_factory=list)

    needs_human: bool = False
    safe_to_answer: bool = True
    allowed_to_answer: bool = True

    confidence: float = 0.0
    reason: str
   
    refusal_reason: Optional[str] = None
    escalation_type: EscalationType = None

    disclaimer: Optional[str] = None
    follow_up: Optional[str] = None
    detected_flags: list[str] = Field(default_factory=list)

    safety_note: Optional[str] = None # Extra structured warning for logs/debugging

# Step 10 - memory
MemorySlotType = Literal["symptom_duration", "mentioned_age", "prior_visit_context", 
                         "uploaded_document_context", "previous_question_context"]

class MemorySlot(BaseModel):
    """
    One controlled piece of conversation memory. 
    We do not store full medical history here; only store small, allowed context that helps with safe follow-up questions.
    """
    slot_type: MemorySlotType
    value: str
    source: Literal["user_message", "uploaded_document", "bot_response"] = "user_message"

class ConversationState(BaseModel):
    """
    Controlled state for one conversation. 
    This should stay small. Do not store full raw conversation text here. 
    """
    slots: list[MemorySlot] = Field(default_factory=list)
        # Not: slots: list[MemorySlot] = [] -- bcz lists are mutable. 
        # slots: list[MemorySlot] = Field(default_factory=list) # Every new ConversationState gets its own fresh empty list. 
    last_user_question: str | None=None
    last_bot_topic: str | None=None

    def get_slot(self, slot_type: MemorySlotType) -> str | None:
        for slot in reversed(self.slots):
            if slot.slot_type == slot_type:
                return slot.value
        return None



    
