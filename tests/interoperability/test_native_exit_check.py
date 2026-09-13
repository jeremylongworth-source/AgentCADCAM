from __future__ import annotations

import subprocess
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from tests.native.check_cadquery_runtime import main


class NativeExitCheckTests(unittest.TestCase):
    def test_printed_success_cannot_hide_native_crash(self):
        result = subprocess.CompletedProcess([], 0xC0000005, stdout='{"checks_finished": true}\n', stderr="")
        output = StringIO()
        with patch("tests.native.check_cadquery_runtime.subprocess.run", return_value=result), redirect_stdout(output):
            self.assertEqual(main(), 1)
        self.assertIn("CADQUERY NATIVE CHECK FAILED", output.getvalue())
        self.assertNotIn("CADQUERY NATIVE CHECK PASSED", output.getvalue())

    def test_hung_native_probe_is_a_failure(self):
        with patch("tests.native.check_cadquery_runtime.subprocess.run", side_effect=subprocess.TimeoutExpired("probe", 60)), redirect_stdout(StringIO()):
            self.assertEqual(main(), 1)
