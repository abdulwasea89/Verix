# Verix.  

[![CI](https://github.com/abdulwasea89/Verix/actions/workflows/ci.yml/badge.svg)](https://github.com/abdulwasea89/Verix/actions/workflows/ci.yml)

**Catch outdated assumptions before your coding agent builds on them.**

Verix is a local command-line tool that helps you and your AI coding assistant notice when information used to plan a change has become outdated.

For example, Codex reads your login code and assumes it uses JWT. Another change switches that code to server-side sessions. Verix flags the changed evidence so you can review the assumption before continuing. A changed file makes a statement worth checking; it does not automatically make the statement wrong.

Verix runs with Python, Git, and SQLite. It needs no Verix account, subscription, or model API key. **Version `0.1.0` is a development candidate**; see [release status](docs/release-status.md) for completed checks and remaining acceptance work.

[Install](#installation) · [Try it](#your-first-check) · [Use with Codex](#use-with-codex) · [PR checks](#github-pull-request-checks) · [Troubleshooting](#troubleshooting)

## How it works

1. **Record evidence:** track the contents and Git revision of files you reviewed.
2. **Register a claim:** explicitly state what those files support, such as “The login endpoint uses JWT.”
3. **Check for changes:** Verix compares current files with that evidence and follows links to dependent claims and proposed edits.
4. **Review the result:** recheck affected statements, correct them, or explicitly reaffirm them after review.

You or your agent must register claims. Verix does not automatically extract assumptions from conversation. It complements code review and tests.

## Installation

You need **Python 3.12+** and **Git** on your PATH. Install from source:

```sh
git clone https://github.com/abdulwasea89/Verix.git
cd Verix
```

Create and activate a virtual environment:

**Linux / macOS**

```sh
python3 -m venv .venv
. .venv/bin/activate
```

**Windows PowerShell**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install and confirm that the command works:

```sh
python -m pip install .
verix --version
verix --help
```

Keep this environment active while using Verix, including from another project. Reactivate it in new terminals. For reproducible installations, check out a reviewed Verix commit before installing. See [CONTRIBUTING.md](CONTRIBUTING.md) for development dependencies.

## Your first check

Work inside the Git project you want to check. It must already have at least one commit. For a first try, you can stay in the cloned Verix repository; its `README.md` works with the example below. Otherwise, replace this placeholder with your project's path:

```sh
cd PATH_TO_YOUR_PROJECT
```

Initialize tracking and create a session:

```sh
verix init
verix session start --agent manual
```

A **session** groups the evidence and claims for one piece of work. Copy the returned `session` value and replace `SESSION_ID` below. Review your project's README first, then run these commands; substitute another existing file and a matching claim if needed:

```sh
verix read README.md --session SESSION_ID
verix claim add "README describes the project setup" --session SESSION_ID --evidence README.md
verix session complete --session SESSION_ID --ack-limitations
verix check --session SESSION_ID --path README.md
verix report --session SESSION_ID
```

With unchanged evidence, this example returns `allow`. `read` records a fingerprint; it does not display the file for you. `complete` acknowledges your assessment that capture is sufficient, rather than proving every dependency was covered.

Initialization creates `.verix.yml` and local state. Commit the policy, and add these entries to your project's `.gitignore` yourself:

```gitignore
.verix/
.codex/hooks.json
.claude/settings.local.json
```

### Understand the result

| Result | Meaning | `verix check` exit code |
| --- | --- | --- |
| `allow` | The recorded claims meet the current policy. | `0` |
| `verify` | Evidence needs review before relying on it. | `10` |
| `block` | The policy rejects the proposed action. | `20` |
| `unresolved` | Evidence is missing, incomplete, or unknown. | `30` |

`verix check` uses `1` for operational errors and `2` for argument errors. Use `report --json` for structured output, or put `--repo PATH` before a command to select another repository.

### When a file changes

Run `verix report --session SESSION_ID`, inspect the diff, and review the affected claim. If it still holds, copy its ID from the report and reaffirm it locally:

```sh
verix verify CLAIM_ID --session SESSION_ID --reaffirm
verix check --session SESSION_ID --path README.md
```

If the claim is wrong, start a fresh session with corrected claims and current evidence. Later evidence, revision, or policy changes expire successful verification. PR receipts require fresh reads and claims; local reaffirmations are not exported as approvals.

## Use with Codex

**Yes, Codex can use Verix.** Start with the CLI workflow above. With Verix available in its environment, give Codex an instruction such as:

> Use Verix to track this task. Start a new tracking session, review the relevant files, record their evidence, and register the claims supporting your change. Show me the session ID and report. If evidence changes, review the affected claims before continuing. Only acknowledge completeness after assessing what was captured.

Codex can run the same commands you run. `--agent codex` labels a Verix session; it does not enable automatic capture.

### Optional automatic hooks — experimental

For the **local Codex CLI**, run this from the project root:

```sh
verix init --hooks --agent codex
codex
```

This merges `.codex/hooks.json` and creates a minimal `.codex/config.toml` enabling hooks if that file is absent. Existing configuration is preserved. Review and trust the project and handlers through `/hooks`, following the [official Codex hooks documentation](https://learn.chatgpt.com/docs/hooks).

The adapter captures single literal `cat path` reads and checks every native `apply_patch` target. Claims remain explicit. Hook sessions use Codex's native `session_id`, which is separate from a session created with `verix session start`.

Start in advisory mode. Reads and unsupported commands mark capture incomplete; blocking mode denies unsupported commands, including ordinary shell tests and shell edits. Keep the installed Python interpreter available. [Codex setup and live evidence](docs/codex.md) explain the supported workflow and limits; Linux repository-file discovery and interactive trust were exercised in the acceptance work; broader native coverage remains limited.

Claude Code users can install its adapter with `verix init --hooks`. See [operations](docs/usage.md) for integration details.

## Policy and enforcement

`verix init` defaults to **advisory** mode: hook and CI findings are reported without blocking work. Local `verix check` still returns the verdict's exit code. To enforce findings, set `mode: blocking` in `.verix.yml`.

Policy supports path-based risk, excluded files, optional Python formatting normalization, and explicitly invoked verification commands. Unmatched paths have medium risk; the highest matching risk wins. Use [configuration and recovery](docs/usage.md) for examples. Review configured commands before executing them.

## GitHub pull request checks

Local tracking and merge enforcement are separate setup steps. Follow the [tested PR setup walkthrough](docs/live-pr-validation.md) to install the pinned reusable workflow and commit policy to the target branch.

After reviewing your changes, use a fresh tracking session and export its receipt:

```sh
verix receipt export --session SESSION_ID > .verix-receipt.json
```

This redirection works in Bash and PowerShell 7. Inspect the receipt, commit it with your changes, push, and open the PR. Receipts omit file bodies and original claim text, but paths and hashes can still be sensitive.

The workflow analyzes exact revisions under the trusted base policy. Same-repository PRs get one updated comment; forks get a report artifact and job summary. Require `check / analyze` and an up-to-date branch in branch protection. A policy added only in the PR cannot enable base-branch blocking. Verix's own `main` now requires PRs, Verix, all three CI jobs, and an up-to-date branch, including for administrators.

## Troubleshooting

- **`verix` not found:** activate the installation environment and check `python -m pip show verix`.
- **Missing repository or revision:** run inside a Git repository with an existing commit and fetch required history.
- **Unresolved result:** inspect the report, capture current evidence, register supported claims, and assess completeness.
- **Codex hooks do not run:** check project trust, enabled hooks, the interpreter path, and the [adapter limits](docs/codex.md).
- **PR remains blocked:** inspect the `verix-report` artifact, update your branch, and export fresh evidence and claims.

## Project documentation

- [Contributor guide](CONTRIBUTING.md) and [agent instructions](AGENTS.md)
- [Configuration, verification, and recovery](docs/usage.md)
- [Codex integration](docs/codex.md) and [live PR validation](docs/live-pr-validation.md)
- [Benchmark protocol](benchmark/README.md), [local Codex trials](benchmark/codex-protocol.md), and [release acceptance](docs/release-status.md)
- [Independent review and pilot handoff](docs/release-acceptance.md)
- [Security and reporting](SECURITY.md)

Verix cannot prove code correct, discover every hidden dependency, or replace review and tests. Receipts are self-reported and hooks are not a security boundary. Hosted subscriptions, dashboards, and automatic claim extraction are outside this release.
