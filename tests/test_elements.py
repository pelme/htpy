from htpy import input


def test_void_element():
    result = str(input(name="foo"))
    assert str(result) == '<input name="foo">'
