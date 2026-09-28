---
source_id: S03
source_sha256: 5916a5f9fae27e1e6716ee7c64ae46670f7008284d51825a716a51fc6f10bbdc
model: gemma4:e2b-mlx
run_id: 20260927T212656Z-306f2ba3
review_status: reviewed
reviewed_by: Codex
---

# Agent Reliability Controls

## Summary

This study note suggests agent run controls for a small local agent project, emphasizing the need for agents to stop, recover, and record their actions. Controls should include limits on steps, tokens, timeouts, retries, checkpoints, approvals, and observability.

## Key points

- A useful agent must stop, recover, and leave a record that a person can inspect. (Original lines 16–16.)
- Budgets include a maximum number of steps, a token budget, and a wall-clock timeout in code. (Original lines 20–24.)
- Retries should be limited for transient failures, avoiding retrying actions that can duplicate something unless there is a duplicate check. (Original lines 20–24.)
- Checkpoints should save enough state to explain what completed and what failed, allowing resumption from a known point. (Original lines 20–24.)
- Approvals should stop the agent before an irreversible action requiring a human decision, enforcing this boundary. (Original lines 20–24.)
- Observability requires saving inputs, tool results, model settings, timing, and errors to diagnose failed runs. (Original lines 20–24.)
- The agent's step, token, and time limits should come from measurements on the Mac and the desired tasks. (Original lines 32–32.)

## Limits

- The exact values for limits should come from local measurements and desired tasks.
- This is for a local learning project, not a deployed service.
- The full checklist is at its source URL.

## Source

[[raw/Agent Run Controls|Agent Run Controls]]
The original preserves the upstream author and URL. Line references use the unchanged file, including its metadata.


## Related pages

<!-- related:start -->
- [[wiki/Agent Architecture Patterns|Agent Architecture Patterns]] — Apply reliability controls to the chosen agent structure.
- [[wiki/Learning from Agent Evaluations|Learning from Agent Evaluations]] — Record evaluation results and keep or revert changes.
<!-- related:end -->
