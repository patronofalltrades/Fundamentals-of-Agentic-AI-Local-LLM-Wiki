# Learning checkpoints

While coding and preparing this assignment, I used a short interactive quiz to check my own understanding. I answered in my own words, then compared each idea with the notes and the behavior of the CLI.

- Retrieval finds a passage in the original notes.
- Gemma uses retrieved passages to write a RAG answer.
- The Python harness selects commands, calls search and Gemma, and checks citation IDs.
- A valid citation ID shows that a passage was retrieved. It does not prove that the passage supports the answer.
- `ask` starts a new question. `chat` keeps recent turns in one session.

The full quiz conversation stays local because it can contain my prompt text and personal answers. The [implementation plan](../IMPLEMENTATION_PLAN.md) shows the quiz checkpoints.

The quiz was a learning check for me. The [question-and-answer review](../evidence/question-and-answer-review.md) tests the wiki system. These are separate checks.
