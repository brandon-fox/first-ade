from pathlib import Path

from first_ade.cli.hook import process_hook_stdin


def test_hook_empty():
    assert process_hook_stdin("", Path("."))[0] == 2
