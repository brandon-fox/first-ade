from first_ade.adapters.git_adapter import parse_name_status_lines


def test_git_parse():
    assert parse_name_status_lines("M\ta.py")[0].path == "a.py"
