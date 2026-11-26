from first_ade.domain.paths import normalize_repo_path


def test_paths_norm():
    assert normalize_repo_path("a\\b") == "a/b"
