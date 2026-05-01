# Document schema
"""
This file keeps the KB data consistent and structured
Chatbot shouldn't store text as "text", we want each chunk to remember where it came from. 
eg. if the bot retrieves: "Call 911 for chest pain with shortness of breath"
We also want to know:
- which doc it came from
- what tpye of source it was
- whether it was a high-risk medication/discharge source
- what title should be cited later
So, use metadata.
eg.
# Define a model
class MedicalDoc(BaseModel):
    doc_id: str
    title: str
    risk_level: str
# Create an obj
doc = MedicalDoc(doc_id="wound_001", title="Wound Care Instructions", risk_level="high")
print(doc)
# Access the fields
print(doc.doc_id) # wound_001
print(doc.title) # Wound Care Instructions
"""

from pydantic import BaseModel, Field # With BaseModel, you don't need def __init__
from typing import Literal

SourceType = Literal["patient_education", "discharge_instruction", "medication_guide", "clinic_policy"]
RiskLevel = Literal["low", "medium", "high"]
class MedicalDoc(BaseModel):
    # type annotation - Pydantic uses the type info to build fields, validate data, and structure objects
    doc_id: str # It's type annotation; class field; part of class definition; doc_id is a field name, str means its value should be a string
    title: str
    source_type: SourceType
    topic: str
    audience: str="patient"
    risk_level: RiskLevel = "medium"
    #version: str = "1.0"
    #last_reviewed: str | None=None
    text: str

class MedicalChunk(BaseModel):
    chunk_id: str
    doc_id: str
    title: str
    source_type: SourceType
    topic: str
    risk_level: RiskLevel
    text: str
    chunk_index: int
    char_count: int

class RetrievalResult(BaseModel):
    chunk: MedicalChunk
    score: float



