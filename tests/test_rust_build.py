from htpy._rust_impl import sum_as_string


def test_sum_as_string() -> None:
    assert sum_as_string(21, 21) == "42"
