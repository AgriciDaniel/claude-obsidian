#!/usr/bin/env python3
"""test_render_rules.py — hermetic tests for scripts/render-rules.py.

Covers the three things that can silently rot a single-source rule pack:

  PARSING     the strict YAML subset (inline lists, block lists, folded scalars,
              quoted scalars, booleans) and the empty-value-then-block-list case
              that a naive `""`-as-sentinel parser gets wrong.
  VALIDATION  id/location agreement, domain/dir agreement, severity, agents,
              required fields. A malformed rule must fail LOUDLY, not silently
              render half a pack.
  RENDERING   per-agent output paths, agent subscription, severity ordering, and
              managed-block splicing into files we only partly own (AGENTS.md,
              GEMINI.md) without eating the author's prose.

Hermetic: every test builds a throwaway rules/ tree under tempfile and
monkeypatches the module's RULES_DIR / VAULT_ROOT globals at it. The repo's real
rules/ and rendered files are never read or written. Stdlib only, no network.

Usage:
  python3 tests/test_render_rules.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "scripts" / "render-rules.py"

spec = importlib.util.spec_from_file_location("render_rules", HELPER)
rr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rr)


class Fail(SystemExit):
    pass


def assert_eq(label, expected, actual):
    if expected != actual:
        raise Fail(f"FAIL {label}: expected {expected!r}, got {actual!r}")
    print(f"OK   {label}")


def assert_true(label, cond, hint=""):
    if not cond:
        raise Fail(f"FAIL {label}{(': ' + hint) if hint else ''}")
    print(f"OK   {label}")


def assert_raises(label, exc_type, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc_type:
        print(f"OK   {label}")
        return
    except Exception as exc:  # noqa: BLE001 - we want the wrong-exception detail
        raise Fail(f"FAIL {label}: raised {exc.__class__.__name__} ({exc}), "
                   f"wanted {exc_type.__name__}")
    raise Fail(f"FAIL {label}: nothing raised, wanted {exc_type.__name__}")


# ─── fixtures ────────────────────────────────────────────────────────────────

RULE_TEMPLATE = """---
id: {id}
domain: {domain}
title: {title}
severity: {severity}
applies_when: >
  {applies_when}
globs:
  - "**/*"
agents: [{agents}]
source: "{source}"
---

{body}
"""


def write_rule(rules_dir: Path, domain: str, slug: str, *, id_=None, title=None,
               severity="high", agents="claude, cursor, windsurf, copilot, codex, gemini",
               applies_when=None, source="test fixture", body="Do the thing.",
               raw=None) -> Path:
    """Write one rule file into <rules_dir>/<domain>/<slug>.md and return its path."""
    domain_dir = rules_dir / domain
    domain_dir.mkdir(parents=True, exist_ok=True)
    path = domain_dir / f"{slug}.md"
    if raw is not None:
        path.write_text(raw, encoding="utf-8")
        return path
    path.write_text(
        RULE_TEMPLATE.format(
            id=id_ if id_ is not None else f"{domain}/{slug}",
            domain=domain,
            title=title or f"Title for {slug}",
            severity=severity,
            applies_when=applies_when or f"You are about to touch {slug}.",
            agents=agents,
            source=source,
            body=body,
        ),
        encoding="utf-8",
    )
    return path


class Sandbox:
    """A temp vault with rules/ inside it, with the module's globals pointed at it."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.rules = self.root / "rules"
        self.rules.mkdir(parents=True, exist_ok=True)
        self._patches = [
            mock.patch.object(rr, "RULES_DIR", self.rules),
            mock.patch.object(rr, "VAULT_ROOT", self.root),
        ]

    def __enter__(self):
        for p in self._patches:
            p.start()
        return self

    def __exit__(self, *exc):
        for p in self._patches:
            p.stop()
        self._tmp.cleanup()
        return False


# ─── frontmatter parsing ─────────────────────────────────────────────────────

def test_parse_inline_list():
    text = '---\nagents: [claude, cursor]\nempty: []\n---\nbody\n'
    meta, body = rr.parse_frontmatter(text, Path("x.md"))
    assert_eq("inline list parsed", ["claude", "cursor"], meta["agents"])
    assert_eq("empty inline list parsed", [], meta["empty"])
    assert_eq("body extracted", "body\n", body)


def test_parse_block_list():
    text = '---\nglobs:\n  - "**/*.py"\n  - "src/**"\n---\nbody\n'
    meta, _ = rr.parse_frontmatter(text, Path("x.md"))
    assert_eq("block list parsed", ["**/*.py", "src/**"], meta["globs"])


def test_parse_empty_value_then_block_list_is_a_list():
    """REGRESSION. `globs:` has an EMPTY value, and its items arrive on the
    following indented lines. A parser that uses "" as its 'value pending'
    sentinel cannot tell that apart from a legitimately empty scalar, so it sees
    a str where a list belongs and dies with 'mixes scalar and list forms'.
    Every rule file in rules/ uses this exact shape, so the bug is total.
    """
    text = '---\nglobs:\n  - "**/*"\nagents:\n  - claude\n  - codex\n---\nbody\n'
    meta, _ = rr.parse_frontmatter(text, Path("x.md"))
    assert_true("empty-value key + block list is a LIST, not a str",
                isinstance(meta["globs"], list), hint=repr(meta["globs"]))
    assert_eq("globs items", ["**/*"], meta["globs"])
    assert_true("second empty-value key also a LIST",
                isinstance(meta["agents"], list), hint=repr(meta["agents"]))
    assert_eq("agents items", ["claude", "codex"], meta["agents"])


def test_parse_empty_value_with_no_continuation_is_empty_scalar():
    """The mirror image: a key whose continuation never arrives is "", not a
    sentinel object leaking into the parsed metadata."""
    text = '---\nsource:\ntitle: T\n---\nbody\n'
    meta, _ = rr.parse_frontmatter(text, Path("x.md"))
    assert_eq("dangling key → empty scalar", "", meta["source"])
    assert_eq("following key unaffected", "T", meta["title"])


def test_parse_folded_scalar():
    text = ('---\napplies_when: >\n  You are about to write a catch\n'
            '  or an except block.\n---\nbody\n')
    meta, _ = rr.parse_frontmatter(text, Path("x.md"))
    assert_eq("folded scalar joined with a space",
              "You are about to write a catch or an except block.",
              meta["applies_when"])


def test_parse_quoted_scalars_and_booleans():
    text = ('---\nsource: "Anthropic, 2025"\nalias: \'single quoted\'\n'
            'enabled: true\ndisabled: false\nplain: bare value\n---\nbody\n')
    meta, _ = rr.parse_frontmatter(text, Path("x.md"))
    assert_eq("double-quoted scalar unquoted", "Anthropic, 2025", meta["source"])
    assert_eq("single-quoted scalar unquoted", "single quoted", meta["alias"])
    assert_eq("true → bool", True, meta["enabled"])
    assert_eq("false → bool", False, meta["disabled"])
    assert_eq("bare scalar left alone", "bare value", meta["plain"])


def test_parse_comments_and_blank_lines_ignored():
    text = '---\n# a comment\n\nid: coding/x\n\n# another\n---\nbody\n'
    meta, _ = rr.parse_frontmatter(text, Path("x.md"))
    assert_eq("comments and blanks skipped", {"id": "coding/x"}, meta)


def test_parse_rejects_missing_and_unterminated_frontmatter():
    assert_raises("no frontmatter raises", rr.RuleError,
                  rr.parse_frontmatter, "just a body\n", Path("x.md"))
    assert_raises("unterminated frontmatter raises", rr.RuleError,
                  rr.parse_frontmatter, "---\nid: coding/x\nbody\n", Path("x.md"))
    assert_raises("unparseable line raises", rr.RuleError,
                  rr.parse_frontmatter, "---\nno colon here\n---\nbody\n", Path("x.md"))
    assert_raises("indented line with no key raises", rr.RuleError,
                  rr.parse_frontmatter, "---\n  - orphan\n---\nbody\n", Path("x.md"))


def test_parse_rejects_genuine_scalar_list_mixing():
    """The guard the regression test must NOT have disarmed: a key with a REAL
    scalar value followed by list items is still an error."""
    text = '---\nkey: a scalar\n  - and a list item\n---\nbody\n'
    assert_raises("real scalar/list mixing still raises", rr.RuleError,
                  rr.parse_frontmatter, text, Path("x.md"))


# ─── validation ──────────────────────────────────────────────────────────────

def test_load_rules_happy_path():
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "verify-by-execution", severity="blocker")
        write_rule(sb.rules, "coding", "match-surrounding-code", severity="medium")
        rules = rr.load_rules()
        assert_eq("loaded 2 rules", 2, len(rules))
        assert_eq("id derived from location", "coding/verify-by-execution", rules[0]["id"])
        assert_eq("globs parsed", ["**/*"], rules[0]["globs"])
        assert_eq("all 6 agents subscribed", 6, len(rules[0]["agents"]))
        assert_eq("applies_when folded to one line",
                  "You are about to touch verify-by-execution.",
                  rules[0]["applies_when"])


def test_id_must_equal_domain_slash_filename():
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "some-rule", id_="coding/a-different-slug")
        assert_raises("id/filename mismatch raises", rr.RuleError, rr.load_rules)


def test_domain_must_match_parent_directory():
    with Sandbox() as sb:
        # id agrees with the declared domain, but the file sits in coding/.
        write_rule(sb.rules, "coding", "some-rule",
                   id_="finance/some-rule")
        assert_raises("domain/dir mismatch raises", rr.RuleError, rr.load_rules)

    with Sandbox() as sb:
        # Same trick, written by hand so the declared domain is 'finance' while
        # the file lives in coding/ and the id agrees with the declared domain.
        raw = ("---\nid: finance/x\ndomain: finance\ntitle: T\nseverity: high\n"
               "applies_when: W\n---\n\nbody\n")
        write_rule(sb.rules, "coding", "x", raw=raw)
        assert_raises("declared domain not matching parent dir raises",
                      rr.RuleError, rr.load_rules)


def test_bad_severity_raises():
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "some-rule", severity="critical")
        assert_raises("unknown severity raises", rr.RuleError, rr.load_rules)


def test_unknown_agent_raises():
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "some-rule", agents="claude, gpt5")
        assert_raises("unknown agent raises", rr.RuleError, rr.load_rules)


def test_missing_required_field_raises():
    required = ("id", "domain", "title", "severity", "applies_when")
    for field in required:
        with Sandbox() as sb:
            lines = [
                "---",
                "id: coding/x",
                "domain: coding",
                "title: T",
                "severity: high",
                "applies_when: W",
                "---",
                "",
                "body",
                "",
            ]
            raw = "\n".join(l for l in lines if not l.startswith(f"{field}:"))
            write_rule(sb.rules, "coding", "x", raw=raw)
            assert_raises(f"missing '{field}' raises", rr.RuleError, rr.load_rules)


def test_duplicate_id_raises():
    """Two rule files claiming the same id cannot both load.

    Note on how this is enforced: because the id/location check runs first, a
    second file claiming an id already taken by another file necessarily
    disagrees with its own location, so it is that check which fires. The
    seen_ids guard downstream is defence in depth. Either way the load fails,
    which is the property that matters.
    """
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "original")
        write_rule(sb.rules, "coding", "copy", id_="coding/original")
        assert_raises("duplicate id raises", rr.RuleError, rr.load_rules)


def test_missing_rules_dir_raises():
    with tempfile.TemporaryDirectory() as tmp:
        with mock.patch.object(rr, "RULES_DIR", Path(tmp) / "nope"):
            assert_raises("absent rules/ raises", rr.RuleError, rr.load_rules)


# ─── ordering ────────────────────────────────────────────────────────────────

def test_rules_sort_by_severity():
    """blocker < high < medium. A pack that opens with the medium-severity rules
    buries the ones that actually stop a defect from shipping."""
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "c-medium", severity="medium")
        write_rule(sb.rules, "coding", "a-high", severity="high")
        write_rule(sb.rules, "coding", "b-blocker", severity="blocker")
        rules = rr.load_rules()
        assert_eq("severity order",
                  ["blocker", "high", "medium"], [r["severity"] for r in rules])


def test_rules_sort_is_stable_by_id_within_a_severity():
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "zebra", severity="high")
        write_rule(sb.rules, "coding", "alpha", severity="high")
        rules = rr.load_rules()
        assert_eq("ties broken by id",
                  ["coding/alpha", "coding/zebra"], [r["id"] for r in rules])


def test_domain_filter():
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "a")
        write_rule(sb.rules, "finance", "b")
        assert_eq("no filter → both domains", 2, len(rr.load_rules()))
        coding = rr.load_rules("coding")
        assert_eq("domain filter → 1 rule", 1, len(coding))
        assert_eq("domain filter → right rule", "coding/a", coding[0]["id"])


# ─── build_outputs: paths and subscription ───────────────────────────────────

def test_build_outputs_emits_the_right_path_per_agent():
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "a")
        outputs = rr.build_outputs(rr.load_rules())
        expected = {
            Path(".claude/rules/coding.md"),
            Path(".cursor/rules/coding.mdc"),
            Path(".windsurf/rules/coding.md"),
            Path(".github/instructions/coding.instructions.md"),
            Path("AGENTS.md"),
            Path("GEMINI.md"),
        }
        assert_eq("6 agents → 6 target paths", expected, set(outputs))
        for rel, content in outputs.items():
            assert_true(f"banner present in {rel}", rr.BANNER in content)
            assert_true(f"rule title present in {rel}", "Title for a" in content)


def test_agent_not_listed_in_a_rule_does_not_receive_it():
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "claude-only", agents="claude")
        outputs = rr.build_outputs(rr.load_rules())
        assert_eq("only the subscribed agent gets a file",
                  {Path(".claude/rules/coding.md")}, set(outputs))
        assert_true("no cursor output at all",
                    Path(".cursor/rules/coding.mdc") not in outputs)


def test_agent_subscription_is_per_rule_not_per_domain():
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "everyone")
        write_rule(sb.rules, "coding", "claude-secret", agents="claude",
                   title="Claude only rule")
        outputs = rr.build_outputs(rr.load_rules())
        claude = outputs[Path(".claude/rules/coding.md")]
        cursor = outputs[Path(".cursor/rules/coding.mdc")]
        assert_true("claude pack has the claude-only rule",
                    "Claude only rule" in claude)
        assert_true("cursor pack does NOT have the claude-only rule",
                    "Claude only rule" not in cursor)
        assert_true("cursor pack still has the shared rule",
                    "Title for everyone" in cursor)


def test_agent_filter_narrows_the_output_set():
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "a")
        outputs = rr.build_outputs(rr.load_rules(), agent_filter="cursor")
        assert_eq("agent filter → 1 file",
                  {Path(".cursor/rules/coding.mdc")}, set(outputs))


def test_cursor_frontmatter_alwaysapply_tracks_severity():
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "a", severity="medium")
        out = rr.build_outputs(rr.load_rules())[Path(".cursor/rules/coding.mdc")]
        assert_true("medium-only pack → alwaysApply: false",
                    "alwaysApply: false" in out, hint=out[:200])

    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "a", severity="blocker")
        out = rr.build_outputs(rr.load_rules())[Path(".cursor/rules/coding.mdc")]
        assert_true("blocker pack → alwaysApply: true",
                    "alwaysApply: true" in out, hint=out[:200])


# ─── managed-block splicing ──────────────────────────────────────────────────

PROSE = """# AGENTS.md

Hand-written prose the author owns. Do not eat this.

## House style

Tabs, not spaces. Obviously.
"""


def test_managed_block_preserves_surrounding_content_verbatim():
    spliced = rr._managed_block(PROSE, "coding", "PAYLOAD-ONE")
    assert_true("original prose preserved verbatim", PROSE.rstrip() in spliced)
    assert_true("payload spliced in", "PAYLOAD-ONE" in spliced)
    assert_true("BEGIN marker present",
                "<!-- BEGIN render-rules:coding -->" in spliced)
    assert_true("END marker present",
                "<!-- END render-rules:coding -->" in spliced)


def test_managed_block_is_idempotent():
    """Re-splicing must not duplicate the block or grow the file. This is the
    property that makes `render` safe to run in a loop, a hook, or CI."""
    once = rr._managed_block(PROSE, "coding", "PAYLOAD")
    twice = rr._managed_block(once, "coding", "PAYLOAD")
    thrice = rr._managed_block(twice, "coding", "PAYLOAD")
    assert_eq("re-splice is byte-identical", once, twice)
    assert_eq("third splice still identical", once, thrice)
    assert_eq("exactly one BEGIN marker", 1, twice.count("<!-- BEGIN render-rules:coding -->"))
    assert_eq("exactly one END marker", 1, twice.count("<!-- END render-rules:coding -->"))


def test_managed_block_replaces_stale_payload_in_place():
    once = rr._managed_block(PROSE, "coding", "OLD-PAYLOAD")
    updated = rr._managed_block(once, "coding", "NEW-PAYLOAD")
    assert_true("new payload present", "NEW-PAYLOAD" in updated)
    assert_true("old payload gone", "OLD-PAYLOAD" not in updated)
    assert_true("prose still intact", "Tabs, not spaces." in updated)
    assert_eq("still exactly one block", 1,
              updated.count("<!-- BEGIN render-rules:coding -->"))


def test_second_domain_adds_a_second_block_without_destroying_the_first():
    coding = rr._managed_block(PROSE, "coding", "CODING-PAYLOAD")
    both = rr._managed_block(coding, "finance", "FINANCE-PAYLOAD")
    assert_true("coding block survives", "CODING-PAYLOAD" in both)
    assert_true("finance block added", "FINANCE-PAYLOAD" in both)
    assert_true("prose survives both", "Tabs, not spaces." in both)
    assert_eq("one coding BEGIN", 1, both.count("<!-- BEGIN render-rules:coding -->"))
    assert_eq("one finance BEGIN", 1, both.count("<!-- BEGIN render-rules:finance -->"))

    # And re-rendering coding does not disturb finance.
    again = rr._managed_block(both, "coding", "CODING-PAYLOAD")
    assert_eq("re-render of one domain leaves the other alone", both, again)


def test_managed_block_on_empty_host_file():
    out = rr._managed_block("", "coding", "PAYLOAD")
    assert_true("empty host gets a block", "PAYLOAD" in out)
    assert_true("no leading blank cruft", out.startswith("<!-- BEGIN render-rules:coding -->"))


def test_build_outputs_chains_domains_into_one_managed_host_file():
    """codex and gemini both write a single file. Two domains rendered in one
    pass must accumulate into it, not overwrite each other."""
    with Sandbox() as sb:
        (sb.root / "AGENTS.md").write_text(PROSE, encoding="utf-8")
        write_rule(sb.rules, "coding", "a", title="Coding rule A")
        write_rule(sb.rules, "finance", "b", title="Finance rule B")
        outputs = rr.build_outputs(rr.load_rules())
        agents_md = outputs[Path("AGENTS.md")]
        assert_true("coding block in AGENTS.md",
                    "<!-- BEGIN render-rules:coding -->" in agents_md)
        assert_true("finance block in AGENTS.md",
                    "<!-- BEGIN render-rules:finance -->" in agents_md)
        assert_true("coding rule body present", "Coding rule A" in agents_md)
        assert_true("finance rule body present", "Finance rule B" in agents_md)
        assert_true("pre-existing prose preserved", "Tabs, not spaces." in agents_md)


def test_render_then_rerender_is_idempotent_on_disk():
    with Sandbox() as sb:
        (sb.root / "AGENTS.md").write_text(PROSE, encoding="utf-8")
        write_rule(sb.rules, "coding", "a")
        write_rule(sb.rules, "finance", "b")

        assert_eq("first render rc=0", 0, rr.main(["render"]))
        first = {p: p.read_text(encoding="utf-8")
                 for p in sb.root.rglob("*") if p.is_file() and "rules/" not in str(p.relative_to(sb.root))}

        assert_eq("second render rc=0", 0, rr.main(["render"]))
        for path, content in first.items():
            assert_eq(f"idempotent on disk: {path.relative_to(sb.root)}",
                      content, path.read_text(encoding="utf-8"))

        agents_md = (sb.root / "AGENTS.md").read_text(encoding="utf-8")
        assert_eq("no duplicated block after 2 renders", 1,
                  agents_md.count("<!-- BEGIN render-rules:coding -->"))
        assert_true("prose survived 2 renders", "Tabs, not spaces." in agents_md)


# ─── check: the CI gate ──────────────────────────────────────────────────────

def test_check_passes_on_freshly_rendered_tree():
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "a")
        assert_eq("render rc=0", 0, rr.main(["render"]))
        assert_eq("check on fresh tree rc=0", 0, rr.main(["check"]))


def test_check_detects_a_stale_rendered_file():
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "a")
        rr.main(["render"])
        rendered = sb.root / ".claude" / "rules" / "coding.md"
        rendered.write_text("someone hand-edited me\n", encoding="utf-8")
        assert_eq("check detects stale file rc=1", 1, rr.main(["check"]))


def test_check_detects_a_missing_rendered_file():
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "a")
        rr.main(["render"])
        (sb.root / ".cursor" / "rules" / "coding.mdc").unlink()
        assert_eq("check detects missing file rc=1", 1, rr.main(["check"]))


def test_check_detects_drift_after_a_rule_edit():
    """The whole point of the gate: edit the source rule, forget to re-render,
    get a red build instead of six agents quietly disagreeing."""
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "a", title="Original title")
        rr.main(["render"])
        assert_eq("check green before the edit", 0, rr.main(["check"]))
        write_rule(sb.rules, "coding", "a", title="Edited title")
        assert_eq("check red after the edit", 1, rr.main(["check"]))
        rr.main(["render"])
        assert_eq("check green again after re-render", 0, rr.main(["check"]))


def test_malformed_rule_exits_3():
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "a", severity="critical")
        assert_eq("malformed rule → main rc=3", 3, rr.main(["check"]))


def test_no_rules_exits_3():
    with Sandbox() as sb:
        (sb.rules / "coding").mkdir(parents=True, exist_ok=True)
        assert_eq("empty rules/ → main rc=3", 3, rr.main(["list"]))


def test_no_subcommand_exits_2():
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "a")
        assert_eq("no subcommand → main rc=2", 2, rr.main([]))


def test_list_succeeds():
    with Sandbox() as sb:
        write_rule(sb.rules, "coding", "a")
        assert_eq("list rc=0", 0, rr.main(["list"]))


def main():
    print("=== test_render_rules.py ===")
    test_parse_inline_list()
    test_parse_block_list()
    test_parse_empty_value_then_block_list_is_a_list()
    test_parse_empty_value_with_no_continuation_is_empty_scalar()
    test_parse_folded_scalar()
    test_parse_quoted_scalars_and_booleans()
    test_parse_comments_and_blank_lines_ignored()
    test_parse_rejects_missing_and_unterminated_frontmatter()
    test_parse_rejects_genuine_scalar_list_mixing()
    test_load_rules_happy_path()
    test_id_must_equal_domain_slash_filename()
    test_domain_must_match_parent_directory()
    test_bad_severity_raises()
    test_unknown_agent_raises()
    test_missing_required_field_raises()
    test_duplicate_id_raises()
    test_missing_rules_dir_raises()
    test_rules_sort_by_severity()
    test_rules_sort_is_stable_by_id_within_a_severity()
    test_domain_filter()
    test_build_outputs_emits_the_right_path_per_agent()
    test_agent_not_listed_in_a_rule_does_not_receive_it()
    test_agent_subscription_is_per_rule_not_per_domain()
    test_agent_filter_narrows_the_output_set()
    test_cursor_frontmatter_alwaysapply_tracks_severity()
    test_managed_block_preserves_surrounding_content_verbatim()
    test_managed_block_is_idempotent()
    test_managed_block_replaces_stale_payload_in_place()
    test_second_domain_adds_a_second_block_without_destroying_the_first()
    test_managed_block_on_empty_host_file()
    test_build_outputs_chains_domains_into_one_managed_host_file()
    test_render_then_rerender_is_idempotent_on_disk()
    test_check_passes_on_freshly_rendered_tree()
    test_check_detects_a_stale_rendered_file()
    test_check_detects_a_missing_rendered_file()
    test_check_detects_drift_after_a_rule_edit()
    test_malformed_rule_exits_3()
    test_no_rules_exits_3()
    test_no_subcommand_exits_2()
    test_list_succeeds()
    print("\nAll render-rules tests passed.")


if __name__ == "__main__":
    main()
