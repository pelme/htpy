import htpy as h
from htpy._compiler import CompiledElement


@h.compile
def trivial() -> h.VoidElement:
    return h.img(src="lol.bmp")


def test_trivial() -> None:
    result = trivial()

    assert isinstance(result, CompiledElement)
    assert result.parts == ['<img src="lol.bmp">']

    assert str(result) == '<img src="lol.bmp">'
