from first_ade.domain.sarif import build_sarif_report


def test_sarif_empty():
    assert build_sarif_report([])["version"] == "2.1.0"
