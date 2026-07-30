import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIRMWARE_INCLUDE = ROOT / "firmware" / "sticks3" / "include"


class FirmwareInputPolicyTests(unittest.TestCase):
    def test_sleeping_display_consumes_first_input_for_wake_only(self) -> None:
        source = """
#include <assert.h>
#include "vibe_input.h"

int main(void) {
    assert(vibe_input_should_wake_only(false));
    assert(!vibe_input_should_wake_only(true));
    return 0;
}
"""
        with tempfile.TemporaryDirectory() as tmp:
            executable = Path(tmp) / "input_policy_test"
            result = subprocess.run(
                [
                    "cc",
                    "-std=c11",
                    "-Werror",
                    f"-I{FIRMWARE_INCLUDE}",
                    "-x",
                    "c",
                    "-o",
                    str(executable),
                    "-",
                ],
                input=source,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            run_result = subprocess.run([str(executable)], check=False)
            self.assertEqual(run_result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
