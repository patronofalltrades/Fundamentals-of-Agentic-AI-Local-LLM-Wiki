# Step 8 — Chat with local Gemma

Start Ollama, then run:

```sh
cd "/Users/haniframadhan/Documents/ChatGPT/Fundamentals of Agentic AI project"
python3 wiki.py chat
```

Type one message and press Return. Check a general drafting turn, a shorter follow-up, and a question about the notes. Type `/exit` to finish. Keep your exact chat inputs in a private local file.

`chat` keeps recent turns in memory during one session. A new `chat` command starts a new session. General drafting does not search notes. Requests about the notes search only the three cataloged originals. The CLI shows source paths and citation IDs for note claims. A follow-up that shortens a note-based answer searches the original again and keeps its citation. Optional ideas have a `Suggestion:` label.

Every turn saves its model request, response, retrieval result when used, and timing under `evidence/chat/<session-id>/`. The session file lists the messages. Chat history stays outside the searchable wiki. Type `/exit` to end the session and save its record.

## Quiz

Explain why contextual chat and a fresh cited answer need different handling. Keep your personal answer outside Git.
