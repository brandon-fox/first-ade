from first_ade.domain.guards import evaluate_tamper_guard
from first_ade.domain.models import AxiomsConfig, FileChange, Mode, TamperGuardConfig

def test_guards_tamper():
    cfg = AxiomsConfig("0.1", "p", tamper_guard=TamperGuardConfig(protected_paths=(".first-ade/axioms.yaml",)))
    assert len(evaluate_tamper_guard([FileChange("M", ".first-ade/axioms.yaml")], cfg, Mode.AGENT)) == 1
