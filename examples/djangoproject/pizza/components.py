from htpy import li, ul


def pizza_list(context, request):
    return ul[(li[pizza.name] for pizza in context["object_list"])]
