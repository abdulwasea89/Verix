# V1 acceptance handoff

This is an evidence checklist, not a completed certification. Keep raw participant data and trial logs private; commit only consented, sanitized summaries and evidence references.

## Release scope

V1 targets the deterministic local CLI and Codex integration, with native Codex hooks supported on Linux only after live acceptance. CLI/engine packaging remains tested on Linux, macOS, and Windows. Native macOS/Windows hooks and Claude are experimental until independently validated. Hosted accounts, subscriptions, automatic claim extraction, and LLM verification remain outside scope.

## Independent benchmark review — nominated reviewer, pending decision

The owner nominated GitHub user `abdulwasea992`. The account exists; independence, scope acceptance, and an actual review decision remain unverified. No approval is implied and no outreach has been sent.

Provide a reviewer handle, date, reviewed repository revision, protocol hash, decision, and unresolved findings. The reviewer must be independent of implementation and label authorship. They must check:

- All 30 scenario claims, evidence links, expected affected labels, and action-validity labels, especially hidden dependencies and benign formatting.
- Diagnostic task validity and oracle limitations, explicit agent adoption, native capture coverage, and missing-read handling.
- Direct-hash baseline fairness, common tools/prompts/policy, fixed-order/cache effects, and transitive comparisons.
- Raw errors, omitted trials, blocked valid proposals, recovery evidence, and latency/token denominators.
- The difference between synthetic initial verdicts, native diagnostic completion, and actual customer feature outcomes.

Use the [frozen-protocol runner guide](../benchmark/codex-protocol.md). A named matching protocol approval is required for the full 450-trial run. Do not use an AI self-review as independent human acceptance.

## Independent security review — pending assignment and decision

Record reviewer identity, version, environment, findings, remediation references, and final decision. Check source/secret exposure, local database permissions, logs and receipts, path and symlink validation, hook trust, fork permissions, trusted workflow/policy pinning, and credential handling. Do this before private-repository pilots. Never request a participant's Codex credentials or private source in public issues.

## Customer discovery — awaiting participants

Recruit 20 teams using coding agents. Record an anonymized team ID, consent, interview date, dated incident, hours lost, safeguard used, and whether the incident happened in the previous 60 days. Ask for concrete examples rather than endorsing the product's assumptions.

- Proceed on demand evidence if at least six teams report a costly incident within that period.
- Fewer than three is a failed demand gate; three to five remains inconclusive.
- Missing participants or interviews remain pending, never completed by synthetic transcripts.

Participant/contact information and outreach authorization must come from the owner. No automatic outreach is authorized by preparing this packet.

## Three real-repository pilots — awaiting partners

After security review, each partner records consent, repository identifier, tested version, platform, start/end dates, advisory onboarding, subsequent enforcement choice, flags acted on, false blocks, bypasses, failures, and measured rework. Partners retain their source and account credentials.

The strategy's willingness-to-pay gate requires at least one payment or written commitment of $500 or more among three design partners within a 90-day pilot window. Record the actual evidence and date. No payment collection, subscription service, or fabricated commitment is part of this implementation. Do not infer willingness to pay from successful installation.

## Engineering and final signoff

Maintain links to production branch protection, exact base/head PR reports, Linux native hook tests, three-platform CI/artifacts, clean installation, deterministic/no-network engine checks, audit replay, benchmark review, security review, and pilot findings.

Final acceptance requires all applicable evidence, reviewed recall at least 80%, false blocks below 10%, and the documented baseline advantage. Current strict fixture false blocks fail that gate. Human confirmation and unknown dependencies remain explicit trust inputs.

Keep version `0.1.0` while any gate is pending or failed. Only after all gates pass, prepare versioned artifacts and a release summary for the owner's final publishing authorization. Do not tag, publish, charge, or describe V1 as complete merely because the code or trial runner is finished.

Raw failed attempts must be reviewed before acceptance rather than deleted.
