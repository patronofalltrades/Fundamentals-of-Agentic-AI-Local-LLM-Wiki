# Questions, responses, and evaluation

This report shows the exact four test questions and the **displayed CLI answers** from the latest completed disconnected run, `20260928T190114Z-21559`. Hanif asked to publish this review. Full model requests, raw JSON responses, terminal logs, and video remain in Git-ignored local storage.

The evaluation uses three approved original notes. [S01](../vault/raw/Choosing%20Agent%20Architectures.md) covers architecture patterns; [S02](../vault/raw/Versioned%20Agent%20Learning.md) covers versioned evaluation; [S03](../vault/raw/Agent%20Run%20Controls.md) covers run controls.

## Four ask cases

### Q1 — Direct answer

**Question:** According to the architecture note, what are the five agent architecture patterns, and how is each one structured?

**Displayed answer:**

> The five agent architecture patterns are: Single agent, Sequential, Parallel, Hierarchical, and Evaluator–optimizer. Single agent has one model handling a task and may repeat a tool-use cycle. Sequential work moves through an ordered set of stages, where a later stage uses the output of an earlier stage. Parallel involves independent pieces of work running simultaneously, with a final step collecting results. Hierarchical involves a coordinator assigning work to specialist agents and combining their returns. Evaluator–optimizer has one role producing a candidate and another checking it against a criterion, revising the candidate only when the check finds a useful change. Sources: [S01-34f0d549d482-L20-L24] vault/raw/Choosing Agent Architectures.md:20-24

**Assessment:** Pass. The answer names all five patterns and explains each structure. S01 lines 20–24 support the claims.

### Q2 — Paraphrase

**Question:** According to the versioned-learning note, what should I do when an edit to a reusable review checklist makes the result worse, and how should I preserve what I learned?

**Displayed answer:**

> If an edit to a reusable review checklist makes the result worse, you should restore the earlier version. You should also keep the diff, the test results, and a short decision note, as a failed edit provides useful evidence for future changes. Sources: [S02-2d3d10ecaaf5-L20-L25] vault/raw/Versioned Agent Learning.md:20-25; [S02-2d3d10ecaaf5-L16-L16] vault/raw/Versioned Agent Learning.md:16-16

**Assessment:** Pass. The answer says to restore the earlier checklist and keep the diff, test results, and decision note. S02 lines 20–25 support the claims.

### Q3 — Two-note synthesis

**Question:** Using the versioned-learning and run-controls notes, explain how to improve agent output over repeated runs and also stop a run from consuming unlimited resources.

**Displayed answer:**

> To improve agent output over repeated runs, use versioned-learning by setting a baseline, changing one thing at a time, running comparable cases to see gains and regressions, evaluating the output, and keeping or reverting the change based on the results. To stop a run from consuming unlimited resources, use agent run controls by enforcing limits such as a maximum number of steps, a token budget, and a wall-clock timeout in the code. Sources: [S03-5916a5f9fae2-L20-L24] vault/raw/Agent Run Controls.md:20-24; [S02-2d3d10ecaaf5-L20-L25] vault/raw/Versioned Agent Learning.md:20-25

**Assessment:** Pass. The answer combines versioned evaluation with code-enforced limits. S02 lines 20–25 and S03 lines 20–24 support the claims.

### Q4 — Unsupported question

**Question:** What exact maximum step count, token budget, and wall-clock timeout do these notes prescribe for this MacBook Air local Gemma wiki?

**Displayed answer:**

> The retrieved passages state that budgets like maximum steps, token budget, and wall-clock timeout should be enforced in code, but they do not set exact values for the MacBook Air wiki. These limits should come from measurements on the Mac and the tasks the project wants to perform.

**Assessment:** Pass for the displayed answer. It gives no invented numbers and no final citation. Gemma's raw response contained citations, which the harness removed and recorded.

## Chat checks

The same offline run tested an ordinary four-turn chat and a separate cited follow-up. The table shows the exact user messages and the displayed replies.

| Turn | User message | Displayed reply | Search used? |
| --- | --- | --- | --- |
| 1.1 | Hi. Tell me one thing you can help me do in this CLI. | I can help you brainstorm ideas, draft text, or refine content for your agentic AI assignment. | No |
| 1.2 | Draft a two-sentence opening for an agent review checklist. | Here is a draft:  This checklist is designed to ensure a thorough and comprehensive review of the agent's performance. Use these points to systematically assess functionality, adherence to instructions, and overall effectiveness. | No |
| 1.3 | Make that shorter. | This checklist ensures a thorough review of the agent's performance. Use these points to assess functionality and effectiveness. | No |
| 1.4 | According to my notes, which three budget limits should the code enforce? | The code should enforce a maximum number of steps, a token budget, and a wall-clock timeout. Sources: [S03-5916a5f9fae2-L20-L24] vault/raw/Agent Run Controls.md:20-24 | Yes |
| 2.1 | According to my notes, which three budget limits should the code enforce? | The code should enforce a maximum number of steps, a token budget, and a wall-clock timeout. Sources: [S03-5916a5f9fae2-L20-L24] vault/raw/Agent Run Controls.md:20-24 | Yes |
| 2.2 | Make that shorter. | The code must enforce a maximum number of steps, a token budget, and a wall-clock timeout. Sources: [S03-5916a5f9fae2-L20-L24] vault/raw/Agent Run Controls.md:20-24 | Yes |

- The first three general turns did not search the notes.
- The note question retrieved S03 and cited lines 20–24.
- The separate short follow-up searched S03 again and kept its citation.
- Chat kept earlier turns within each session. The standalone `ask` cases did not use chat history.

## Search and offline checks

- `search` returned original passages while Gemma was unloaded.
- Wi-Fi was off, and an external HTTPS check failed.
- Local ingestion of all three notes completed.
- All 35 code tests passed.
- The four ask cases and chat checks passed in this disconnected run.
- The [offline summary](offline/completed-run-summary.json) records flags, times, and hashes without the raw transcripts.

## Overall evaluation

- **Strength:** All four displayed ask outcomes match their expected roles. The three supported answers cite the correct originals. The unsupported answer does not invent values.
- **Strength:** Chat separates general drafting from note-based answers. Note-based replies retain citations.
- **Important limit:** Citation-ID checks prove that an ID was retrieved. They do not prove that the passage supports the claim. A person checked these four answers against the original lines.
- **Important limit:** These four planned cases were used during development. They are not an independent or broad accuracy test. A new paraphrase can still miss a passage because search is keyword-based.
- **Recorded correction:** The raw Q4 model response included citations with an insufficient-evidence flag. The harness removed the citations from the displayed answer. The raw event remains in the private run record.

The machine-readable offline evaluation marked manual review as pending when the script finished. The later human review is documented in the [offline evidence note](offline/README.md).
