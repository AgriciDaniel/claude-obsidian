#!/usr/bin/env python3
"""test_wiki_link_resolve_check.py — hermetic tests for scripts/wiki-link-resolve-check.py.

Builds throwaway vaults (no git needed) and asserts Obsidian-accurate link resolution:
resolves via filename OR alias; flags unresolved links; flags Mode B code pages
unreachable by their own title; flags shadowed titles (a decoy stub stealing the name);
ignores links inside code fences and inside templates/meta.

Usage:
  python3 tests/test_wiki_link_resolve_check.py
"""
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "scripts" / "wiki-link-resolve-check.py"

spec = importlib.util.spec_from_file_location("wiki_link_resolve_check", HELPER)
lr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lr)


class Fail(SystemExit):
    pass


def assert_true(label, cond, hint=""):
    if not cond:
        raise Fail(f"FAIL {label}{(': ' + hint) if hint else ''}")
    print(f"OK   {label}")


def write(vault, rel, frontmatter, body=""):
    p = vault / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    fm = "\n".join(["---", *frontmatter, "---"])
    p.write_text(fm + "\n\n" + body + "\n", encoding="utf-8")


def fresh(tmp, name="vault"):
    v = Path(tmp) / name
    (v / "wiki" / "modules").mkdir(parents=True)
    return v


def test_resolves_via_alias():
    with tempfile.TemporaryDirectory() as tmp:
        v = fresh(tmp)
        write(v, "wiki/modules/domain-content-generation.md",
              ['type: module', 'title: "Content Generation"', 'source_type: code',
               'aliases: ["Content Generation"]'], "# Content Generation")
        write(v, "wiki/modules/api-layer.md",
              ['type: module', 'title: "API Layer"', 'source_type: code',
               'aliases: ["API Layer"]'], "Calls [[Content Generation]] heavily.")
        res = lr.scan(v)
        assert_true("aliased title link resolves", res["unresolved"] == {}, hint=str(res["unresolved"]))
        assert_true("no unreachable code pages", res["unreachable"] == [], hint=str(res["unreachable"]))


def test_unresolved_and_unreachable_without_alias():
    with tempfile.TemporaryDirectory() as tmp:
        v = fresh(tmp)
        # slug filename, no alias → title link cannot resolve
        write(v, "wiki/modules/domain-content-generation.md",
              ['type: module', 'title: "Content Generation"', 'source_type: code'],
              "# Content Generation")
        write(v, "wiki/modules/api-layer.md",
              ['type: module', 'title: "API Layer"', 'source_type: code',
               'aliases: ["API Layer"]'], "Calls [[Content Generation]] heavily.")
        res = lr.scan(v)
        assert_true("title link is unresolved", "Content Generation" in res["unresolved"],
                    hint=str(res["unresolved"]))
        titles = [u["title"] for u in res["unreachable"]]
        assert_true("page unreachable by its own title", "Content Generation" in titles, hint=str(titles))


def test_shadowed_by_decoy_stub():
    with tempfile.TemporaryDirectory() as tmp:
        v = fresh(tmp)
        # real page is a slug with no self-alias; an empty decoy steals the name
        write(v, "wiki/modules/api-layer.md",
              ['type: module', 'title: "API Layer"', 'source_type: code'], "# API Layer real")
        (v / "API Layer.md").write_text("", encoding="utf-8")  # empty root decoy
        res = lr.scan(v)
        shadowed_titles = [s["title"] for s in res["shadowed"]]
        assert_true("real page is shadowed by the decoy", "API Layer" in shadowed_titles, hint=str(res["shadowed"]))


def test_code_fence_links_ignored():
    with tempfile.TemporaryDirectory() as tmp:
        v = fresh(tmp)
        write(v, "wiki/modules/api-layer.md",
              ['type: module', 'title: "API Layer"', 'source_type: code',
               'aliases: ["API Layer"]'],
              "Example: `[[Inline Example]]`\n\n```\n[[Fenced Example]]\n```\n")
        res = lr.scan(v)
        assert_true("inline-code link ignored", "Inline Example" not in res["unresolved"], hint=str(res["unresolved"]))
        assert_true("fenced-code link ignored", "Fenced Example" not in res["unresolved"], hint=str(res["unresolved"]))


def test_templates_and_meta_excluded():
    with tempfile.TemporaryDirectory() as tmp:
        v = fresh(tmp)
        (v / "_templates").mkdir(parents=True, exist_ok=True)
        write(v, "_templates/decision.md", ['type: decision', 'title: "ADR-NNNN"'], "See [[Other Table]].")
        write(v, "wiki/meta/lint-report-2026-06-09.md",
              ['type: meta', 'title: "Lint Report"'], "Example [[Some Broken Example]].")
        write(v, "wiki/modules/api-layer.md",
              ['type: module', 'title: "API Layer"', 'source_type: code', 'aliases: ["API Layer"]'],
              "# clean")
        res = lr.scan(v)
        assert_true("template example link not counted", "Other Table" not in res["unresolved"], hint=str(res["unresolved"]))
        assert_true("meta example link not counted", "Some Broken Example" not in res["unresolved"], hint=str(res["unresolved"]))
        assert_true("template (ADR-NNNN) not flagged unreachable",
                    all(u["title"] != "ADR-NNNN" for u in res["unreachable"]), hint=str(res["unreachable"]))


def test_cli_peek_and_report():
    with tempfile.TemporaryDirectory() as tmp:
        v = fresh(tmp)
        write(v, "wiki/modules/domain-content-generation.md",
              ['type: module', 'title: "Content Generation"', 'source_type: code'], "x")
        report = Path(tmp) / "report.md"
        r = subprocess.run([sys.executable, str(HELPER), "--vault", str(v), "--report", str(report)],
                           capture_output=True, text=True, timeout=30)
        assert_true("cli rc=0", r.returncode == 0, hint=r.stderr)
        assert_true("report has Link Resolution", "## Link Resolution" in report.read_text(), hint=report.read_text())
        p = subprocess.run([sys.executable, str(HELPER), "--vault", str(v), "--peek"],
                           capture_output=True, text=True, timeout=30)
        assert_true("peek rc=0", p.returncode == 0 and '"pages":' in p.stdout, hint=p.stdout)


def main():
    print("=== test_wiki_link_resolve_check.py ===")
    test_resolves_via_alias()
    test_unresolved_and_unreachable_without_alias()
    test_shadowed_by_decoy_stub()
    test_code_fence_links_ignored()
    test_templates_and_meta_excluded()
    test_cli_peek_and_report()
    print("\nAll wiki-link-resolve-check tests passed.")


if __name__ == "__main__":
    main()
