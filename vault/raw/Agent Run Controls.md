---
title: Agent Run Controls
source_kind: personal_study_note
prepared_with: Codex
review_status: reviewed_by_hanif
reference_author: Karan
reference_url: https://x.com/kmeanskaran/status/2089417884984606736
---

# Agent Run Controls

> Hanif-reviewed study note. It selects controls relevant to a small local agent project rather than copying the linked AWS checklist.

## Core idea

A useful agent must stop, recover, and leave a record that a person can inspect. A successful demo does not show what happens after a timeout, a repeated request, or a weak model answer. I would add controls in code and verify them with tests.

## Limits and recovery

- **Budgets:** Enforce a maximum number of steps, a token budget, and a wall-clock timeout in code. A prompt can ask the model to be brief, but it cannot be the only enforcement mechanism. The linked post gives categories; it does not set exact values for this MacBook Air wiki.
- **Retries:** Use limited retries for transient failures. Avoid retrying an action that can duplicate a payment, file write, or message unless the action has an idempotency key or another duplicate check.
- **Checkpoints:** Save enough state to explain what completed and what failed. Resume from a known point when that is safer than starting again.
- **Approvals:** Stop before an irreversible action that needs a human decision. The application should enforce this boundary rather than relying on a model promise.
- **Observability:** Save inputs, tool results, model settings, timing, and errors. Use these records to diagnose a failed run and compare versions.

## Application to this wiki

Our local CLI checks source hashes before it ingests notes. It saves retrieval and generation records separately. `search` can work with Gemma stopped. `ask` starts fresh for each question so an earlier chat answer cannot become evidence. The harness checks that cited IDs came from the retrieved passages, and a human checks whether those passages support the claims.

## Limit

This is a local learning project, not a deployed service. It does not need the cloud infrastructure described in the linked post. The exact step, token, and time limits should come from measurements on this Mac and from the tasks we want it to perform.

## Reference

Inspired by [Karan's post on production controls for agents](https://x.com/kmeanskaran/status/2089417884984606736). The full checklist stays at its source URL.
