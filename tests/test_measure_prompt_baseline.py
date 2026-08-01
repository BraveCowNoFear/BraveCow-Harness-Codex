from __future__ import annotations

import unittest

from harness.scripts.measure_prompt_baseline import bucket_for_text, measure_messages


class MeasurePromptBaselineTests(unittest.TestCase):
    def test_buckets_and_skill_descriptions(self) -> None:
        messages = [
            {
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "<skills_instructions>\n## Skills\n"
                            "- demo: Short useful description. (file: demo/SKILL.md)\n"
                            "- plugin:demo: Namespaced description. (file: plugin/demo/SKILL.md)"
                        ),
                    },
                    {"type": "input_text", "text": "MEMORY_SUMMARY\nsmall memory"},
                ]
            }
        ]
        result = measure_messages(messages)
        self.assertGreater(result["buckets"]["skills"], 0)
        self.assertGreater(result["buckets"]["memory"], 0)
        self.assertEqual(result["skill_catalog"]["entries"], 2)
        self.assertGreater(result["skill_catalog"]["description_tokens"], 0)

    def test_plugin_bucket(self) -> None:
        self.assertEqual(bucket_for_text("<plugins_instructions>"), "plugins")


if __name__ == "__main__":
    unittest.main()
