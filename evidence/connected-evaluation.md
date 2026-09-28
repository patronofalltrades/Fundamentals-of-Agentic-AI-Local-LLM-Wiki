# Connected test of the approved notes

- **Date:** 2026-09-27, local time.
- **Model:** local `gemma4:e2b-mlx`.
- **Source hashes:** S01 `34f0d549d482`, S02 `2d3d10ecaaf5`, S03 `5916a5f9fae2`.
- **Scope:** This test used a local model while the Mac was connected. The [offline report](offline/README.md) gives the required disconnected proof.

| Case | Purpose | Result | Supporting original lines | Time |
| --- | --- | --- | --- | ---: |
| Q1 | Direct answer | Passed | S01 lines 20–24 | 19.0 s |
| Q2 | Paraphrase | Passed | S02 lines 20–25 | 5.6 s |
| Q3 | Combine notes | Passed | S02 lines 20–25; S03 lines 20–24 | 8.5 s |
| Q4 | Unsupported question | Passed | No exact values in the notes | 7.1 s |

## Checks

- The harness confirmed that each displayed citation ID came from a retrieved passage.
- A person checked the supported claims against the cited lines.
- Q4 returned insufficient evidence and no final citations.
- Gemma's raw Q4 response contained two citations. The harness removed them from the displayed result and saved the correction.
- The raw answer and exact test questions remain in Git-ignored local records.

See the [Obsidian proof](obsidian/README.md) for screenshots of the linked vault.
