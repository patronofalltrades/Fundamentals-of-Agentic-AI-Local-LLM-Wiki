---
title: Choosing Agent Architectures
source_kind: personal_study_note
prepared_with: Codex
review_status: reviewed_by_hanif
reference_author: h100envy
reference_url: https://x.com/h100envy/status/2070162890036801603
---

# Choosing Agent Architectures

> Hanif-reviewed study note. It interprets the linked post in new wording. It does not reproduce the post.

## Core idea

An agent architecture is a way to divide work between a model, tools, and control code. More agents can help when tasks are independent or need different roles. They also add coordination cost and more places for an error to spread. I would choose the smallest structure that meets the task and test it before adding more agents.

## Five patterns

1. **Single agent:** One model handles a task and may repeat a tool-use cycle. The application still sets limits and checks the result.
2. **Sequential:** Work moves through an ordered set of stages. A later stage uses the output of an earlier stage, so the handoff can be inspected.
3. **Parallel:** Independent pieces of work run at the same time. A final step collects and reconciles their results.
4. **Hierarchical:** A coordinating agent assigns work to specialist agents and combines what they return. The coordinator needs clear scope and a limit on delegation.
5. **Evaluator–optimizer:** One role produces a candidate, and another role checks it against a criterion. The candidate is revised only when the check finds a useful change.

## How I would choose

I would begin with one agent or one model call when the task is narrow. I would add ordered stages when the output of one step must be verified before the next step. I would use parallel work only for pieces that do not depend on each other. I would consider a coordinator when specialist roles are truly different. I would use an evaluator when I can state what a better result means and test that judgment.

## Application to this wiki

This assignment does not require a team of agents. Our CLI uses code to choose a mode, retrieve passages, call local Gemma, and check citation IDs. That fixed harness is easier to inspect than delegating these steps to other models. A future version could add an evaluator for wiki drafts, but a human must still check claims against the source.

## Limit

The linked post makes broad performance claims about multi-agent systems. This note does not adopt any numerical claim. The right structure depends on task quality, latency, cost, and failure rate in our own tests.

## Reference

Inspired by [h100envy's post on agent patterns](https://x.com/h100envy/status/2070162890036801603). The link is for attribution and further reading, not a claim that the post's measurements were independently verified.
