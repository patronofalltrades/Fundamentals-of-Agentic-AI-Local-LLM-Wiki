# Personal Wiki with Local Gemma + RAG

Assignment 4 for Fundamentals of Agentic AI. This repository is being built as a learning project. The [assignment brief](https://docs.google.com/document/d/1p9vRwgdT9cmSxwdl4ylHKi7dcBZFSmVpILcFMQS33Vs/edit) governs the final deliverable.

Read the [step-by-step implementation plan](IMPLEMENTATION_PLAN.md) for the build order, checks, and quiz points.

## Current status

Preparation is in progress. This repository does **not** yet contain the required personal sources, working CLI, offline evidence, or Obsidian screenshots. Do not submit it in this state.

This is the initial public repository. The three source notes will be selected before any wiki pages or evaluation results are added.

The target computer is a MacBook Air with an Apple M5 chip and 16 GB of unified memory. Ollama 0.34.3 and Obsidian are installed. `gemma4:e2b-mlx` is already downloaded locally; Ollama reports Gemma 4 E2B, `nvfp4` quantization, a 131,072-token model context limit, and a 7.5 GB download. A local CLI smoke test returned `ready`; Ollama reported 7.4 GB loaded on the GPU with a 4,096-token runtime context. This model check is separate from the required offline demonstration. We will measure actual memory use and latency during ingestion and answer generation before finalizing the choice. The [official Gemma guide](https://ai.google.dev/gemma/docs/core) explains the model-size tradeoffs, and [Ollama's Gemma 4 listing](https://ollama.com/library/gemma4) identifies the runtime model.

## Build contract

- Keep at least three unchanged, publishable original notes in `vault/raw/`.
- Generate short, descriptive Markdown pages in `vault/wiki/`, review each against its original, connect related pages, and maintain `vault/index.md`.
- Build our own CLI and harness with `ingest`, `chat`, `ask`, `search`, and `help`.
- `search` returns original passages and paths without model generation. `ask` answers independently from retrieved evidence with checked citations or says the evidence is insufficient. `chat` keeps conversation context, retrieves only when useful, and labels suggestions.
- Keep source passages, wiki pages, prompts, evaluation expectations, and run outputs separate. Research retrieval must not index the answer key or generated chat history.
- Define three answerable questions and one unsupported question before running the evaluation. Record retrieval and generation separately.
- Restart and run ingestion, four ask tests, and chat/search checks while disconnected from the internet. Save actual outputs, timing, memory observations, and a terminal recording or screenshots.
- Open `vault/` in Obsidian and capture the required note, index/page-list, and graph screenshots. Check links and source references by opening them.
- Publish one public GitHub repository only after checking shareability, credentials, and signed-out access. Submit its URL through bCourses.

## Project folders

| Folder | Purpose |
| --- | --- |
| `vault/raw/` | Unchanged original notes. |
| `vault/wiki/` | Reviewed, linked wiki pages. |
| `vault/index.md` | The human start page. |
| `vault/attachments/` | Images used in wiki pages. |
| `evaluation/` | Test questions and expected evidence. The CLI must not search this folder. |
| `learning/` | Our quiz answers and corrections. The CLI must not search this folder. |
| `evidence/` | Actual test records, offline proof, and Obsidian screenshots. |

Obsidian reads a vault from a normal folder. We will use **Open folder as vault** and select `vault/`, not the repository root. We will open the first wiki pages in Obsidian after we select and ingest the notes. Obsidian supports links such as `[[Page Name]]`. We will check each link and source reference in the app. See the [Obsidian vault guide](https://help.obsidian.md/Files%20and%20folders/Manage%20vaults) and [internal link guide](https://help.obsidian.md/Linking%20notes%20and%20files/Internal%20links).

## Learning checkpoints

We will pause at each checkpoint to answer a short quiz and test the answer against the implementation:

1. Explain the retrieval tool, RAG workflow, and harness.
2. Trace `search`, `ask`, and `chat` through the code and predict their different outputs.
3. Diagnose a failed retrieval separately from an unsupported generated claim.
4. Explain why an offline restart is stronger evidence than a cached online result.

The answers belong in `learning/quiz-log.md`, outside the searchable wiki. The quiz is part of our learning process, not a substitute for the assignment's four required ask-mode tests.

## Next decisions

Choose three original notes that are safe to publish and decide what questions this wiki should answer. Then we can write the evaluation expectations before building retrieval, as the assignment requires.
