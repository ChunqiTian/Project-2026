Step 10 - Multi-turn conversation memory

Let the bot track safe context across turns, eg
- symptom duration | age | prior visit context | uploaded doc context
But keep this tightly controlled bcz medical data is sensitive. 

Goal: Track safe context across turns.

How this memory works? (router.py)
eg. I have had a cough for 3 days.
The memory layer stores:
memorySlot(slot_type="symptom_duration", value="for 3 days", source="user_message")
Then later the user says: Is that serious?
Without memory, the bot may not know what "that" means.
With memory, the router can see:
{"symptom_duration": "for 3 dayss", "previous_question_context": "symtom question"}
Then the bot can interpret the follow-up more safely.

Design:
uer message -> update_conversation_memory() -> controlled conversationSate-> enrich_question_with_memory()
    -> intent / risk / router / answer generator
Note: the memory layer should only help the bot understand what the user is referring to. 

Order:
1. Add MemorySlot and ConversationState to schemas_1.py
2. Create memory_10.py (where controlled memory logic lives)
3. Test memory_10.py alone
4. Add enrich_question_with_memory() to router_8.py
5. Update handle_message() to return response + state
6. Add memory policy to doc/safety_policy.md

File:
- app/memory.py - Stores controlled conversation state. 
    - eg. symptom duration | mentioned age | uploaded doc context | previous question context 
- app/schemas.py - may include: conversation state | memory slot
- app/router.py - may use memory to interpret follow-up questions.
    - eg. "What about this symptom?", "Can you explain that medicine too?"
- docs/safety_policy.md - Doc what memory is allowed and what is minimized

In memory.py
Field(default_factory=list) is a technique used in Python dataclasses (and similar libraries like Pydantic) to initialize a new, empty list for every new instance of a class

from dataclasses import dataclass, field

@dataclass
class User:
    name: str
    # Each user gets a brand new, empty list
    items: list[str] = field(default_factory=list)

- Usage
u1 = User("Alice")
u2 = User("Bob")

u1.items.append("laptop")

print(u1.items)  # Output: ['laptop']
print(u2.items)  # Output: [] (Correct! u2 is not affected by u1)









