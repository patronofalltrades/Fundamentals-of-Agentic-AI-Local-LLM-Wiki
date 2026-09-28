---
source_id: S02
source_sha256: 2d3d10ecaaf5958ec70d0e739f1afd776e0e6e9a93593bd1f169fe23f3b4aed2
model: gemma4:e2b-mlx
run_id: 20260927T212656Z-306f2ba3
review_status: reviewed
reviewed_by: Codex
---

# Learning from Agent Evaluations

## Summary

This study note suggests a method for improving prompts or checklists by treating each change as a small experiment. This involves setting a baseline, making one change, testing with comparable cases, evaluating the results, and keeping the learning from the changes.

## Key points

- A useful prompt or checklist should improve through measured changes. (Original lines 16–16.)
- The review cycle involves setting a baseline, changing one thing, running comparable cases, evaluating the output, and deciding whether to keep or revert the change. (Original lines 20–25.)
- The goal is to save the diff, test results, and a decision note when an edit fails, as this evidence is useful for future changes. (Original lines 20–25.)
- The first answer tests exposed a gap between finding a passage and producing a complete cited answer, requiring adjustments to retrieval and answer instructions. (Original lines 29–29.)
- The final answer should be judged against the original passage, not just by the validity of a citation ID. (Original lines 29–29.)
- This method does not guarantee that every edit improves an agent, and the test cases might miss a failure. (Original lines 33–33.)

## Limits

- The test cases used might miss a failure.
- A small sample of tests can be misleading.
- The method does not guarantee that each edit improves an agent.

## Original source

[[raw/Versioned Agent Learning|Versioned Agent Learning]]

## Related pages

<!-- related:start -->
- [[wiki/Agent Architecture Patterns|Agent Architecture Patterns]] — Place evaluation within an agent architecture.
- [[wiki/Agent Reliability Controls|Agent Reliability Controls]] — Combine quality checks with controls for reliable operation.
<!-- related:end -->
