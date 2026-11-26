from first_ade.ports.analyzer_port import AstAnalyzerPort, BoundaryAnalyzerPort, CuePort

def test_analyzer_ports():
    assert CuePort is not None and BoundaryAnalyzerPort is not None and AstAnalyzerPort is not None
