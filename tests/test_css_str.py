from htpy import div


def test_id() -> None:
    assert str(div("#a")) == '<div id="a"></div>'


def test_class() -> None:
    assert str(div(".a")) == '<div class="a"></div>'


def test_id_class() -> None:
    assert str(div("#a.a")) == '<div id="a" class="a"></div>'


def test_id_spaces() -> None:
    assert str(div("#a ")) == '<div id="a"></div>'


def test_class_spaces() -> None:
    assert str(div(".a ")) == '<div class="a"></div>'


def test_id_class_spaces() -> None:
    assert str(div("#a .a ")) == '<div id="a" class="a"></div>'
