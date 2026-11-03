# Live pull request validation

## Verified on GitHub — 2026-11-03

Validation used synthetic files, a disposable blocking-policy base branch, a same-repository [PR #1](https://github.com/abdulwasea89/Verix/pull/1), and a real organization-fork [PR #2](https://github.com/abdulwasea89/Verix/pull/2). Product `main` policy and branch protection were not changed.

| Case | Live result and evidence |
| --- | --- |
| Current receipt | `allow`; analysis and comment jobs passed ([run](https://github.com/abdulwasea89/Verix/actions/runs/41618344929/attempts/1)) |
| Stale receipt plus PR policy downgrade | `block` under the trusted base's blocking policy; analysis failed ([run](https://github.com/abdulwasea89/Verix/actions/runs/41618538511)) |
| Malformed receipt | `unresolved`; analysis failed and report uploaded ([run](https://github.com/abdulwasea89/Verix/actions/runs/41618883370)) |
| Missing receipt | `unresolved`; analysis failed and report uploaded ([run](https://github.com/abdulwasea89/Verix/actions/runs/41618995261)) |
| Reviewed source change with fresh receipt | `allow` using corrected implementation `0c60404cfaa8c2ad8e130c4f34e2a9c0c52d0c57` ([run](https://github.com/abdulwasea89/Verix/actions/runs/41619154096)) |
| Real fork | Analysis and artifact succeeded, comment job skipped, no Verix comment ([initial run](https://github.com/abdulwasea89/Verix/actions/runs/41618524066), [fixed-version run](https://github.com/abdulwasea89/Verix/actions/runs/41619164320)) |
| Comment updates | Same bot comment ID `6601013869` changed through allow, block, unresolved, and allow; no duplicate Verix comments |
| Stale rerun | Rerunning the original allow event left the newer block comment unchanged; log confirmed revision guard ([attempt 2](https://github.com/abdulwasea89/Verix/actions/runs/41618344929/attempts/2)) |
| Passing check permits merge | [PR #3](https://github.com/abdulwasea89/Verix/pull/3) merged only into the disposable protected base after [its passing run](https://github.com/abdulwasea89/Verix/actions/runs/41619381633) |
| Behind an advanced base | Conflict-free PR had `allow` and successful jobs ([run](https://github.com/abdulwasea89/Verix/actions/runs/41619732756)), but GitHub reported `BEHIND` and rejected merge with HTTP 405 |
| Failing required check | Test branch required `check / analyze` from GitHub Actions, strict updates, and admin enforcement; merge API rejected the stale PR with HTTP 405 |

The behind-branch run retained the earlier event base SHA `6c3818c`; the target had advanced to `354423e`. Strict protection prevented that older-base result from authorizing a merge. This is why an up-to-date requirement is necessary alongside the Verix check. An initial probe also encountered a receipt conflict; the final probe used matching receipt contents to isolate freshness.

Test PRs #1 and #2 were closed without merging; #3 merged only into the disposable base. Upstream test branches and their protection rule were removed. The temporary organization fork was archived with Actions disabled: deleting it requires a `delete_repo` token scope that the current login does not have.

Fork job setup logs confirmed `Contents: read`, `Metadata: read`, and `Secret source: None`. Downloaded reports were checked against their exact base/head SHAs. These runs exercised the reusable workflow in real `pull_request` events, rather than simulated event payloads.

Preparing recovery exposed a false block: comparing a fresh PR receipt against the earlier base contents invalidated the PR's own reviewed edits. The fix compares up-to-date evidence against head, while retaining conservative base analysis for diverged branches. Regression tests cover both behaviors, and the corrected version passed the live same-repository and fork recovery runs.

The implementation fix passed 79 local tests (95.53% engine coverage), Ruff, and package building. Its [hosted CI run](https://github.com/abdulwasea89/Verix/actions/runs/41619126012) passed Linux, macOS, and Windows checks, including installed-wheel and performance checks.

## Enable it in your repository

1. Install Verix and commit a reviewed `.verix.yml` to the target branch first. Start with advisory mode; choose `mode: blocking` when ready to enforce verdicts. A policy introduced only in a PR cannot change the trusted base policy.
2. Add `.github/workflows/verix.yml` on that target branch:

```yaml
name: Verix
on: [pull_request]
permissions:
  contents: read
  actions: read
  pull-requests: write
jobs:
  check:
    uses: abdulwasea89/Verix/.github/workflows/verix-pr.yml@0c60404cfaa8c2ad8e130c4f34e2a9c0c52d0c57
    with:
      tool-ref: 0c60404cfaa8c2ad8e130c4f34e2a9c0c52d0c57
```

3. After the first run, configure the target branch's protection: require `check / analyze` from GitHub Actions, require the branch to be up to date, and apply the rule to administrators/bypass actors. Also require your normal test checks. GitHub's [protected-branch documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) explains these controls. Verix's `main` had no protection during this validation; test-branch protection does not protect `main`.

## Use it for each change

Create your feature branch and make the change. Review the current files and run relevant tests, then start a fresh session:

```sh
verix session start --agent codex
```

Copy the returned session ID into the following commands. Repeat `read` and `--evidence` for every file supporting your claim:

```sh
verix read src/example.py --session SESSION_ID
verix claim add "Reviewed example behavior" --session SESSION_ID --evidence src/example.py
verix session complete --session SESSION_ID --ack-limitations
verix receipt export --session SESSION_ID > .verix-receipt.json
```

Inspect the receipt, commit it with your changes, push, and open the PR. On the PR, check `check / analyze`, the Verix comment for same-repository PRs, and the `verix-report` workflow artifact. Forks get the artifact and job summary without a Verix comment.

If blocked, review the changed files, capture fresh reads, and register fresh claims in a new session before exporting again. Local `--reaffirm` approvals are stripped from receipts; they cannot authorize CI. If unresolved, inspect the artifact for missing/malformed receipts or incomplete evidence. Never change the PR policy to bypass a finding.

Receipts are self-reported metadata and can include sensitive paths. Hooks and green checks do not prove correctness or hidden-dependency coverage. Merge queues and independent-contributor approval settings were not exercised by this validation.
