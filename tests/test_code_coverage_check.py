#!/usr/bin/env python3
"""test_code_coverage_check.py — hermetic tests for scripts/code-coverage-check.py.

Builds a throwaway git repo + a throwaway vault and asserts coverage-gap detection
(including the ancestor-coverage-does-not-suppress-siblings rule) and ingest-staleness
(behind-count, missing ingest_commit, orphaned commit) plus the no-git exit code.
No network, no LLM.

Usage:
  python3 tests/test_code_coverage_check.py
"""
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "scripts" / "code-coverage-check.py"

spec = importlib.util.spec_from_file_location("code_coverage_check", HELPER)
cov = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cov)


class Fail(SystemExit):
    pass


def assert_true(label, cond, hint=""):
    if not cond:
        raise Fail(f"FAIL {label}{(': ' + hint) if hint else ''}")
    print(f"OK   {label}")


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=30)


def make_repo(tmp):
    """app/domain/{a,b,c}/svc.py — three sibling domain packages."""
    repo = Path(tmp) / "repo"
    for pkg in ("a", "b", "c"):
        d = repo / "app" / "domain" / pkg
        d.mkdir(parents=True)
        (d / "svc.py").write_text(f"# {pkg}\nx = 1\n", encoding="utf-8")
    run(["git", "init", "-q"], repo)
    run(["git", "config", "user.email", "t@example.com"], repo)
    run(["git", "config", "user.name", "Test"], repo)
    run(["git", "add", "."], repo)
    run(["git", "commit", "-q", "-m", "init"], repo)
    return repo


def head(repo):
    return run(["git", "-C", str(repo), "rev-parse", "HEAD"], repo).stdout.strip()


def make_page(vault, rel, title, source_paths, ingest_commit):
    p = vault / "wiki" / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    body = ["---", "type: module", f'title: "{title}"', "source_type: code", "source_paths:"]
    body += [f'  - "{sp}"' for sp in source_paths]
    body += [f'ingest_commit: "{ingest_commit}"', "---", "", f"# {title}", ""]
    p.write_text("\n".join(body), encoding="utf-8")


def fresh_vault(tmp, name="vault"):
    vault = Path(tmp) / name
    (vault / "wiki" / "modules").mkdir(parents=True)
    return vault


def test_gap_detected_for_undocumented_sibling():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp); h = head(repo)
        vault = fresh_vault(tmp)
        make_page(vault, "modules/a.md", "A", ["app/domain/a/"], h)
        make_page(vault, "modules/b.md", "B", ["app/domain/b/"], h)
        gaps, covered, containers = cov.scan_coverage(str(repo), vault)
        paths = [g["path"] for g in gaps]
        assert_true("undocumented sibling c is a gap", "app/domain/c" in paths, hint=str(paths))
        assert_true("documented a is NOT a gap", "app/domain/a" not in paths, hint=str(paths))


def test_ancestor_coverage_does_not_suppress_sibling():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp); h = head(repo)
        vault = fresh_vault(tmp)
        # one broad page maps the whole app/domain; one dedicated page maps a
        make_page(vault, "modules/domain.md", "Domain", ["app/domain/"], h)
        make_page(vault, "modules/a.md", "A", ["app/domain/a/"], h)
        gaps, _, _ = cov.scan_coverage(str(repo), vault)
        paths = [g["path"] for g in gaps]
        assert_true("b still flagged despite broad app/domain page", "app/domain/b" in paths, hint=str(paths))
        assert_true("c still flagged", "app/domain/c" in paths, hint=str(paths))
        assert_true("a (dedicated) not flagged", "app/domain/a" not in paths, hint=str(paths))


def test_staleness_behind_count():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp); h0 = head(repo)
        vault = fresh_vault(tmp)
        make_page(vault, "modules/a.md", "A", ["app/domain/a/"], h0)
        # advance HEAD by one commit
        (repo / "app" / "domain" / "a" / "svc.py").write_text("x = 2\n", encoding="utf-8")
        run(["git", "add", "."], repo); run(["git", "commit", "-q", "-m", "edit"], repo)
        h1 = head(repo)
        stale = cov.scan_staleness(str(repo), vault, h1)
        s = stale["summary"][0]
        assert_true("ingest is ancestor of HEAD", s["ancestor"] is True, hint=str(s))
        assert_true("reports 1 commit behind", s["behind"] == 1, hint=str(s))


def test_missing_ingest_commit_flagged():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp); h = head(repo)
        vault = fresh_vault(tmp)
        make_page(vault, "modules/a.md", "A", ["app/domain/a/"], "")  # empty ingest_commit
        stale = cov.scan_staleness(str(repo), vault, h)
        assert_true("missing ingest_commit reported", len(stale["missing"]) == 1, hint=str(stale))


def test_orphaned_ingest_commit():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp); h = head(repo)
        vault = fresh_vault(tmp)
        make_page(vault, "modules/a.md", "A", ["app/domain/a/"], "0" * 40)  # not in history
        stale = cov.scan_staleness(str(repo), vault, h)
        assert_true("non-ancestor ingest is orphaned", len(stale["orphaned"]) == 1, hint=str(stale))


def test_cli_exit_11_non_git_repo():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp); h = head(repo)
        vault = fresh_vault(tmp)
        make_page(vault, "modules/a.md", "A", ["app/domain/a/"], h)
        nongit = Path(tmp) / "plain"; nongit.mkdir()
        r = subprocess.run([sys.executable, str(HELPER), "--repo", str(nongit), "--vault", str(vault)],
                           capture_output=True, text=True, timeout=30)
        assert_true("non-git repo → exit 11", r.returncode == 11, hint=f"rc={r.returncode} {r.stderr}")


def test_cli_report_and_peek():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp); h = head(repo)
        vault = fresh_vault(tmp)
        make_page(vault, "modules/a.md", "A", ["app/domain/a/"], h)
        report = Path(tmp) / "report.md"
        r = subprocess.run([sys.executable, str(HELPER), "--repo", str(repo),
                            "--vault", str(vault), "--report", str(report)],
                           capture_output=True, text=True, timeout=30)
        assert_true("cli rc=0", r.returncode == 0, hint=r.stderr)
        text = report.read_text()
        assert_true("report has Coverage & Staleness", "## Coverage & Staleness" in text, hint=text)
        assert_true("report lists the c gap", "app/domain/c" in text, hint=text)
        p = subprocess.run([sys.executable, str(HELPER), "--vault", str(vault), "--peek"],
                           capture_output=True, text=True, timeout=30)
        assert_true("peek rc=0 + reports code_pages", p.returncode == 0 and '"code_pages": 1' in p.stdout, hint=p.stdout)


def main():
    print("=== test_code_coverage_check.py ===")
    test_gap_detected_for_undocumented_sibling()
    test_ancestor_coverage_does_not_suppress_sibling()
    test_staleness_behind_count()
    test_missing_ingest_commit_flagged()
    test_orphaned_ingest_commit()
    test_cli_exit_11_non_git_repo()
    test_cli_report_and_peek()
    print("\nAll code-coverage-check tests passed.")


if __name__ == "__main__":
    main()
