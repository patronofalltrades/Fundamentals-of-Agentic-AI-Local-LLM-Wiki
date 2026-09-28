# Connected evaluation of the frozen corpus

Run date: 2026-09-27 local time. Model: local `gemma4:e2b-mlx`. Corpus hashes: S01 `34f0d549d482`, S02 `2d3d10ecaaf5`, S03 `5916a5f9fae2`. This was a connected local-model test, not the required offline proof.

| Case | Role | Result | Cited source support | Wall time |
| --- | --- | --- | --- | ---: |
| Q1 | Direct | Passed | S01 lines 20–24 describe all five structures. | 19.0 s |
| Q2 | Paraphrase | Passed | S02 lines 20–25 support restoring a worse revision and saving the diff, tests, and decision. | 5.6 s |
| Q3 | Synthesis | Passed | S02 lines 20–25 support versioned evaluation; S03 lines 20–24 support code-enforced budgets. | 8.5 s |
| Q4 | Unsupported | Passed | The notes do not specify exact values. The displayed answer abstained and contained no citations. | 7.1 s |

The harness verified that each displayed citation ID belonged to the retrieved passages. We then checked the supported claims against the cited source lines. For Q4, Gemma marked the answer as insufficient but included two citations in its raw JSON. The harness cleared those citations and recorded that correction. The raw response remains in a Git-ignored local run record.

The exact test questions, model requests, raw answers, and terminal transcript are private. This report omits their text. The required Obsidian screenshots and a completed disconnected run are documented in `evidence/offline/README.md`.
