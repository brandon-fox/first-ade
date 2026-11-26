from first_ade.domain.models import CheckResult
from first_ade.domain.receipt import render_run_receipt

def test_receipt_pass():
    assert "PASS" in render_run_receipt(CheckResult())
