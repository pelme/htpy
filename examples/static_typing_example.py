from htpy import Element, h1


class User:
    def __init__(self, name: str):
        self.name = name


def greeting(user: User) -> Element:
    return h1[f"Hi {user.first_name.capitalize()}!"]
