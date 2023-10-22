from htpy import input, li, ul


def test_void_element():
    result = str(input(name="foo"))
    assert str(result) == '<input name="foo">'


def test_list_children():
    result = ul([li("a"), li("b")])
    assert str(result) == "<ul><li>a</li><li>b</li></ul>"


def test_generator_children():
    result = ul(li(x) for x in ["a", "b"])
    assert str(result) == "<ul><li>a</li><li>b</li></ul>"
    assert str(result) == "<ul><li>a</li><li>b</li></ul>"
