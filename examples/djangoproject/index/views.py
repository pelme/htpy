from django.shortcuts import render

from htpy import h1


def index(request):
    return render(request, "base.html", {"content": h1["Welcome to my site!"]})
