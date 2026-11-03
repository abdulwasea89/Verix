"""Trial isolation, actual capture, independent baselines, and resumable outcomes; no model calls."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import run_codex_trials as trials


class TrialTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "trial"
        self.case = trials.load(trials.SCENARIOS)[0]

    def payload(self, root, tool, command, event, id, response=None):
        return {
            "session_id": "native",
            "cwd": str(root),
            "hook_event_name": event,
            "tool_use_id": id,
            "tool_name": tool,
            "tool_input": {"command": command},
            "tool_response": response,
        }

    def fake_invoke(self, directory, phase, prompt, session=None):
        root = directory / "repo"
        if phase == "read":
            trials.capture(
                directory,
                {"session_id": "native", "cwd": str(root), "hook_event_name": "SessionStart"},
            )
            for index, path in enumerate(self.case["reads"]):
                command = "cat " + path
                for event in ("PreToolUse", "PostToolUse"):
                    trials.capture(
                        directory,
                        self.payload(
                            root, "Bash", command, event, str(index), (root / path).read_text()
                        ),
                    )
            message = json.dumps(
                {
                    "plan": "Review the integration contract",
                    "claims": [c["id"] for c in self.case["claims"]],
                }
            )
        else:
            target = self.case["action"]["path"]
            body = "DECISION = " + repr(
                {
                    "contract_holds": self.case["action"]["valid"],
                    "affected_claims": self.case["expected_affected"],
                    "reason": "Reviewed current source",
                }
            )
            native_target = str(root / target)
            command = f"*** Begin Patch\n*** Add File: {native_target}\n+{body}\n*** End Patch"
            result = trials.capture(
                directory, self.payload(root, "apply_patch", command, "PreToolUse", "write")
            )
            if result.get("hookSpecificOutput", {}).get("permissionDecision") != "deny":
                (root / target).parent.mkdir(exist_ok=True)
                (root / target).write_text(body)
                trials.capture(
                    directory,
                    self.payload(
                        root,
                        "apply_patch",
                        command,
                        "PostToolUse",
                        "write",
                        "Exit code: 0\nWall time: 0.1 seconds\nOutput:\n"
                        "Success. Updated the following files:\nA " + target + "\n",
                    ),
                )
            message = "Revised diagnostic plan"
        return {"session": "native", "messages": [message], "usage": [], "seconds": 1.0}

    def test_three_conditions_and_completed_resume_never_calls_model_again(self):
        rows = []
        for condition in trials.CONDITIONS:
            directory = self.directory.with_name(condition)
            with patch.object(trials, "invoke", side_effect=self.fake_invoke) as invoke:
                row = trials.trial(directory, self.case, condition)
                self.assertEqual(invoke.call_count, 2)
                self.assertEqual(trials.trial(directory, self.case, condition), row)
                self.assertEqual(invoke.call_count, 2)
            self.assertEqual(row["task_completed"], condition == "no_guard")
            self.assertFalse(row["unsafe_execution"])
            rows.append(row)
        report = trials.summarize(rows, [self.case], "hash", 450)
        self.assertFalse(report["release_accepted"])
        self.assertEqual(report["completed_trials"], 3)
        self.assertEqual(report["conditions"]["verix"]["initial_capture_recall"], 1)
        self.assertLess(report["conditions"]["file_hash"]["initial_capture_recall"], 1)

    def test_literal_oracle_cannot_execute_code_or_accept_wrong_diagnosis(self):
        self.assertFalse(trials.validate_decision("__import__('os').system('false')", self.case))
        body = "DECISION = " + repr(
            {
                "contract_holds": False,
                "affected_claims": self.case["expected_affected"],
                "reason": "Changed export",
            }
        )
        self.assertTrue(trials.validate_decision(body, self.case))
        self.assertFalse(trials.validate_decision(body.replace("False", "True"), self.case))
        self.assertFalse(trials.validate_decision(body + "\nraise Exception()", self.case))

    def test_proposal_scoring_rejects_multiple_targets_and_malformed_patch(self):
        self.assertIsNone(trials.proposal_content("*** Begin Patch\n*** End Patch", "a.py"))
        self.assertIsNone(
            trials.proposal_content(
                "*** Begin Patch\n*** Add File: a.py\n+x\n*** Add File: b.py\n+y\n*** End Patch",
                "a.py",
            )
        )

    def test_credentials_and_provider_cannot_fall_back_to_api(self):
        with patch.dict(
            trials.os.environ,
            {
                "CODEX_API_KEY": "secret",
                "OPENAI_API_KEY": "secret",
                "OPENAI_BASE_URL": "https://example.invalid",
            },
        ):
            env = trials.child_environment()
            self.assertNotIn("CODEX_API_KEY", env)
            self.assertNotIn("OPENAI_API_KEY", env)
            self.assertNotIn("OPENAI_BASE_URL", env)
        command = trials.command(self.directory, self.directory)
        self.assertIn('forced_login_method="chatgpt"', command)
        self.assertIn("--ignore-user-config", command)

    def test_manifest_binds_implementation_scenarios_model_and_cli(self):
        cases = [self.case]
        first = trials.manifest(cases, "codex 1")
        self.assertNotEqual(
            first["protocol_hash"], trials.manifest(cases, "codex 2")["protocol_hash"]
        )
        changed = deepcopy(cases)
        changed[0]["claims"][0]["text"] += " changed"
        self.assertNotEqual(
            first["protocol_hash"], trials.manifest(changed, "codex 1")["protocol_hash"]
        )
        self.assertIn("implementation_sha256", first)

    def test_unknown_native_tools_and_out_of_protocol_writes_are_denied(self):
        with patch.object(trials, "invoke", side_effect=self.fake_invoke):
            trials.trial(self.directory, self.case, "no_guard")
        root = self.directory / "repo"
        for tool, command in (
            ("Bash", "echo x > stolen.py"),
            ("apply_patch", "*** Begin Patch\n*** Add File: stolen.py\n+x\n*** End Patch"),
        ):
            result = trials.capture(
                self.directory, self.payload(root, tool, command, "PreToolUse", "bad")
            )
            self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertFalse((root / "stolen.py").exists())

    def test_full_run_requires_matching_independent_review_before_trial_calls(self):
        from types import SimpleNamespace

        with (
            patch.object(trials.sys, "argv", ["runner", "--output", str(self.directory)]),
            patch.object(trials.sys, "platform", "linux"),
            patch.object(trials.subprocess, "check_output", return_value="codex 0.164.0"),
            patch.object(
                trials.subprocess,
                "run",
                return_value=SimpleNamespace(
                    returncode=0, stdout="Logged in using ChatGPT", stderr=""
                ),
            ),
            patch.object(trials, "trial") as invoke,
            self.assertRaisesRegex(ValueError, "independent review"),
        ):
            trials.main()
        invoke.assert_not_called()
        self.assertFalse(self.directory.exists())

    def test_failed_postprocessing_resume_reuses_completed_agent_response(self):
        with patch.object(trials, "invoke", side_effect=self.fake_invoke):
            row = trials.trial(self.directory, self.case, "no_guard")
        # Simulate a crash after native completion but before a result is committed.
        state = trials.read(self.directory / "state.json")
        state["phase"] = "seeded"
        trials.write(self.directory / "state.json", state)
        (self.directory / "result.json").unlink()
        with patch.object(trials, "invoke") as invoke:
            self.assertEqual(trials.trial(self.directory, self.case, "no_guard"), row)
        invoke.assert_not_called()

    def test_graph_commit_crash_does_not_duplicate_claims_on_resume(self):
        original = trials.write
        stopped = False

        def crash(path, data):
            nonlocal stopped
            if path.name == "state.json" and data.get("phase") == "captured" and not stopped:
                stopped = True
                raise RuntimeError("crash after SQLite commit")
            return original(path, data)

        with patch.object(trials, "invoke", side_effect=self.fake_invoke) as invoke:
            with patch.object(trials, "write", side_effect=crash):
                with self.assertRaisesRegex(RuntimeError, "SQLite commit"):
                    trials.trial(self.directory, self.case, "no_guard")
            row = trials.trial(self.directory, self.case, "no_guard")
            self.assertTrue(row["task_completed"])
            self.assertEqual(invoke.call_count, 2)
        engine = trials.Engine(self.directory / "repo")
        try:
            claims = [n for n in engine.store.nodes("native").values() if n["kind"] == "claim"]
            self.assertEqual(len(claims), len(self.case["claims"]))
        finally:
            engine.store.db.close()

    def test_hash_baseline_only_flags_explicitly_adopted_claims(self):
        with patch.object(trials, "invoke", side_effect=self.fake_invoke):
            trials.trial(self.directory, self.case, "no_guard")
        state = trials.read(self.directory / "state.json")
        state["condition"] = "file_hash"
        state["claims"] = {"unrelated": state["claims"]["unrelated"]}
        engine = trials.Engine(self.directory / "repo")
        try:
            self.assertEqual(trials.decision(engine, state), {"verdict": "allow", "flags": []})
        finally:
            engine.store.db.close()
