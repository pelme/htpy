from dataclasses import dataclass
from htpy import p, ul, li, span, div
from htpy.utils import if_, for_


def test_if_something() -> None:
    result = if_(True)[p["Something"]]
    assert str(result) == "<p>Something</p>"


def test_not_something() -> None:
    result = if_(False)[p["Something"]]
    assert str(result) == ""


def test_multiple_somethings() -> None:
    result = if_(True)[
        p["Something"],
        p["Something"],
        p["Something"],
    ]
    assert str(result) == "<p>Something</p><p>Something</p><p>Something</p>"


def test_map_string() -> None:
    result = ul[
        for_(
            "abc",
            lambda l: li[l],
        )
    ]

    assert str(result) == "<ul><li>a</li><li>b</li><li>c</li></ul>"

 
def test_map_animals() -> None:
    result = div[for_(["Cat", "Doge", "Horse"], lambda animal: p[animal])]

    assert str(result) == "<div><p>Cat</p><p>Doge</p><p>Horse</p></div>"


def test_map_multiple() -> None:
    actual = for_(["Cat", "Doge", "Horse"], lambda animal: [p[animal], p[animal]])
    expected = "<p>Cat</p><p>Cat</p><p>Doge</p><p>Doge</p><p>Horse</p><p>Horse</p>"

    assert str(actual) == expected


def test_map_dataclasses() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    persons = [Person("Morgan", 51), Person("Ola Conny", 60)]

    actual = ul[
        for_(
            persons,
            lambda pax: li[
                span[pax.name],
                span[str(pax.age)],
            ],
        )
    ]
    expected = "<ul><li><span>Morgan</span><span>51</span></li><li><span>Ola Conny</span><span>60</span></li></ul>"

    assert str(actual) == expected
