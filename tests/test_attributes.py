from htpy import div


def test_class_str():
    result = div(class_=">foo bar")
    assert str(result) == '<div class="&gt;foo bar"></div>'


def test_class_list():
    result = div(class_=[">foo", False, None, "", "bar"])
    assert str(result) == '<div class="&gt;foo bar"></div>'


def test_class_dict():
    result = div(class_={">foo": True, "x": False, "y": None, "z": "", "bar": True})
    assert str(result) == '<div class="&gt;foo bar"></div>'
