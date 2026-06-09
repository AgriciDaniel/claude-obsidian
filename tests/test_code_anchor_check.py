#!/usr/bin/env python3
"""test_code_anchor_check.py — hermetic tests for scripts/code-anchor-check.py.

Builds a throwaway git repo + a throwaway vault with anchored wiki pages and
asserts clean/DRIFTED/MOVED/UNTRACKED/MALFORMED detection and the no-git exit
codes. No network, no LLM.

Usage:
  python3 tests/test_code_anchor_check.py
"""
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "scripts" / "code-anchor-check.py"

spec = importlib.util.spec_from_file_location("code_anchor_check", HELPER)
cac = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cac)


class Fail(SystemExit):
    pass


def assert_true(label, cond, hint=""):
    if not cond:
        raise Fail(f"FAIL {label}{(': ' + hint) if hint else ''}")
    print(f"OK   {label}")


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=30)


def make_repo(tmp):
    repo = Path(tmp) / "repo"
    (repo / "app").mkdir(parents=True)
    (repo / "app" / "main.py").write_text("import os\nprint(1)\n", encoding="utf-8")
    run(["git", "init", "-q"], repo)
    run(["git", "config", "user.email", "t@example.com"], repo)
    run(["git", "config", "user.name", "Test"], repo)
    run(["git", "add", "app"], repo)
    run(["git", "commit", "-q", "-m", "init"], repo)
    return repo


def obj_sha(repo, path):
    return run(["git", "-C", str(repo), "rev-parse", f"HEAD:{path}"], repo).stdout.strip()


def make_vault(tmp, anchors, title="Crawler"):
    vault = Path(tmp) / "vault"
    (vault / "wiki" / "modules").mkdir(parents=True)
    body = ["---", "type: module", f'title: "{title}"', "source_type: code", "code_anchors:"]
    body += [f'  - "{a}"' for a in anchors]
    body += ["---", "", f"# {title}", ""]
    (vault / "wiki" / "modules" / f"{title}.md").write_text("\n".join(body), encoding="utf-8")
    return vault


def test_clean_when_anchors_match():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        anchors = [f"app/main.py@{obj_sha(repo, 'app/main.py')}", f"app@{obj_sha(repo, 'app')}"]
        vault = make_vault(tmp, anchors)
        findings, checked, clean = cac.scan(str(repo), vault)
        assert_true("checked both anchors", checked == 2, hint=str(checked))
        assert_true("all clean", clean == 2 and not any(findings.values()), hint=str(findings))


def test_drift_detected_after_edit():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        anchors = [f"app/main.py@{obj_sha(repo, 'app/main.py')}"]
        vault = make_vault(tmp, anchors)
        (repo / "app" / "main.py").write_text("import os\nprint(2)\nprint(3)\n", encoding="utf-8")
        run(["git", "add", "app"], repo)
        run(["git", "commit", "-q", "-m", "edit"], repo)
        findings, checked, clean = cac.scan(str(repo), vault)
        drifted = [f["path"] for f in findings["drifted"]]
        assert_true("main.py reported DRIFTED", "app/main.py" in drifted, hint=str(findings))


def test_moved_when_path_absent():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        vault = make_vault(tmp, ["app/ghost.py@" + ("0" * 40)])
        findings, _, _ = cac.scan(str(repo), vault)
        moved = [f["path"] for f in findings["moved"]]
        assert_true("ghost path reported MOVED/DELETED", "app/ghost.py" in moved, hint=str(findings))


def test_untracked_when_on_disk_not_in_head():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        (repo / "app" / "new.py").write_text("x=1\n", encoding="utf-8")  # on disk, never committed
        vault = make_vault(tmp, ["app/new.py@" + ("0" * 40)])
        findings, _, _ = cac.scan(str(repo), vault)
        untracked = [f["path"] for f in findings["untracked"]]
        assert_true("uncommitted file reported UNTRACKED", "app/new.py" in untracked, hint=str(findings))


def test_malformed_anchor():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        vault = make_vault(tmp, ["no-at-sign-here"])
        findings, _, _ = cac.scan(str(repo), vault)
        assert_true("anchor without @ is MALFORMED", len(findings["malformed"]) == 1, hint=str(findings))


def test_cli_exit_11_non_git_repo():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        vault = make_vault(tmp, ["app/main.py@" + obj_sha(repo, "app/main.py")])
        nongit = Path(tmp) / "plain"
        nongit.mkdir()
        r = subprocess.run([sys.executable, str(HELPER), "--repo", str(nongit), "--vault", str(vault)],
                           capture_output=True, text=True, timeout=30)
        assert_true("non-git repo → exit 11", r.returncode == 11, hint=f"rc={r.returncode} {r.stderr}")


def test_cli_report_written():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        vault = make_vault(tmp, [f"app/main.py@{obj_sha(repo, 'app/main.py')}"])
        # edit so there is drift to report
        (repo / "app" / "main.py").write_text("print('changed')\n", encoding="utf-8")
        run(["git", "add", "app"], repo)
        run(["git", "commit", "-q", "-m", "edit"], repo)
        report = Path(tmp) / "report.md"
        r = subprocess.run([sys.executable, str(HELPER), "--repo", str(repo),
                            "--vault", str(vault), "--report", str(report)],
                           capture_output=True, text=True, timeout=30)
        assert_true("cli rc=0", r.returncode == 0, hint=r.stderr)
        text = report.read_text()
        assert_true("report has Code Drift section", "## Code Drift" in text, hint=text)
        assert_true("report lists Drifted", "Drifted" in text, hint=text)


def test_cli_peek():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        vault = make_vault(tmp, [f"app/main.py@{obj_sha(repo, 'app/main.py')}"])
        r = subprocess.run([sys.executable, str(HELPER), "--vault", str(vault), "--peek"],
                           capture_output=True, text=True, timeout=30)
        assert_true("peek rc=0", r.returncode == 0, hint=r.stderr)
        assert_true("peek reports 1 anchored page", '"anchored_pages": 1' in r.stdout, hint=r.stdout)


def main():
    print("=== test_code_anchor_check.py ===")
    test_clean_when_anchors_match()
    test_drift_detected_after_edit()
    test_moved_when_path_absent()
    test_untracked_when_on_disk_not_in_head()
    test_malformed_anchor()
    test_cli_exit_11_non_git_repo()
    test_cli_report_written()
    test_cli_peek()
    print("\nAll code-anchor-check tests passed.")


if __name__ == "__main__":
    main()
