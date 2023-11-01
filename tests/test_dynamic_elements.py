import htpy


def test_instance_cache() -> None:
    """
    htpy creates element object dynamically. make sure they are reused.
    """
    assert htpy.div is htpy.div
