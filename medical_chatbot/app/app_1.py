# This one is optional, but nice for quick terminal testing. 
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tester.main_obsolete import handle_message

def run_chat():
    print("Medical chatbot Step 1 demo")
    print("Type 'quit' to stop.\n")

    while True:
        user_text = input("You: ").strip()
        if user_text.lower() in {"quit", "exit"}:
            print("Goodbye.")
            break
        result = handle_message(user_text)
        print("\nBot structured output:")
        print(result.model_dump_json(indent=2))
        print()

if __name__ == "__main__":
    run_chat()






