# Offline proof

Two disconnected runs completed on 2026-09-28. The latest run is `20260928T190114Z-21559/` in Git-ignored local storage. Its `status.txt` says `completed`.

## What the recording shows

- Wi-Fi was off.
- An external HTTPS check failed.
- Ollama ran on the Mac.
- Search worked after Gemma was unloaded.
- The script ingested three notes and ran the tests.
- The final run status was `completed`.

The [public JSON summary](completed-run-summary.json) gives check flags, times, and hashes. It does not include the private test prompts.

## Results

- **Search:** Passed without model generation.
- **Ingestion:** S01, S02, and S03 passed in 34.08 seconds.
- **Code:** 35 tests passed.
- **Ask Q1–Q3:** Retrieved the expected sources and returned valid citations.
- **Ask Q4:** Returned insufficient evidence, with no final citation or invented number.
- **Chat:** The four-turn session and cited follow-up passed.

A person checked each answerable response against the cited original lines:

- Q1: S01 lines 20–24.
- Q2: S02 lines 20–25.
- Q3: S02 lines 20–25 and S03 lines 20–24.

The harness removed a citation from the unsupported response. The private run record keeps that event and the raw response.

## Timing and memory

- Q1–Q4 model calls took 3.9, 2.9, 3.8, and 3.2 seconds.
- After the checks, Ollama showed 7.6 GB loaded on the GPU.
- The runtime context was 8,192 tokens.
- The 7.6 GB value is a loaded-model snapshot. It is not peak application memory.

## Video evidence

The [12.5-second GIF](completed-offline-steps.gif) shows five cropped Terminal views:

1. Disconnection check.
2. Search and ingestion.
3. Code tests.
4. Four ask outcomes.
5. Completed status.

![Five steps from the completed disconnected run](completed-offline-steps.gif)

The full recording stays private. Its full-screen view includes unrelated personal notes. The GIF has no private question text.

## Earlier attempts

- The first attempt, `20260928T183319Z-17279/`, ended with `failed (exit 1)` before the ask checks.
- A private test file was not present on local disk after disconnection.
- [Its short GIF](first-attempt-steps.gif) remains as an honest failure record.
- `scripts/prepare-offline-inputs.py` put that file on local disk before two completed reruns.
- The earlier completed run is `20260928T185634Z-21046/`.

Exact questions, raw answers, model requests, and full logs remain in Git-ignored local files.
