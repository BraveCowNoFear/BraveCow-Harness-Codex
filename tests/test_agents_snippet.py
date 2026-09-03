from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SNIPPET = ROOT / "templates" / "AGENTS.snippet.md"


class AgentsSnippetTests(unittest.TestCase):
    def test_compact_rules_are_packaged_inside_managed_markers(self) -> None:
        text = SNIPPET.read_text(encoding="utf-8-sig")

        self.assertEqual(text.count("<!-- BraveCow Harness: start -->"), 1)
        self.assertEqual(text.count("<!-- BraveCow Harness: end -->"), 1)
        self.assertLessEqual(len(text), 9000)
        self.assertLessEqual(len(text.splitlines()), 220)
        self.assertIn("## Finish the real job", text)
        self.assertIn("## Respect the authorization boundary", text)
        self.assertIn("## Writing principles", text)
        self.assertIn("## Bilibili scripts and titles", text)
        self.assertIn("## DOM and Unicode debugging", text)
        self.assertIn("Conclusion -> reason -> example -> limitation", text)
        self.assertIn("先给结论，再解释原因", text)
        self.assertIn("术语第一次出现，必须马上翻译", text)
        self.assertIn("标题只能有一个主要钩子", text)
        self.assertIn("Do not interrupt or repeatedly prompt a working subagent", text)


if __name__ == "__main__":
    unittest.main()
