---
title: Versioned Agent Learning
source_kind: personal_study_note
prepared_with: Codex
review_status: reviewed_by_hanif
reference_author: Shubham Saboo
reference_url: https://x.com/Saboo_Shubham_/status/2069473303992115607
---

# Versioned Agent Learning

> Hanif-reviewed study note. It develops the linked idea in new wording and uses this assignment as an example.

## Core idea

A useful prompt or checklist should improve through measured changes. Saving only the latest version hides why a rule was added and whether it helped. I can treat each change as a small experiment: make one edit, run the same cases, inspect the results, and record the decision.

## Review cycle

1. **Set a baseline.** Keep the current prompt, checklist, or rubric and the results it produces.
2. **Change one thing.** State what the edit is meant to improve.
3. **Run comparable cases.** Use examples that reveal both gains and regressions.
4. **Evaluate the output.** Check evidence, accuracy, clarity, and any task-specific rule. A fluent answer is not enough.
5. **Keep or revert.** Keep the edit if the results improve without a serious regression. If the edit makes the result worse, restore the earlier version.
6. **Save the learning.** Keep the diff, the test results, and a short decision note. A failed edit is useful evidence when the next change is designed.

## Application to this wiki

Our first answer tests exposed a gap between finding a passage and producing a complete cited answer. We kept earlier failures, adjusted the retrieval and answer instructions, and reran the frozen questions. The final answer should be judged against the original passage, not only by whether a citation ID is valid. This record lets us explain what changed and why.

## Limit

This method does not guarantee that each edit improves an agent. The test cases may miss a failure, and a small sample can be misleading. I would widen the evaluation set before relying on the same prompt for many kinds of work.

## Reference

Inspired by [Shubham Saboo's post on versioned product memory](https://x.com/Saboo_Shubham_/status/2069473303992115607). The post is a starting point for these study notes; its full text is not reproduced here.
