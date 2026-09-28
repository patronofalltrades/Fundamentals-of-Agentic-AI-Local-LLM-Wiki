# Assignment 4 handover

The final handover is **one public GitHub repository URL** through the course portal. The local implementation and evidence are complete; public-file review, GitHub publication, and course submission remain.

**Status checked 2026-09-28:** Hanif approved the three rewritten study notes in the separate assignment Obsidian vault. Local Gemma generated three linked wiki pages. Prompt-free connected and disconnected evaluation reports and the required Obsidian screenshots are ready. Two disconnected runs completed; the latest passed ingestion, 35 code tests, four ask cases, and chat checks. Its cited answers were checked against the originals. Most project files are still uncommitted locally.

## What exists

- `wiki.py` and `retrieval.py` implement the CLI, local Gemma calls, ingestion, search, ask, chat, citation checks, and saved run records.
- `vault/raw/` has three approved study notes. `vault/wiki/` has three reviewed, linked pages. `vault/index.md` links the pages and notes.
- `data/source-catalog.json` has frozen source hashes. `evaluation/expectations.md` describes the four test cases without reproducing the exact private questions.
- Version-1 connected runs and full bookmark copies are in the Git-ignored `private-archive/corpus-v1/`. They are not evidence for the new corpus.
- `evidence/connected-evaluation.md` and `evidence/offline/README.md` report the four-case checks without private question or answer text. The raw records and quiz conversation stay in Git-ignored local storage. `evidence/offline/completed-offline-steps.gif` shows the safe completed-run steps; the first failed attempt remains documented.

## What remains

1. [x] **Capture Obsidian proof.** `open-note.png`, `index.png`, and `graph.png` are saved in `evidence/obsidian/`, along with five supplementary source/page screenshots. The index-to-page and page-to-original links were checked in Obsidian. The graph screenshot shows all seven named files connected.
2. [x] **Prove offline operation.** Two disconnected runs completed. The latest log folder, status, output, timing, memory snapshot, and safe GIF are recorded. The first failed attempt and both full recordings remain private.
3. [x] **Finish the public evidence.** The prompt-free offline report, measured timings and memory snapshot, limitation, and improvement are in the README and evidence notes. Exact personal test and chat inputs remain in Git-ignored local storage.
4. [ ] **Publish and submit.** Review staged files and the existing public commit history for private text. Commit and push the safe repo. Verify its public view while signed out. Submit its URL through bCourses.

The original bookmark notes in Hanif's Brain were not edited. The new study notes currently live only in the separate assignment vault.
