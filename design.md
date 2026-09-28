# Design choices to verify

Frozen corpus version 2 contains three Hanif-approved, Codex-assisted study notes in the separate assignment Obsidian vault. They credit their reference posts. The exact source paths and hashes are in `data/source-catalog.json`. The frozen corpus passed connected and disconnected four-case answer checks.

## Separation of responsibilities

| Part | Job | Reads | Produces |
| --- | --- | --- | --- |
| Retrieval tool | Search locally indexed **original passages** | `vault/raw/` index | Passage text, source path, section, stable citation ID |
| RAG workflow | Answer a standalone factual question using retrieved passages | User question and retrieval results | Neutral answer or insufficient-evidence response, with citations |
| Harness | Select mode, assemble prompts, call local Gemma, validate citations, handle errors, save evidence | CLI request, mode instructions, optional chat history, retrieval tool | Displayed result and run record |
| Wiki ingestion | Turn an original note into a draft linked page for review | One unchanged raw note, local Gemma, existing page catalog | Descriptive Markdown draft and updated index |

The required modes differ at the harness boundary:

- `search` stops after retrieval and works while the model is unavailable.
- `ask` does not read chat history. It retrieves, generates with research rules, then checks that cited IDs were in the retrieved set. We still inspect semantic support manually in evaluations.
- `chat` uses recent conversation for follow-ups. It retrieves only for requests about the user's notes and cites note-derived claims. Suggestions are identified as suggestions.

The CLI defaults to local inference. No hosted embeddings, remote search, or cloud fallback will be included in the required path.

## Initial implementation choice

Use Python's standard library and SQLite FTS5 for a local keyword index. Index originals only, preserving source paths and section labels. This avoids an embedding download and makes the offline dependency chain easy to audit. If the three evaluation questions expose a retrieval gap, record it before adjusting indexing or adding a local embedding model.

Use Ollama's local `/api/chat` endpoint with `gemma4:e2b-mlx`. Keep the working context small despite the model's advertised maximum. Record exact runtime settings with every evidence card.

## Evidence order

1. Freeze the three sources in `data/source-catalog.json` and keep the exact four question expectations in the Git-ignored local archive before running retrieval. The public `evaluation/expectations.md` records case roles only.
2. Inspect raw `search` hits for each question.
3. Run `ask` and assess each claim and citation against the originals.
4. Check ordinary chat, follow-up chat, raw search, and ask isolation.
5. Disconnect internet, restart the CLI, ingest a local source, and repeat the required tests. Preserve actual terminal output and record memory use and timing.
6. Inspect the final vault in Obsidian and capture the required three views.

This order guided the implementation. Earlier failed results are preserved in the private archive; the frozen-corpus connected result is summarized publicly.

## Implemented ingestion boundary

`wiki.py ingest` reads only cataloged originals whose SHA-256 hashes match. The harness labels unchanged source paragraphs. A local Gemma call produces structured draft text and selects a supporting passage ID for each point. The harness validates those IDs, copies exact evidence from the original, uses the page plan for file names, and writes stable wiki paths. The page plan supplies editorial related-page links; Gemma does not invent those links.

The ingestion context is 8,192 tokens, with a 1,200-token output limit and a conservative input byte budget. This differs from the initial 4,096-token smoke test. Larger input is rejected rather than silently shortened. Chunked ingestion remains future work.

The client uses a fixed loopback address, checks that the model is installed locally, and rejects cloud-backed model metadata. There is no proxy or redirect path in the client. This design is separate from the required disconnected-and-restarted demonstration.

Draft validation does not establish truth. Exact quotations can support inaccurate source claims. Version-1 tests exposed this problem: a draft repeated unverified percentages from an aggregator note, and two other attempts altered quotations. We preserved those failures in the private archive, revised the prompt, and moved quotation extraction into code by using passage IDs. Hanif approved the three version-2 source notes; the three generated wiki pages were then checked against their source lines and marked reviewed.

## Implemented retrieval

`wiki.py search` verifies the cataloged originals, then passes only those texts to `retrieval.py`. Search never reads evaluation expectations, wiki pages, chat history, or quizzes. It strips frontmatter and URL-only/navigation blocks from indexing. It groups paragraphs within headings toward 220 words with one-paragraph overlap; a single oversized paragraph stays intact. Returned text preserves source line ranges. Citation IDs include source ID, source hash prefix, and line range.

The cache is SQLite FTS5 with Porter stemming and BM25 ranking. Title and section receive less weight than passage text. Query tokens are literal OR terms. Search limits default to five; ask defaults to three passages and allows an explicit limit. Search removes a shorter same-source passage when its complete normalized text appears inside a longer candidate, so duplicate summaries do not use multiple result slots. Hash and metadata signatures detect source or catalog changes, and returned passages are checked against original lines.

Version-1 retrieval tests found a gap for a budget passage. A small term expansion for “resources” and “unlimited” corrected it. On the version-2 candidate corpus, Q1 initially missed the five-pattern passage; a visible “architecture” expansion corrected that gap. The expansion terms are recorded in result JSON. All three answerable candidate questions now have full expected line coverage in the top five. These are development-set checks after tuning, not a held-out accuracy estimate. Ranking can still place a less useful match first.

Gemma was unloaded before and after a fresh index build and search. A code test also forbids network and model calls during search. The connected check kept Ollama available. The later disconnected run repeated search after unloading Gemma and recorded its output in the offline proof.

## Implemented ask

`wiki.py ask` sends one new factual question, without chat history, and the retrieved original passages to local Gemma. It checks that the response matches a JSON schema, rejects citations that were not retrieved, and returns an insufficient-evidence response when no passage matches. The prompt requires an abstention when retrieved text does not support every part of a question. If Gemma flags insufficient evidence but returns a field-name echo instead of an explanation, the harness replaces only that unhelpful text with a fixed, claim-free explanation and records the normalization. The raw model response stays saved. The harness also saves retrieval, model identity, exact request, response, and status. A valid citation ID only proves membership in the retrieved set; human review checks whether the passage actually supports the claim.

The candidate evaluation uses a question set outside the searchable corpus. It checks expected line coverage, expected source citations, supported versus unsupported behavior, and citation membership. Q1 uses its top passage; Q2–Q4 use three. The first version-2 model run failed several checks, so we shortened the ask prompt and reduced Q1's unrelated context before retesting. The earlier version-1 results are archived locally. Two disconnected runs completed, and the latest answers were checked against cited original lines.

## Implemented chat

`wiki.py chat` keeps recent user and assistant turns within one terminal session. It routes requests about the notes to original-passage search. Casual brainstorming and drafting send no retrieved notes and use plain text generation. Note-based turns use structured JSON so the harness can reject citations outside that turn's retrieved set. A request to shorten a cited note answer searches the original again; the answer keeps its source. The harness marks optional ideas as suggestions and saves each turn's request, response, retrieval status, timing, and outcome outside the vault.

Version-1 live chat attempts and their corrections remain in the private archive. Chat history is never added to the retrieval index. Connected and disconnected version-2 chat checks completed on the frozen corpus.
