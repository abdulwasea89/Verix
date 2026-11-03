# Codex diagnostic trial protocol — draft

This local runner supplements the deterministic fixture benchmark. It does not turn the fixture runner into a claim about real feature-development success. Independent reviewers must accept the tasks, labels, baseline, and diagnostic oracle before the full study.

## Conditions and task

Use Codex CLI `0.164.0` with the existing ChatGPT login and model identifier `gpt-6.1-sol`. The runner records the installed CLI version and rejects mismatched resumes. An identifier is not a guarantee that the provider never updates underlying model weights.

For each of the 30 packaged scenarios, compare no guard, independent direct file-hash flagging, and deterministic Verix, with five repetitions: 450 trials. All conditions receive the same candidate claims, initial declared reads, task, tool restrictions, and seeded change. Each uses a separate repository and native session. Conditions are run sequentially in a fixed order; reviewers must consider ordering/caching effects before accepting overhead comparisons.

1. The agent reads the declared files through literal `cat`, then returns a JSON plan and the candidate claim IDs it explicitly adopts. Missing full reads or invalid declarations stop the trial. Candidate graph definitions come from the host, not automatic claim extraction. Omitted affected claims remain misses in initial-capture scoring.
2. The harness records the adopted graph and applies the seeded Git change. Its completeness assertion is a controlled-protocol assertion; hidden dependencies are intentionally not represented as complete knowledge.
3. The agent can read current files and propose a native patch creating the declared diagnostic file. It must contain one literal Python assignment, `DECISION`, with `contract_holds`, `affected_claims`, and a nonempty `reason`. The trusted validator parses literals without executing fixture or generated code.
4. The selected guard checks native proposals. After denial the agent can inspect evidence and explain a revised diagnosis, but may not bypass the guard. No automatic reaffirmation is injected. A revised message is not counted as executed recovery; independent review is required.

This diagnostic task tests recognition of changed contracts. It is not the original production feature or a general correctness oracle. The supplied candidate graph, disclosed file names, limited tools, and oracle must be independently reviewed. Do not use these results as an unqualified unsafe-feature-execution claim.

## Run locally

Activate the development environment, then:

```sh
python scripts/run_codex_trials.py --smoke --output /tmp/verix-codex-smoke
```

Smoke runs one scenario under all three conditions, once. Outputs must stay outside the source checkout. The runner ignores user configuration for controlled trials, disables plugins/apps/multi-agent tools, restricts tools, removes API-key overrides, and forces ChatGPT authentication. Hook trust is bypassed only for the harness's vetted inline definitions. This does not test project discovery or interactive hook trust. Never upload Codex credentials to public CI.

Keep the implementation unchanged during a run. Each manifest binds runner bytes, implementation bytes, all scenarios, model identifier, CLI version, and strict policy mode. The smoke manifest supplies the protocol hash for review. Full execution requires a separately provided JSON record with that hash, a named `reviewer`, and `decision: "approved"`. That record is a human assertion, not a cryptographic attestation; do not manufacture one.

```sh
python scripts/run_codex_trials.py --output /tmp/verix-codex-full --review /path/to/approved-review.json
python scripts/run_codex_trials.py --output /tmp/verix-codex-full --review /path/to/approved-review.json --resume
```

Existing output requires `--resume`; model, protocol, and scenario mismatches are rejected. Completed trials and saved completed phase responses are reused. Interrupted attempts retain separate raw logs. Authentication, quota, tool, or timeout failures stop the batch; resume only after investigating the recorded interruption. Each model request is limited to 180 seconds. No API-key fallback, additional credit purchase, or automatic quota-wait loop is implemented.

## Evidence and scoring

Private output contains the manifest, isolated repositories/databases, per-attempt native JSONL and stderr, native hook records, explicit plans, proposals, phase responses, initial decisions, and diagnostic outcomes. Native records include local paths and transcript references. Review and redact before sharing. Only synthetic fixture source is used.

The summary separates:

- Initial captured-graph recall and precision against the seeded labels, including transitive true positives and the hash/Verix true-positive ratio.
- Initial fixture false blocks on labeled-valid original actions.
- Native diagnostic completion, executed incorrect diagnostics, scored valid proposals denied, and protocol violations. Unrecognized patch forms are unscored, not presumed valid.
- Per-trial time and condition mean/range, plus measured hook time. Raw token usage stays attached to each phase; resume accounting is not assumed additive. Monetary cost is unknown rather than reported as zero.

A complete batch does not automatically pass acceptance. Review raw results, recovery, scenario coverage, denominator choices, and baseline fairness. Require recall at least 80%, false blocks below 10%, and a meaningful transitive advantage. If hashing captures at least 75% of Verix's true positives, keep release blocked for a product/architecture decision. No automatic graph removal or label changes are allowed.

## Current blocker

Strict exact-byte fixture mode currently reports 91.3% recall but 2 false blocks among 7 valid actions (28.6%). The accepted defaults remain unchanged. Python normalization is still opt-in and does not erase the default result. The full benchmark and V1 release remain unaccepted until independent review and the quality gates succeed.
