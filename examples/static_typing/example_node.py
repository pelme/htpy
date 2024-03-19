from htpy import Element, Node, div


def bootstrap_alert(contents: Node) -> Element:
    return div(".alert", role="alert")[contents]


print(bootstrap_alert("hest"))
