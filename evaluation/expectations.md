# Evaluation expectations — define before retrieval

This file stays outside `vault/` and must not be indexed by the CLI. Fill the source and expected-passage fields from the three selected originals before running the harness. Do not write model answers here in advance.

| Test | Question | Expected source and exact passage | Expected behavior |
| --- | --- | --- | --- |
| 1 — direct | Pending source choice | Pending | Answer from one source with a correct citation |
| 2 — paraphrase | Pending source choice | Pending | Retrieve despite changed wording, then cite the supporting passage |
| 3 — synthesis | Pending source choice | Pending | Answer from the available evidence, possibly linking two sources |
| 4 — unsupported | Pending source choice | No supporting passage in the frozen corpus | Explicitly say the evidence is insufficient |

For each run, save the exact retrieved passages and paths, Gemma answer, citations, model identity, execution setting, timing, and our assessment in a separate evidence card. A citation ID that exists in the retrieval result is necessary but does not prove the cited text supports the claim.
