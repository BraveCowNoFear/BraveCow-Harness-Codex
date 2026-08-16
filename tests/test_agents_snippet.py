from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SNIPPET = ROOT / "templates" / "AGENTS.snippet.md"


class AgentsSnippetTests(unittest.TestCase):
    def test_plain_spoken_rules_are_packaged_inside_managed_markers(self) -> None:
        text = SNIPPET.read_text(encoding="utf-8-sig")

        self.assertEqual(text.count("<!-- BraveCow Harness: start -->"), 1)
        self.assertEqual(text.count("<!-- BraveCow Harness: end -->"), 1)
        self.assertIn("Plain-Spoken & Perspective Rules (Highest Priority)", text)
        self.assertIn("Always speak to the end user", text)
        self.assertIn("先给结论，再解释原因", text)
        self.assertIn("术语第一次出现，必须马上翻译", text)
        self.assertIn("删除至少 20% 的文字", text)
        self.assertIn("标题只能有一个主要钩子", text)


if __name__ == "__main__":
    unittest.main()
