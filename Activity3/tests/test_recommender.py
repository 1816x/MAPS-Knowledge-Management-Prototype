import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from recommender import Recommender, clean_text  # noqa: E402


class RecommenderBehavior(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = Recommender(ROOT / "corpus.csv")

    def test_corpus_contract(self):
        with (ROOT / "corpus.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 38)
        self.assertEqual(len({r["id"] for r in rows}), 38)
        self.assertEqual(sum(r["category"] == "Policy/Process" for r in rows), 6)

    def test_seed_excluded_scores_sorted(self):
        results = self.engine.by_id("PP-01")
        self.assertEqual(len(results), 5)
        self.assertNotIn("PP-01", [r.document.id for r in results])
        self.assertEqual([r.score for r in results], sorted(
            (r.score for r in results), reverse=True))

    def test_support_seed(self):
        results = self.engine.by_id("IR-01")
        self.assertEqual(len(results), 5)
        self.assertTrue(all(r.score > 0 for r in results))

    def test_query_and_unknowns(self):
        self.assertEqual(len(self.engine.by_query(
            "How to reproduce command display reconnect freeze?")), 5)
        with self.assertRaisesRegex(ValueError, "Unknown document"):
            self.engine.by_id("MISSING")
        with self.assertRaisesRegex(ValueError, "empty"):
            self.engine.by_query("?!")
        self.assertEqual(clean_text("Log-in, ERROR!"), "log in error")


if __name__ == "__main__":
    unittest.main()
