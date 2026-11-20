import unittest

from vgt.bible import BibleIndex


class FixedContextTest(unittest.TestCase):
    """style + premise nam trong system prompt (duoc cache), khong lap lai trong moi lo."""

    def test_split(self):
        b = {"style": {"tone": "u toi"}, "work": {"premise": "P", "synopsis": "dai"},
             "characters": [{"id": "a", "names": ["Ana"]}]}
        bidx = BibleIndex(b)
        self.assertEqual(bidx.fixed_context(), {"style": {"tone": "u toi"}, "work": {"premise": "P"}})
        ctx = bidx.context_for([type("E", (), {"source": "Ana: hi", "speaker": None, "face": None,
                                               "grp": "g"})()])
        self.assertNotIn("style", ctx)
        self.assertNotIn("work", ctx)
        self.assertEqual([c["id"] for c in ctx["characters"]], ["a"])

    def test_empty(self):
        self.assertEqual(BibleIndex({}).fixed_context(), {})


if __name__ == "__main__":
    unittest.main()
