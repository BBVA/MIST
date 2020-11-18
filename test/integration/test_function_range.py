import os

from mist.action_run import execute_from_text

EXAMPLE_FILE = "function_range.mist"

def test_range(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()

    console = execute_from_text(content)
    assert "[0, 1, 2]" in console
