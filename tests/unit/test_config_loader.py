from pathlib import Path

from first_ade.adapters.config_loader import load_axioms_config


def test_load_axioms():
    assert load_axioms_config(Path(".")).project == "first-ade"
