"""The shared byte envelopes stay importable where annotation syntax matters.

``claude_obsidian.limits`` is imported by the mutation engine, and therefore by
the CLI and the hooks, on whatever interpreter the user has. Its
``ledger_capacity_message`` annotates a parameter as ``int | str``; that syntax
is evaluated at function-definition time before Python 3.10 unless the module
postpones annotations, which made the whole package fail to import on 3.9.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from claude_obsidian.limits import ledger_capacity_message


class LimitsAnnotationTests(unittest.TestCase):
    def test_annotations_are_postponed(self):
        self.assertEqual(
            ledger_capacity_message.__annotations__,
            {'relative': 'str', 'size': 'int | str', 'return': 'str'},
        )

    def test_message_keeps_the_capacity_bound(self):
        message = ledger_capacity_message('wiki/meta/ledgers/source-ledger.json', 12)
        self.assertIn('12 bytes', message)
        self.assertIn('16777216 bytes', message)


if __name__ == '__main__':
    unittest.main()
