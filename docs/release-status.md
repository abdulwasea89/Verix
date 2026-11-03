# V1 implementation and acceptance status

Version remains `0.1.0` while release acceptance is open. This is a working development candidate, not a claim that every product gate has passed.

## Milestone handoff

| Milestone | Implemented and automated | Remaining acceptance |
| --- | --- | --- |
| 1. Foundation | Package, CLI, lint/format, coverage, wheel/sdist builds, clean-environment install, Linux/macOS/Windows Actions matrix | Latest commit must pass all three hosted jobs |
| 2. Benchmark | 30 distinct fixtures, validated file/claim/action definitions, reproducible commits, independently calculated baseline, raw results and metrics | Independent label review and realistic baseline review |
| 3. Persistence | SQLite schema version 1, transactional writes, nested rollback, isolation, audit records | Future schema changes require explicit migrations |
| 4. Capture/detection | Exact reads, optional Python AST digest, changes/renames/deletions/mode checks, root aliases, path/symlink protections | Actual-agent capture coverage must be measured |
| 5. Impact engine | Transitive suspicion, unrelated controls, explicit alternative evidence groups, unknown evidence | Real repository dependency coverage is unproven |
| 6. Policy/verification | Validated policy, allow/verify/block/unresolved, explicit reaffirmation/checks, revision/content/policy-bound approvals, deterministic replay | Human confirmation remains a trust input |
| 7. CLI/hooks | Session lifecycle, Read/Edit/Write capture, idempotent settings merge, compaction persistence, concurrent-event/race regressions | Linux Codex discovery/trust and compaction exercised; Codex first, native Linux only for V1. Claude/macOS/Windows native hooks remain experimental |
| 8. PR integration | Trusted-base policy, receipts, exact SHAs, fork isolation, comment updates, stale-run suppression, artifacts; live same-repository/fork and disposable merge-protection validation | Blocking policy and pinned workflow deployed; main requires PRs, four checks, strict updates, and administrator enforcement |
| 9. Evaluation/release | Installed-wheel benchmark smoke check and installation timing, 5,000-file simulated hook latency check, operational/security documentation | Reviewed real-agent trials, customer validation, final release decision |

## Verified automated evidence

The path-fix CI run passed all Linux, macOS, and Windows jobs: [run 41518933457](https://github.com/abdulwasea89/Verix/actions/runs/41518933457). Each job includes tests, coverage, lint/format, package building, and installed-wheel benchmark execution. Follow-up commits add further hook, PR, and performance checks; inspect their own runs before relying on them.

The current local suite passes 89 tests plus parameterized subtests, with 95.53% engine statement coverage on Python 3.14. Workflow JavaScript tests execute under Node.js with mocked GitHub APIs; they do not post comments. CI supplies Node.js and runs the suite on Python 3.12 across Linux, macOS, and Windows.

Windows latency now measures 281 ms median and 282 ms p95 across the unchanged 20-sample, 5,000-file fixture in [run 41531655667](https://github.com/abdulwasea89/Verix/actions/runs/41531655667), meeting the proposed 300 ms / 1 s targets on that runner. Earlier measurements reached 391 ms median after initial batching and varied above target during subsequent runs.

The measured fix combines Git repository/revision discovery, limits mode queries to observed files, removes redundant filesystem checks, and avoids constructing unrelated command parsers for hook invocations. The discovery revision is consumed once and always checked again after evidence reads; stale discovery is refreshed once, and continuing races are rejected. Index snapshots bind content and file identity, including rewrites that restore original bytes. Linked worktrees and custom Git layouts retain full Git-based rechecks. Missing Windows mode-filter matches and platform command-length limits fall back to the complete index; other Git errors remain errors. Literal path queries prevent filename pattern expansion.

These measurements cover simulated hook command processes, not actual Claude Code transport. They are hardware/runner dependent, not a service-level guarantee. CI uploads each platform's own measurements and a cumulative call profile, and explicitly reports target misses. Fixture-setup timeouts are separate from measured hook timings and runtime Git timeouts.

The experimental Codex adapter has live Linux read, stale-denial, reaffirmation, patch-execution, resume, and audit-replay evidence. See [the setup and test limits](codex.md); this does not establish broad real-agent capture coverage. The current local simulated hook check measured 218 ms median / 252 ms p95 on 5,000 files.

## Benchmark limits

Default exact-byte blocking produces two false blocks among seven valid fixture actions. `verix bench run --ignore-python-formatting` applies the same explicit normalization to both guard conditions and avoids those two false blocks, while preserving the affected detections and hidden-dependency misses. Normalization is off by default and cannot prove correctness. Independent review and real-agent trials remain required.

## Deferred external gates

The user has deferred paid real-agent trials until implementation, commits/pushes, and automated checks are reported complete. Do not spend on the planned minimum 450 trials without a subsequent instruction. Live PR evidence is recorded in [the validation walkthrough](live-pr-validation.md); production blocking policy and main branch protection are now configured. Full-study acceptance is still pending independent protocol and result review. Independently reviewed labels, customer interviews, design partners, and a final release decision cannot be replaced with synthetic tests.

A narrow Codex adapter was subsequently authorized; its live evidence and limits are recorded in [codex.md](codex.md). No subscriptions, hosted history, dashboard, LLM claim extraction, or automatic release publishing are included in this V1 scope.

## Acceptance follow-through

Production bootstrap commit `7d9323d` passed [three-platform CI](https://github.com/abdulwasea89/Verix/actions/runs/41626315271). Main now requires PRs, `check / analyze`, all three platform CI checks, strict branch updates, and administrator enforcement, with no force pushes or deletions. Future work uses protected PRs. [PR #4](https://github.com/abdulwasea89/Verix/pull/4) exercises this rollout; its initial missing receipt correctly produced unresolved under the blocking base policy.

A resumable local diagnostic runner and [draft protocol](../benchmark/codex-protocol.md) are implemented. A previous three-condition smoke exposed absolute-path handling in the harness; it was corrected. The runner retains failed attempts and binds source, model, CLI version, and scenario hashes. Smoke mechanics do not establish benchmark or recovery acceptance. Full 450-trial runs require a named independent review matching the protocol hash and use only local ChatGPT authentication.

Interactive Linux Codex testing discovered repository-local handlers, reviewed/trusted them through `/hooks`, and captured a complete read. Real `/compact` exposed invalid PreCompact JSON. Commit `19602a2` changes that event to the supported common output `{"continue": true}`; the subsequent native compaction succeeded and stored evidence remained intact. These tests used an instrumented synthetic hook command delegating to the adapter. The interrupted two-session continuation was not accepted as completed evidence. A subsequent fresh [two-session native demo](../benchmark/results/native-sessions-20261103.json) did complete: a peer edit executed, a stale edit was denied, and a fresh read plus explicit operator verification allowed the reviewed edit. This uses real native Codex actions with controlled operator claim/completeness steps, not automatic claim inference.

GitHub user `abdulwasea992` is nominated for independent review, with no decision recorded. The [review/security/customer packet](release-acceptance.md) defines the remaining actual human evidence. No pilot teams, completed interviews, paid commitments, or final publishing approval have been supplied. Strict default fixture false blocks remain 2/7 (28.6%); release acceptance stays open and version remains 0.1.0.

The frozen current diagnostic smoke completed 3/3 trials with no protocol violations. Its [sanitized summary](../benchmark/results/codex-smoke-20261103.json) records a completed unguarded diagnostic and denied correct revised proposals under both guards; those denials are not successful recovery. This one-scenario smoke is not the 450-trial study or a release-accuracy estimate. Raw records remain local and private for reviewer inspection.
