import pytest

import htpy
from htpy import Element


def test_instance_cache() -> None:
    """
    htpy creates element object dynamically. make sure they are reused.
    """
    assert htpy.div is htpy.div


def test_invalid_element_name() -> None:
    with pytest.raises(ValueError, match="html elements must have all lowercase names"):
        Element("Foo", {}, [])
