# Step 6 — Search the originals

## Run a search

```sh
cd "/Users/haniframadhan/Documents/ChatGPT/Fundamentals of Agentic AI project"
python3 wiki.py search "max steps tokens" --limit 1
```

`search` selects the retrieval tool. The words in quotes are the query. `--limit 1` shows one passage. Gemma is not used.

## Read the result

1. Find the source title: `Agent Run Controls`.
2. Check the path. It must start with `vault/raw/`.
3. Read the passage that includes original line 20. It names the three budget categories.
4. Note the citation ID. It ties this passage to a source version and line range.
5. Open the saved JSON search record to see the query terms and timing.

The passage says to limit steps, tokens, and elapsed time. It does not give exact budget values for this Mac. A related passage is not always enough to answer a question.

## Try a paraphrase

```sh
python3 wiki.py search "unlimited resources" --limit 5 --json
```

Inspect `expanded_terms`. The harness adds a few related keywords. The text under each hit still comes from the original note. This search does not use embeddings or an LLM.

## Rebuild the local index

```sh
python3 wiki.py search "max steps tokens" --limit 1 --rebuild
```

This rebuilds the local SQLite index. It does not change original notes or wiki pages. The database stays outside the vault and is ignored by Git.

## Quiz

If the wrong passage appears, should we first inspect retrieval or change Gemma's answer prompt? Explain why.

Next, `ask` will pass retrieved passages to Gemma and require a supported answer or an insufficient-evidence response.
