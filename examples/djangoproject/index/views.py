from django.shortcuts import render

from .components import index_content


def index(request):
    return render(request, "base.html", {"content": index_content()})
