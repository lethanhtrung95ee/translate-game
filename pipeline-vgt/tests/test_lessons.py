import sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import check_lessons  # noqa: E402


class TestLessons(unittest.TestCase):
    def test_repo_lessons_valid(self):
        _, errs = check_lessons.run(ROOT)
        self.assertEqual(errs, [])

    def test_missing_field_detected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "docs" / "lessons"
            p.mkdir(parents=True)
            (p / "global.md").write_text("### G-999: thu\n- Phạm vi: global\n", encoding="utf-8")
            _, errs = check_lessons.run(Path(d))
            self.assertTrue(any("Dấu hiệu kiểm tra" in e for e in errs))


if __name__ == "__main__":
    unittest.main()
