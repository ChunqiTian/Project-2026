# This file is for display formatting only. 
"""
It should not do retrieval.
It should not generate medical answers.
It only makes the answer easier to show in CLI or Streamlit later.
"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.schemas_1 import AnswerResponse, Citation

def format_citation(citation: Citation) -> str:
    """
    Convert a Citation obj into display text. 
    eg. Citation(doc_id="fever_care", chunk_id="chunk_0") becomes: [fever_care: chunk_0]
    """
    return f"[{citation.doc_id}:{citation.chunk_id}]"

def format_citations(citations: list[Citation]) -> str:
    # Convert a list of citations into one readable string
    if not citations: return "No citations available."
    citation_texts = []
    for citation in citations:
        citation_texts.append(format_citation(citation))
    return ", ".join((citation_texts))

def format_confidence(confidence: float) -> str:
    # Convert confidence score into a user-friendly label.
    percent = round((confidence * 100))
    if confidence >= 0.70: label = "High"
    elif confidence >= 0.40: label = "Medium"
    else: label = "low"
    return f"{label} confidence ({percent}%)"

def format_answer_block(response: AnswerResponse) -> str:
    # Format the final answer for display in CLI or UI.
    citations_text = format_citations(response.citations)
    confidence_text = format_confidence(response.confidence)
    return (
        f"Answer:\n{response.answer}\n\n"
        f"Citations: {citations_text}\n"
        f"Confidence: {confidence_text}\n"
        f"Grounded: {response.grounded}\n"
        f"Reason: {response.reason}"
    )


# Step 11 - UI
from typing import Any

def response_to_dict(response: Any) -> dict[str, Any]:
    """
    Convert diff response formats into a normal dict
    Your bot may return: a PYdantic model, eg. BotResponse | a normal Pythond dict | a plain string
    The Streamlit UI should work with all of them
    """
    if hasattr(response, "model_dump"): return response.model_dump() # Case 1 - Pydantic v2 model
    if hasattr(response, "dict"): return response.dict() # Case 2 - Pydantic v1 model
    if isinstance(response, dict): return response # Case 3 - A dict
    return { # Case 4 - Plain string fallback
        "answer": str(response), 
        "risk_level": "unknown",
        "action": "answer",
        "confidence": None,
        "citations": [],
        "needs_human": False, 
        "safe_to_answer": True, 
        "reason": None,
    }

def get_risk_badge_text(risk_level: str | None) -> str:
    # Convert risk level into a simple badge label. 
    if risk_level is None: return "⚪ Risk: Unknown" 
    risk = risk_level.lower()
    if risk in ["low", "safe"]: return "🟢 Risk: Low"
    if risk in ["medium", "moderate"]: return "🟡 Risk: Medium"
    if risk in ["high"]: return "🟠 Risk: High"
    if risk in ["emergency", "critical"]: return "🔴 Risk: Emergency"
    return f"⚪ Risk: {risk_level}"

def get_action_badge_text(action: str | None) -> str:
    # Convert bot acton into a readable UI label. 
    if action is None: return "Action: Unknown"
    action = action.lower()
    if action == "answer": return "Answer allowed"
    if action == "answer_with_caution": return "Answer with caution"
    if action == "refuse": return "Refused"
    if action == "escalate": return "Escalation needed"
    if action == "emergency": return "Emergency escalation"
    return f"Action: {action}"

def format_confidence(confidence: float | None) -> str:
    # Format confidence / evidence strength for the UI. 
    if confidence is None: return "Evidence strength: Not available"
    try: confidence_float = float(confidence)
    except (TypeError, ValueError): return "Evidence strength: Not available"
    percentage = round(confidence_float * 100, 1)
    if confidence_float >= 0.75: label = "Strong"
    elif confidence_float >= 0.45: label = "Moderate"
    else: label = "Weak"
    return f"Evidence strength: {label} ({percentage}%)"

def normalize_citations(citations: Any) -> list[str]:
    # Normalize citations into a list of strings. 
    # Your citations may come back as: list[str], list[dict], list[Pydantic Citation objects]
    if not citations: return []
    normalized = []
    for citation in citations:
        if isinstance(citation, str): normalized.append(citation)
        elif hasattr(citation, "model_dump"): 
            data = citation.model_dump()
            normalized.append(str(data))
        elif hasattr(citation, "dict"):
            data = citation.dict()
            normalized.append(str(data))
        elif isinstance(citation, dict):
            normalized.append(str(citation))
    return normalized
  
