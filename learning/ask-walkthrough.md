# Step 7 — Ask Gemma from original notes

Keep Ollama running. Set `QUESTION` to a question of your own, then run this command from the project folder:

```sh
python3 wiki.py ask "$QUESTION" --limit 3
```

The direct test uses one passage; the other three cases use three. A test run uses `gemma4:e2b-mlx` with an 8,192-token context, a 900-token output limit, temperature 0, and seed 42. Exact evaluation questions remain in a Git-ignored local file.

Check each result:

1. Read the answer and its citation ID.
2. Open the source file named after the citation. Compare the cited line range with the answer.
3. For a supported answer, check that every requested part is present and supported.
4. For the unsupported question, check that the CLI says the notes do not provide the requested values. It must not invent limits.
5. Open `evidence/ask/<run-id>/run.json` to inspect the exact model output. The adjacent files save the retrieved passages, request, response, and model details.

Use `--json` to print the full retrieval and answer record in the terminal. The CLI also prints its evidence folder. No chat history is sent to `ask`.

## Checkpoint 3 quiz

Explain the difference between checking that a citation ID was retrieved and checking that its passage supports a claim. Keep your personal answer outside Git.
