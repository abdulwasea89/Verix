# Codex integration (experimental)

## Installation

Install Verix in the Python environment that will remain available to Codex:

```sh
verix init --hooks --agent codex
```

The installer merges `.codex/hooks.json` and creates a minimal `.codex/config.toml` with `features.hooks = true` if that file is absent. Existing configuration and handlers are preserved. Ignore the generated hook file in Git: its command contains the local Python interpreter path.

Start Codex from the repository root. Enable the hooks feature if disabled in existing configuration, trust the repository, and review/enable the handlers in `/hooks`. Follow the [official Codex hooks documentation](https://learn.chatgpt.com/docs/hooks) for trust and configuration layers. Do not bypass review of unfamiliar hooks.

## Supported workflow

- A single literal `cat path` or `cat -- path` through the native Bash tool captures evidence only when returned bytes exactly match stable pre/post fingerprints and revision.
- Native `apply_patch` checks every added, updated, deleted, and moved target before execution. A denied target denies the whole tool call. Only a recognized successful response marks actions executed.
- Register claims with `verix claim add --session SESSION_ID --evidence path "claim"`. The hook payload supplies the native Codex session ID; session rows also identify the agent as `codex`.
- Every read and unsupported command marks completeness unknown. After reviewing capture, run `verix session complete --session SESSION_ID --ack-limitations`. Fresh reads alone do not reaffirm old claims: review them and use `verix verify CLAIM_ID --session SESSION_ID --reaffirm`.
- Begin with advisory policy. Blocking policy denies unsupported commands, including ordinary shell tests, pipes, partial readers, and shell edits. Use the established explicit verification commands from an operator terminal.

This deliberately narrow adapter rejects non-root working directories and unsafe paths. It does not infer claims, parse arbitrary shell programs, or provide a security boundary. Hook failures, disabled hooks, and tools outside native hook coverage require operational monitoring.

## Live evidence — 2026-11-03

Tested on Linux with Codex CLI `0.164.0`, `gpt-6.1-sol`, and the existing ChatGPT login. Only a disposable synthetic Git repository was exposed. Plugins, apps, and multi-agent tools were disabled. No Claude session or 450-run benchmark was used.

| Check | Observed result |
| --- | --- |
| Native `cat auth.py` | Exact full-file observation persisted under Codex session |
| Host changes `AUTH_MODE` after declared claim | Native patch denied with `Verix block`; `TIMEOUT` unchanged |
| Native reread, operator reaffirmation and completeness acknowledgement | Same native patch allowed; `TIMEOUT` changes from 30 to 60 |
| Successful native patch response | Exit-code envelope recognized; action recorded executed |
| Resume and audit replay | Session evidence persisted; stored verdicts replayed consistently |

The first stale attempt was denied as unresolved because the test harness had not committed its completeness acknowledgement. After correcting the harness transaction, the stale attempt was denied as block. The first allowed run exposed the native patch response envelope; the adapter was corrected, the captured response replayed, and a fresh native patch confirmed execution on the final code.

Runs used explicit inline hook configuration with user configuration ignored and trust bypassed only for the vetted synthetic handlers. Repository-file discovery and interactive `/hooks` trust were not established by these runs. Windows/macOS native hooks, live compaction, parallel native tool delivery, and unrestricted real-project capture remain unvalidated. Automated regression tests cover supported payloads, duplicates, partial output, failed patches, multiple targets, unsafe paths, configuration preservation, and compaction persistence.

## Linux acceptance follow-through

Subsequent interactive CLI testing loaded the instrumented project-local hook file through the trusted repository layer. The `/hooks` UI showed four handlers needing review, then showed the handlers active after trust. A real read captured complete evidence. `/compact` initially exposed an invalid event response; returning the supported common field `continue: true` corrected it, and a second native compaction preserved observations and claims without another hook error. Global user configuration was preserved; no hook-trust bypass was used for that UI test.

The handler instrumentation only recorded synthetic payloads and delegated to `verix codex-hook`. This establishes a narrow Linux path, not arbitrary shell or native macOS/Windows coverage. V1 prioritizes Codex on Linux; Claude and other native platforms remain experimental. See the [acceptance handoff](release-acceptance.md) and [local diagnostic protocol](../benchmark/codex-protocol.md).

A fresh controlled [two-native-session demo](../benchmark/results/native-sessions-20261103.json) subsequently passed peer-edit, stale-denial, and explicit-review recovery checks. It used vetted inline hooks, so its discovery claim is separate from the interactive project-file test above. Operator code registered claims and acknowledged completeness between native turns.
