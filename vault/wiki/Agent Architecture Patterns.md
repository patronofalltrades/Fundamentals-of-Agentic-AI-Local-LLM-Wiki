---
source_id: S01
source_sha256: 34f0d549d4820cfbd02578ee1cbd54b3a9d3c04c996dd2f7cb73190efbceee4c
model: gemma4:e2b-mlx
run_id: 20260927T212656Z-306f2ba3
review_status: reviewed
reviewed_by: Codex
---

# Agent Architecture Patterns

## Summary

Agent architectures divide work among a model, tools, and control code. The study note recommends choosing the smallest structure that fits the task and testing it before adding more agents. It describes five patterns: single agent, sequential, parallel, hierarchical, and evaluator–optimizer.

## Key points

- An agent architecture divides work between a model, tools, and control code. More agents can help when tasks are independent or need different roles, but they add coordination cost and more places for errors to spread. (Original lines 16–16.)
- Single agent involves one model handling a task and may repeat a tool-use cycle, with the application setting limits and checking the result. (Original lines 20–24.)
- Sequential work moves through an ordered set of stages where a later stage uses the output of an earlier stage, allowing for inspection of the handoff. (Original lines 20–24.)
- Parallel work involves independent pieces of work running at the same time, with a final step collecting and reconciling their results. (Original lines 20–24.)
- Hierarchical involves a coordinating agent assigning work to specialist agents and combining their returns, requiring the coordinator to have clear scope and limits on delegation. (Original lines 20–24.)
- Evaluator–optimizer uses one role to produce a candidate and another to check it against a criterion. It revises the candidate when the check finds a useful change. (Original lines 24–24.)
- The study note recommends starting with one agent for narrow tasks and adding other patterns only when the task calls for them. (Original lines 28–28.)

## Limits

- The choice of the right structure depends on task quality, latency, cost, and failure rate in tests.
- This note does not adopt any numerical claims from the linked post.
- The reference link is for attribution and further reading, not a claim that the post's measurements were independently verified.

## Original source

[[raw/Choosing Agent Architectures|Choosing Agent Architectures]]

## Related pages

<!-- related:start -->
- [[wiki/Learning from Agent Evaluations|Learning from Agent Evaluations]] — Use evaluation to improve the instructions that an agent follows.
- [[wiki/Agent Reliability Controls|Agent Reliability Controls]] — Add operating limits and recovery controls to the chosen structure.
<!-- related:end -->
