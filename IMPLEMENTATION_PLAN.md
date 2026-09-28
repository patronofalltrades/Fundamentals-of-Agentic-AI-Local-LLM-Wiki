# Implementation plan

This plan uses short, direct sentences. Each step has one result to check. The [assignment brief](https://docs.google.com/document/d/1p9vRwgdT9cmSxwdl4ylHKi7dcBZFSmVpILcFMQS33Vs/edit) gives the full requirements.

**Goal:** Make one local personal wiki. Use local Gemma to make wiki pages and answer questions from original notes. Show the result in a CLI and in Obsidian.

**Current state:**

- The Mac has an Apple M5 chip and 16 GB of memory.
- Ollama, Obsidian, and `gemma4:e2b-mlx` are installed.
- Hanif approved three rewritten notes in the separate assignment vault.
- The source catalog records their fixed hashes.
- The CLI has `ingest`, `search`, `ask`, `chat`, and `help` commands.
- Local Gemma made three linked wiki pages.
- The four answer cases, search, chat, and 35 code tests passed online and offline.
- The Obsidian screenshots and two completed offline runs are saved.
- The public repo includes a safe GIF and a question-and-answer review.

**Next action:** Submit the [public repository URL](https://github.com/patronofalltrades/Fundamentals-of-Agentic-AI-Local-LLM-Wiki) in bCourses.

## Progress checklist

- [x] **Steps 1–4:** Select three notes, record the model, set test cases, and make separate folders.
- [x] **Steps 5–6:** Make three linked wiki pages and search the originals.
- [x] **Steps 7–10:** Build the CLI. Test ask, chat, search, and code.
- [x] **Step 11:** Open the vault in Obsidian. Save the required screenshots.
- [x] **Step 12:** Disconnect, restart, and run the offline test twice.
- [x] **Step 13:** Publish the code, notes, wiki, and safe evidence.
- [ ] **Final action:** Submit the public repository URL in bCourses.

The exact test and chat inputs remain in Git-ignored local files.

```mermaid
flowchart LR
    A["1. Freeze<br/>three notes"] --> B["2. Build<br/>wiki and CLI"]
    B --> C["3. Test<br/>answers and chat"]
    C --> D["4. Prove<br/>offline use"]
    D --> E["5. Publish<br/>and submit"]
```

## Step 1 — Select the notes

1. Select at least three original notes. Use notes that you can put in a public repository.
2. State what the wiki must help you find or remember.
3. Copy the notes to `vault/raw/`. Do not change the text in these copies.
4. Record the title, path, and file hash of each note in a source list.

**Check:** Three original files are present. Each file is safe to share. The wiki has a clear subject.

## Step 2 — Record the local model

1. Record the Mac model, chip, memory, operating system, and free disk space.
2. Record the Ollama version and the exact Gemma model tag.
3. Record the model quantization and the model file size.
4. Set a small working context for the first test. Use local mode as the default.
5. Run one short model request. Record the response time and memory use.

**Check:** Gemma gives a response on this Mac. The record names the model and the measured result. A model test alone is not offline proof.

## Step 3 — Write the test questions

1. Read the three original notes.
2. Write three questions that the notes can answer.
3. Write one question that the notes cannot answer.
4. Record the expected source passage for each answerable question.
5. Keep the original evaluation file outside the wiki. Record case roles and expected evidence in `evaluation/expectations.md`. The exact four questions were later approved for the public [review](evidence/question-and-answer-review.md).

**Check:** The four questions and expected results exist before the retrieval test.

**Quiz 1:** What does the retrieval tool do? What does RAG do? What does the harness do? Record your answer in `learning/quiz-log.md`.

## Step 4 — Make the project structure

1. Put original notes in `vault/raw/`.
2. Put wiki pages in `vault/wiki/`. Put the human index in `vault/index.md`.
3. Put code, search data, prompts, tests, and run records outside `vault/`.
4. Add a `.gitignore` rule for model files, local databases, secrets, and temporary files.

**Check:** The search code cannot read the test answer key, chat logs, or generated wiki text as original evidence.

## Step 5 — Make wiki ingestion

1. Make an `ingest` command that reads one or more original notes.
2. Send each note, or a labeled part of it, to local Gemma.
3. Save a draft wiki page with a short subject name and a source reference.
4. Check each draft against the original note. Correct each false or unclear claim.
5. Add useful links between related pages. Update `vault/index.md`.
6. Ingest one note a second time. Check that the command updates its page without a duplicate.

**Check:** Each page has a readable file name, a matching first heading, a source reference, and useful content. Related pages have working links.

## Step 6 — Make local search

1. Split original notes into passages. Keep the source path and section with each passage.
2. Build a local search index from the original passages only.
3. Make `search` return passages and source paths. Do not call Gemma in this mode.
4. Run `search` for the three answerable questions.
5. Check if each expected passage appears. Record misses before you change search.

**Check:** Search works when Gemma is off. Search shows original text and its location.

**Quiz 2:** If `search` returns the wrong passage, which part must you check first? Explain why.

## Step 7 — Make grounded answers

1. Make `ask` start with a new question. Do not add chat history.
2. Retrieve relevant original passages.
3. Send the question and labeled passages to local Gemma.
4. Require a direct answer with source citations.
5. Check that each citation names a passage that was retrieved.
6. Return an insufficient-evidence response when the passages do not support an answer.

**Check (passed locally with Gemma):** Three supported questions get cited answers. The unsupported question gets an honest limit. Check each material claim against its cited text. See `evidence/ask/README.md` and the final evaluation record.

## Step 8 — Make personal chat

1. Give `chat` a clear voice and a true list of its functions.
2. Keep recent chat turns for follow-up requests.
3. Search notes only when the request needs note evidence.
4. Cite claims that come from notes. Mark new ideas as suggestions.
5. Test a casual request, a short draft, and a shorter follow-up.

**Check (passed locally with Gemma):** Chat handles a casual request without an unrelated note search. A follow-up uses the prior chat turn. A note-based follow-up retrieves and cites its source again. Chat text does not become evidence for `ask`. See `evidence/chat/README.md`.

**Quiz 3:** Why can `chat` use history while `ask` must start without it?

## Step 9 — Complete the CLI

1. Connect `help`, `ingest`, `search`, `ask`, and `chat` to the harness.
2. Show the model tag and local mode in model results.
3. Show a clear error if a source file or the local model is unavailable.
4. Save actual outputs and run settings outside the wiki.

**Check (passed locally, including the disconnected run):** A reader can run every required command from the README. The commands use the local model endpoint. Step 12 records the disconnected proof.

## Step 10 — Test and correct the result

1. Run the four `ask` questions one at a time.
2. Save the retrieved passages, actual Gemma answer, citations, and model settings for each question.
3. Check retrieval before you judge the answer.
4. Check every material claim against the cited passage.
5. Run the chat and search checks. Save the transcript.
6. Keep the first failed result when you make a change. Run the affected test again.

**Check (passed locally with Gemma):** The record shows expected evidence, actual evidence, actual answers, and an honest result for each test. Repeat these checks after disconnecting and restarting in Step 12.

## Step 11 — Check the wiki in Obsidian

1. Open `vault/` as the Obsidian vault.
2. Open `index.md`. Follow a link to a wiki page.
3. Follow one related-page link and one source reference.
4. Check the page names, headings, and graph labels.
5. Take three screenshots: an open note, the page list or index, and the graph.

**Check:** The links work. The screenshots show readable notes and meaningful connections.

## Step 12 — Make the offline proof

Use the [offline walkthrough](learning/offline-walkthrough.md) and `scripts/offline-proof.sh` to repeat the test.

- The first attempt stopped before the ask checks. A private file was not stored on local disk.
- Two later disconnected runs completed.
- The [safe GIF](evidence/offline/completed-offline-steps.gif) shows the main steps.
- The [offline report](evidence/offline/README.md) gives run results. The [question and answer review](evidence/question-and-answer-review.md) shows the four public test questions and displayed answers.
- Raw records remain private.

1. Confirm that the model and all software packages are on the Mac.
2. Disconnect the Mac from the internet. Restart the CLI.
3. Ingest a local source. Run the four `ask` questions.
4. Run the chat and search checks.
5. Record the terminal session or take clear screenshots.
6. Record the memory use and response time for ingestion and one answer.

**Check:** All required commands work after the disconnect and restart. The record shows the commands and actual results. No cloud fallback is active.

**Quiz 4:** Why does a restart after the disconnect give stronger proof than a test that starts online?

## Step 13 — Make the submission clear

1. Write the README as the entry point.
2. Add the exact setup commands, model choice, device facts, architecture, and known limit.
3. Link the source list, wiki, question-and-answer review, offline proof summary, and Obsidian screenshots.
4. Check the repository for secrets and private data.
5. Publish one public GitHub repository. Open it while signed out and check the links.
6. Submit that repository URL in bCourses.

**Final check:** The repository contains the code, three original notes, reviewed wiki pages, question-and-answer review, offline proof summary, screenshots, and a complete README. The public links work.

## Work rule

Do one step at a time. Record a real result for each check. Do not replace a failed result with a planned result. Answer each quiz after the related work.
