from django.db import models
from django.urls import reverse


class Ingredient(models.Model):
    """"Ingredient for recipe"""
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("RUD_ingredient", kwargs={"id": self.id})
    

class Recipe(models.Model):
    """Recipe objects"""
    name = models.CharField(max_length=20, unique=True)
    ingredients = models.ManyToManyField(Ingredient)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("RUD_recipe", kwargs={"id": self.id})