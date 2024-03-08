from django.http import HttpResponse

from . import components
from .forms import MyForm


def my_form(request):
    form = MyForm(request.POST or None)
    if form.is_valid():
        return HttpResponse(components.my_form_success())

    return HttpResponse(components.my_form(request, form))
