# Design choices to verify

The source corpus and final model choice remain open until the owner selects publishable notes and we measure the local run.

## Separation of responsibilities

| Part | Job | Reads | Produces |
| --- | --- | --- | --- |
| Retrieval tool | Search locally indexed **original passages** | `vault/raw/` index | Passage text, source path, section, stable citation ID |
| RAG workflow | Answer a standalone factual question using retrieved passages | User question and retrieval results | Neutral answer or insufficient-evidence response, with citations |
| Harness | Select mode, assemble prompts, call local Gemma, validate citations, handle errors, save evidence | CLI request, mode instructions, optional chat history, retrieval tool | Displayed result and run record |
| Wiki ingestion | Turn an original note into a reviewed, linked human page | One unchanged raw note, local Gemma, existing page catalog | Descriptive Markdown page and updated index |

The required modes differ at the harness boundary:

- `search` stops after retrieval and works while the model is unavailable.
- `ask` does not read chat history. It retrieves, generates with research rules, then checks that cited IDs were in the retrieved set. We still inspect semantic support manually in evaluations.
- `chat` uses recent conversation for follow-ups. It retrieves only for requests about the user's notes and cites note-derived claims. Suggestions are identified as suggestions.

The CLI defaults to local inference. No hosted embeddings, remote search, or cloud fallback will be included in the required path.

## Initial implementation choice

Use Python's standard library and SQLite FTS5 for a local keyword index. Index originals only, preserving source paths and section labels. This avoids an embedding download and makes the offline dependency chain easy to audit. If the three evaluation questions expose a retrieval gap, record it before adjusting indexing or adding a local embedding model.

Use Ollama's local `/api/chat` endpoint with `gemma4:e2b-mlx`. Keep the working context small despite the model's advertised maximum. Record exact runtime settings with every evidence card.

## Evidence order

1. Freeze the three sources and four question expectations in `evaluation/expectations.md` before running retrieval.
2. Inspect raw `search` hits for each question.
3. Run `ask` and assess each claim and citation against the originals.
4. Check ordinary chat, follow-up chat, raw search, and ask isolation.
5. Disconnect internet, restart the CLI, ingest a local source, and repeat the required tests. Preserve actual terminal output and record memory use and timing.
6. Inspect the final vault in Obsidian and capture the required three views.

This is a proposed design. We will revise it when measured behavior warrants a change, preserving earlier failed results as evidence.
