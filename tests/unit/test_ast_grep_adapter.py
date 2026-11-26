from first_ade.adapters.ast_grep_adapter import SubprocessAstGrepAdapter


def test_ast_grep_adapter():
    assert SubprocessAstGrepAdapter() is not None
