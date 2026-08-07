#!/usr/bin/env python3
#
# Copyright this project and it's contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import os
import unittest
from unittest.mock import MagicMock, patch
from slack_sdk.errors import SlackApiError

from main import SLACK_SECTION_TEXT_LIMIT, format_release_notes, main

class TestSlackReleaseNotifier(unittest.TestCase):

    def test_format_release_notes_within_limit(self):
        """Test formatting markdown within character limit."""
        raw_notes = "## Release Notes\n\n- Feature 1\n- Feature 2\n\n"
        formatted = format_release_notes(raw_notes)

        # Check trailing whitespace stripped
        self.assertFalse(formatted.endswith("\n"))
        self.assertLessEqual(len(formatted), SLACK_SECTION_TEXT_LIMIT)

    def test_format_release_notes_exceeding_limit(self):
        """Test truncation when release notes exceed limit."""
        long_notes = "a" * (SLACK_SECTION_TEXT_LIMIT + 500)
        formatted = format_release_notes(long_notes)

        self.assertEqual(len(formatted), SLACK_SECTION_TEXT_LIMIT)

    @patch.dict(
        os.environ,
        {
            "INPUT_PROJECT_NAME": "MyProject",
            "INPUT_SLACK_BOT_TOKEN": "xoxb-test-token",
            "INPUT_PROJECT_LOGO": "https://example.com/logo.png",
            "INPUT_RELEASE_VERSION": "v1.0.0",
            "INPUT_RELEASE_URL": "https://github.com/example/repo/releases/tag/v1.0.0",
            "INPUT_RELEASE_NOTES": "Release notes content",
            "INPUT_SLACK_CHANNEL": "releases",  # No '#' to test auto-prefixing
        },
    )
    @patch("main.WebClient")
    def test_main_success_channel_without_hash(self, mock_web_client_class):
        """Test main execution success path when channel lacks '#' prefix."""
        mock_client = MagicMock()
        mock_web_client_class.return_value = mock_client
        mock_client.chat_postMessage.return_value = {
            "message": {"text": "MyProject v1.0.0"}
        }

        main()

        mock_web_client_class.assert_called_once_with(token="xoxb-test-token")
        mock_client.chat_postMessage.assert_called_once()

    @patch("builtins.print")
    @patch.dict(
        os.environ,
        {
            "INPUT_PROJECT_NAME": "MyProject",
            "INPUT_SLACK_BOT_TOKEN": "xoxb-test-token",
            "INPUT_PROJECT_LOGO": "https://example.com/logo.png",
            "INPUT_RELEASE_VERSION": "v1.0.0",
            "INPUT_RELEASE_URL": "https://github.com/example/repo/releases/tag/v1.0.0",
            "INPUT_RELEASE_NOTES": "Release notes content",
            "INPUT_SLACK_CHANNEL": "#releases",  # With '#' prefix
        },
    )
    @patch("main.WebClient")
    def test_main_slack_api_error(self, mock_web_client_class, mock_print):
        """Test SlackApiError exception handling branch in main."""
        mock_client = MagicMock()
        mock_web_client_class.return_value = mock_client

        # Mock SlackApiError response structure
        mock_response = {
            "ok": False,
            "error": "invalid_auth",
        }
        mock_slack_response = MagicMock()
        mock_slack_response.__getitem__.side_effect = mock_response.__getitem__
        mock_slack_response.status_code = 401

        error = SlackApiError("Auth Error", response=mock_slack_response)
        mock_client.chat_postMessage.side_effect = error

        main([])

        mock_client.chat_postMessage.assert_called_once()

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
