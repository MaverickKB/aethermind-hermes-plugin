# Hermes core patch: steered prompts get pre_llm_call hook context

## Problem

Hermes collects plugin `pre_llm_call` context (the AetherMind CL2 packet,
shell-hook continuity) only in `build_turn_context`, once per user turn.
A prompt delivered mid-run (`/steer`, or a same-second reply admitted into
an open run) never passes that gate, so the model keeps working from the
turn-start packet alone: no refreshed continuity brief, no write reminder
on the newest turn. Measured on this install: only ~14-29% of mid-run
prompts carried any packet, vs ~98% of turn-start prompts.

## The patch

`hermes-steer-pre-llm-context.patch` adds `_attach_steer_hook_context` to
`agent/agent_runtime_helpers.py`. After a steer row is appended, it runs the
same `_collect_pre_llm_call_context` collector turn starts use and rides the
context on the steer row itself (a new, unflushed row, so no cached prompt
byte moves). Failures and hook vetoes are non-fatal: the steer is user text
already accepted and is never dropped over hook context.

## Apply (stock checkout, no commit)

    cd ~/.hermes/hermes-agent
    git apply --check docs-patch-location/hermes-steer-pre-llm-context.patch  # dry run
    git apply <path>/hermes-steer-pre-llm-context.patch
    # restart the desktop/gateway so the running process picks it up

## Rollback

    cd ~/.hermes/hermes-agent
    git apply -R <path>/hermes-steer-pre-llm-context.patch

## Update survival

`hermes update` may reset or stash local changes on the main channel.
Re-apply this patch after any update (check with `git apply --check` first).
The durable path is upstreaming it; this patch is written to be PR-ready.
