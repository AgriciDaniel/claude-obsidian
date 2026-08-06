#!/usr/bin/env python3
"""Hermetic tests for pure-Python ``.gitignore`` evaluation."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from claude_obsidian.gitignore import GitignoreMatcher


class GitignoreMatcherTests(unittest.TestCase):
    def _matcher(self, files: dict[str, str]) -> GitignoreMatcher:
        self._directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._directory.cleanup)
        root = Path(self._directory.name)
        for relative, content in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return GitignoreMatcher(root)

    def test_no_gitignore_means_nothing_is_ignored(self) -> None:
        matcher = self._matcher({"wiki/page.md": "x"})
        self.assertFalse(matcher.is_ignored("wiki/page.md"))

    def test_unanchored_pattern_matches_any_depth(self) -> None:
        matcher = self._matcher({".gitignore": "build\n"})
        self.assertTrue(matcher.is_ignored("build"))
        self.assertTrue(matcher.is_ignored("deep/nested/build"))
        self.assertFalse(matcher.is_ignored("buildinfo"))

    def test_anchored_pattern_matches_only_at_scope_root(self) -> None:
        matcher = self._matcher({".gitignore": "/build\n"})
        self.assertTrue(matcher.is_ignored("build"))
        self.assertFalse(matcher.is_ignored("deep/build"))

    def test_dir_only_pattern_excludes_contents_but_not_same_named_file(self) -> None:
        matcher = self._matcher({".gitignore": "bin/\n", "bin/tool": "x"})
        self.assertTrue(matcher.is_ignored("bin/tool"))
        self.assertTrue(matcher.is_ignored("sub/bin/tool"))
        self.assertFalse(matcher.is_ignored("docs/bin"))

    def test_negation_reincludes_a_file(self) -> None:
        matcher = self._matcher({".gitignore": "*.log\n!keep.log\n"})
        self.assertTrue(matcher.is_ignored("debug.log"))
        self.assertFalse(matcher.is_ignored("keep.log"))

    def test_contents_of_excluded_directory_stay_excluded(self) -> None:
        matcher = self._matcher(
            {".gitignore": "out/\n", "out/.gitignore": "!wanted.txt\n"}
        )
        self.assertTrue(matcher.is_ignored("out/wanted.txt"))

    def test_nested_gitignore_is_scoped_to_its_directory(self) -> None:
        matcher = self._matcher({"sub/.gitignore": "local.txt\n"})
        self.assertTrue(matcher.is_ignored("sub/local.txt"))
        self.assertFalse(matcher.is_ignored("local.txt"))

    def test_deeper_gitignore_overrides_shallower(self) -> None:
        matcher = self._matcher(
            {".gitignore": "*.tmp\n", "sub/.gitignore": "!special.tmp\n"}
        )
        self.assertTrue(matcher.is_ignored("sub/other.tmp"))
        self.assertFalse(matcher.is_ignored("sub/special.tmp"))

    def test_double_star_patterns(self) -> None:
        matcher = self._matcher({".gitignore": "docs/**\n**/node.bin\na/**/b\n"})
        self.assertTrue(matcher.is_ignored("docs/x/y.md"))
        self.assertFalse(matcher.is_ignored("docs"))
        self.assertTrue(matcher.is_ignored("deep/tree/node.bin"))
        self.assertTrue(matcher.is_ignored("a/b"))
        self.assertTrue(matcher.is_ignored("a/x/y/b"))
        self.assertFalse(matcher.is_ignored("a/x/c"))

    def test_character_classes_and_question_mark(self) -> None:
        matcher = self._matcher({".gitignore": "*.py[cod]\nfile?.txt\n"})
        self.assertTrue(matcher.is_ignored("mod.pyc"))
        self.assertFalse(matcher.is_ignored("mod.py"))
        self.assertTrue(matcher.is_ignored("file1.txt"))
        self.assertFalse(matcher.is_ignored("file10.txt"))

    def test_comments_blanks_and_escapes(self) -> None:
        matcher = self._matcher({".gitignore": "# note\n\n\\#literal\n"})
        self.assertTrue(matcher.is_ignored("#literal"))
        self.assertFalse(matcher.is_ignored("# note"))

    def test_symlinked_gitignore_is_not_read(self) -> None:
        matcher = self._matcher({"real-ignore.txt": "secret\n"})
        root = Path(self._directory.name)
        try:
            os.symlink(root / "real-ignore.txt", root / ".gitignore")
        except (OSError, NotImplementedError):
            self.skipTest("platform does not support symlinks")
        self.assertFalse(matcher.is_ignored("secret"))


if __name__ == "__main__":
    unittest.main()
