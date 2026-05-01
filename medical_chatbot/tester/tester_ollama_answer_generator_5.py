from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rag.ollama_answer_generator_5 import generate_ollama_answer
from app.ui_helpers_5 import format_answer_block


def test_strong_evidence():
    mock_results = [
        {
            "chunk": {
                "doc_id": "fever_care",
                "chunk_id": "chunk_0",
                "text": (
                    "A mild fever can often be managed with rest and fluids. "
                    "Seek medical care if fever is very high, lasts several days, "
                    "or comes with severe symptoms."
                ),
            },
            "score": 0.82,
        }
    ]

    response = generate_ollama_answer(
        user_text="What should I do for a mild fever?",
        retrieved_chunks=mock_results,
    )

    print(format_answer_block(response))


def test_weak_evidence():
    mock_results = [
        {
            "chunk": {
                "doc_id": "fever_care",
                "chunk_id": "chunk_0",
                "text": "A mild fever can often be managed with rest and fluids.",
            },
            "score": 0.12,
        }
    ]

    response = generate_ollama_answer(
        user_text="Can fever cause chest pain?",
        retrieved_chunks=mock_results,
    )

    print(format_answer_block(response))


if __name__ == "__main__":
    print("\n--- Strong Evidence Test ---")
    test_strong_evidence()

    print("\n--- Weak Evidence Test ---")
    test_weak_evidence()
