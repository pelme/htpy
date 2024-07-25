from django.db import models


class Pizza(models.Model):
    name = models.CharField(max_length=100)
