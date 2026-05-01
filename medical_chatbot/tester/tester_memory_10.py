from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.schemas_1 import ConversationState
from app.memory_10 import update_conversation_memory, summarize_memory_for_router, is_follow_up_question
from app.router_8 import enrich_question_with_memory

def test_memory_flow():
    state = ConversationState()
    user_1 = "I have had a cough for 3 days."
    state = update_conversation_memory(user_1, state)

    print("After first message:")
    print(state.model_dump()) # model_dump() - convert a model instance into a standard dict

    user_2 = "Is that serious?"
    print("\nIs follow-up?")
    print(is_follow_up_question(user_2))

    enriched = enrich_question_with_memory(user_2, state)

    print("\nEnriched question:")
    print(enriched)

    print("\nSafe router memory summary:")
    print(summarize_memory_for_router(state))

if __name__ == "__main__":
    test_memory_flow()




