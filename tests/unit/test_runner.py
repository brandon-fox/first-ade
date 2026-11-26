from first_ade.cli.runner import run_checks


def test_runner_callable():
    assert callable(run_checks)
