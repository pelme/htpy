from django.http import HttpRequest, HttpResponse

from .components import my_form_page, my_form_success_page
from .forms import MyForm


def my_form(request: HttpRequest) -> HttpResponse:
    form = MyForm(request.POST or None)
    if form.is_valid():
        return HttpResponse(my_form_success_page())

    return HttpResponse(my_form_page(request, my_form=form))
