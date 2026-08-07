import unittest

from main import format_release_notes


class FormatReleaseNotesTests(unittest.TestCase):
    def test_converts_openexr_release_note_to_slack_mrkdwn(self):
        release_notes = (
            "* **PyOpenEXR RGB-channel-coalescing bugs**\n"
            "  * [CVE-2026-68514]"
            "(https://www.cve.org/CVERecord?id=CVE-2026-68514) "
            "PyOpenEXR heap buffer overflow"
        )

        self.assertEqual(
            format_release_notes(release_notes),
            (
                "•   *PyOpenEXR RGB-channel-coalescing bugs*\n"
                "    ◦   "
                "<https://www.cve.org/CVERecord?id=CVE-2026-68514|"
                "CVE-2026-68514> PyOpenEXR heap buffer overflow"
            )
        )

    def test_converts_headings_emphasis_and_ordered_lists(self):
        self.assertEqual(
            format_release_notes(
                "# Changes\n\n"
                "1. **Bold**\n"
                "2. *Italic* and ~~removed~~"
            ),
            (
                "*Changes*\n\n"
                "1.  *Bold*\n"
                "2.  _Italic_ and ~removed~"
            )
        )

    def test_preserves_code_and_converts_blockquotes(self):
        release_notes = (
            "> **Important**\n\n"
            "`inline` and:\n\n"
            "```python\n"
            "print(\"**not bold**\")\n"
            "```"
        )

        self.assertEqual(
            format_release_notes(release_notes),
            (
                "> *Important*\n\n"
                "`inline` and:\n\n"
                "```\n"
                "print(\"**not bold**\")\n"
                "```"
            )
        )

    def test_enforces_slack_section_text_limit_after_conversion(self):
        release_notes = "[link](https://example.com) " + ("x" * 3000)

        formatted_notes = format_release_notes(release_notes)

        self.assertEqual(len(formatted_notes), 3000)
        self.assertTrue(formatted_notes.startswith("<https://example.com|link>"))


if __name__ == "__main__":
    unittest.main()
