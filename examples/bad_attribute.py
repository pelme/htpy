from htpy import div


def good_component_a():
    return div[good_component_b()]


def good_component_b():
    return div[good_component_c()]


def good_component_c():
    return div[bad_component()]


def bad_component():
    return div(a=object())


print(str(good_component_a()))
