from django.views.generic import ListView

from pizza.models import Pizza


class PizzaListView(ListView):
    model = Pizza
    template_name = "pizza.components.pizza_list"
