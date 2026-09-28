# Step 5 — Make the wiki pages

## What this step does

An original note goes in. A short wiki draft comes out. Local Gemma writes the draft. Our Python harness checks the source, calls Gemma, checks the selected passage IDs and copies the original evidence, saves the page, and records the run.

This does not train Gemma. It does not build the search index. The separate `search` command indexes the original passages for retrieval.

## Open a terminal

Run these commands from the project folder:

```sh
cd "/Users/haniframadhan/Documents/ChatGPT/Fundamentals of Agentic AI project"
python3 wiki.py help
python3 wiki.py ingest --help
```

The first command lists available commands. The second explains ingestion options. Neither command calls Gemma or changes a page.

## Understand the ingestion command

```sh
python3 wiki.py ingest --source S01
```

- `python3` runs the Python program.
- `wiki.py` is our CLI entry point.
- `ingest` selects the wiki drafting task.
- `--source S01` selects the architecture note from the source catalog.

Use `S02` for versioned agent learning and `S03` for run controls. The IDs refer to `data/source-catalog.json`.

A reviewed page is protected. The command will tell you if it cannot replace that page. Use `--replace-reviewed` only when you intend to replace it with a new draft. The prior page is archived in the run folder. Review the replacement again.

## Follow the files

1. Read the original in `vault/raw/`.
2. Read the model instruction in `prompts/ingest.txt`.
3. Read the page in `vault/wiki/`.
4. Open the matching run folder in `evidence/ingestion/`.
5. Compare the saved model response and draft with the reviewed page.

`run.json` records the outcome, settings, and elapsed time. The response file contains the actual Gemma output. A review record explains corrections. The source catalog stores file hashes so we can detect changes to the originals.

## Review the result

Check each point against its cited original lines. Check whether the summary adds anything the note does not support. Keep reported claims and recommendations attributed to their source. A quote can be exact while its claim remains unverified.

Version-1 tests on the older corpus exposed unsupported numbers and altered quotations. Their records remain in the Git-ignored local archive. The approved version-2 wiki pages were checked against their frozen original notes.

## Run the code checks

```sh
python3 -m unittest discover -s tests -v
```

These checks use synthetic notes and a fake model response. They test code behavior without running Gemma. The real model run records are separate. Neither set of checks is the final offline demonstration.
