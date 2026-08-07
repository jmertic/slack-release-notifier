#!/usr/bin/env python3
#
# Copyright this project and it's contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import os
import tempfile
import unittest
from unittest.mock import patch

# 1. Safely mock os.environ before importing the module to prevent KeyError on load
with patch.dict(os.environ, {"GITHUB_OUTPUT": "/dev/null"}):
    # Adjust import path if this file is located elsewhere (e.g., `import io_helper`)
    import actions.io as io_module


class TestWriteToOutput(unittest.TestCase):

    def setUp(self):
        # Create a real temporary file to act as the buffer
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()

    def tearDown(self):
        # Clean up temporary file after each test run
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_write_to_output_success(self):
        """Test writing multiple key-value pairs to output buffer."""
        context = {
            "name": "John",
            "release": "v1.0.0"
        }

        # Override BUFFER_PATH to point to our isolated temporary file
        with patch.object(io_module, "BUFFER_PATH", self.temp_file.name):
            io_module.write_to_output(context)

        # Pass newline="" to disable universal newline translation when reading
        with open(self.temp_file.name, "r", newline="") as f:
            content = f.read()

        expected_content = "name=John\r\nrelease=v1.0.0\r\n"
        self.assertEqual(content, expected_content)

    def test_write_to_output_empty_dict(self):
        """Test write_to_output with an empty dictionary context."""
        context = {}

        with patch.object(io_module, "BUFFER_PATH", self.temp_file.name):
            io_module.write_to_output(context)

        with open(self.temp_file.name, "r") as f:
            content = f.read()

        self.assertEqual(content, "")


if __name__ == "__main__":
    unittest.main()
