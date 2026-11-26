from first_ade.domain.models import Mode, Violation


def test_models_mode():
    assert Mode.AGENT.value == "agent"
    assert Violation("A", "f", 1, "r", "h").format_terminal().startswith("[A]")
