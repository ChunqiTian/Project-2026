from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rag.answer_generator_5 import (
    generate_answer,
    format_citations_for_display,
)


"""
mock_results = [
    {
        "chunk": {
            "doc_id": "fever_care",
            "chunk_id": "chunk_0",
            "text": "A mild fever can often be managed with rest and fluids."
        },
        "score": 0.78,
    }
]
"""


mock_results = [
    {
        "chunk": {
            "doc_id": "fever_care",
            "chunk_id": "chunk_0",
            "text": "A mild fever can often be managed with rest and fluids."
        },
        "score": 0.12,
    }
]



response = generate_answer(
    user_text="What should I do for a mild fever?",
    retrieved_chunks=mock_results,
)

print(response.answer)
print(response.confidence)
print(format_citations_for_display(response.citations))


# test_ui_helpers_5.py

from app.schemas_1 import AnswerResponse, Citation
from app.ui_helpers_5 import format_answer_block


response = AnswerResponse(
    answer="A mild fever can often be managed with rest and fluids.",
    citations=[
        Citation(doc_id="fever_care", chunk_id="chunk_0")
    ],
    confidence=0.78,
    grounded=True,
    reason="answered_from_retrieved_evidence",
)

print(format_answer_block(response))








