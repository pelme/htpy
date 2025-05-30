from htpy import Renderable, h1


class User:
    def __init__(self, name: str):
        self.name = name


def greeting(user: User) -> Renderable:
    return h1[f"Hi {user.first_name.capitalize()}!"]
