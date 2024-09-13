from joulegl.utility.definitions import vec4wise


def test_vec4wise() -> None:
    it = [1, 2, 3, 4, 5, 6, 7, 8]
    vec4 = vec4wise(it)
    assert list(vec4) == [(1, 2, 3, 4), (5, 6, 7, 8)]
