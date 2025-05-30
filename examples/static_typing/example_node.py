from htpy import Node, Renderable, div


def bootstrap_alert(contents: Node) -> Renderable:
    return div(".alert", role="alert")[contents]


print(bootstrap_alert("hest"))
