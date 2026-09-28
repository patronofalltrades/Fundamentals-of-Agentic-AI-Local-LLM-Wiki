# Offline proof

Two disconnected runs completed on 2026-09-28. The latest is the Git-ignored run `20260928T190114Z-21559/`. Its `status.txt` says `completed`. The recording shows Wi-Fi off, a failed external HTTPS check, local Ollama, the test sequence, and the final status. The script saved the network check and full terminal log in that run folder. The earlier completed run is `20260928T185634Z-21046/`. The [prompt-free JSON summary](completed-run-summary.json) records the check flags, timing, and hashes of the private raw evidence.

| Check in the latest run | Result |
| --- | --- |
| Search original passages after unloading Gemma | Passed; no model generation |
| Isolated ingestion of S01, S02, and S03 | Passed; 34.08 seconds total |
| Code tests | 35 passed |
| Q1–Q3 answerable cases | Passed retrieval, expected-source, and citation-ID checks |
| Q4 unsupported case | Final answer marked insufficient; no invented number or final citation |
| Four-turn chat and cited note follow-up | Passed; note turns kept their citations |

I checked the three answerable responses against the cited original lines. Q1 matches S01 lines 20–24; Q2 matches S02 lines 20–25; Q3 matches S02 lines 20–25 and S03 lines 20–24. Q4 correctly says the notes give no exact budget values for this Mac. The harness removed a citation from the unsupported response, as recorded in the private evaluation file. The final answer contains no citation. Exact questions, raw answers, model requests, and full logs remain in Git-ignored local files.

The model calls for Q1–Q4 took 3.9, 2.9, 3.8, and 3.2 seconds of wall time. Ollama showed the model at 7.6 GB, 100% GPU, with an 8,192-token runtime context after the checks. This is a loaded-model snapshot, not peak application memory.

The [12.5-second completed-run GIF](completed-offline-steps.gif) shows five cropped Terminal views: disconnection check, search and ingestion, code tests, four ask outcomes, and the completed status. The source video stays private because its full-screen view includes unrelated personal notes. The GIF contains no private question text.

![Five steps from the completed disconnected run](completed-offline-steps.gif)

The first attempt remains saved in `20260928T183319Z-17279/` with `failed (exit 1)`. It stopped before the ask checks because a private test file was not resident on local disk. [Its short GIF](first-attempt-steps.gif) remains as an honest failure record. `scripts/prepare-offline-inputs.py` staged that file locally before the two successful reruns.
