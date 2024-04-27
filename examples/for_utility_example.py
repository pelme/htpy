from htpy import ul, li, span
from htpy.utils import for_
from dataclasses import dataclass


@dataclass
class Person:
    name: str
    age: int


persons = [Person("Morgan", 51), Person("Ola Conny", 60)]

print(
    ul[
        for_(
            persons,
            lambda pax: li[
                span[pax.name],
                span[str(pax.age)],
            ],
        )
    ]
)

#  Prettified output:
#  <ul>
#    <li>
#      <span>Morgan</span>
#      <span>51</span>
#    </li>
#    <li>
#      <span>Ola Conny</span>
#      <span>60</span>
#    </li>
#  </ul>
