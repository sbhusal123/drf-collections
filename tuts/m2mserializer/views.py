from rest_framework import generics
from .models import Ingredient, Recipe
from . import serializers

class CreateRecipeView(generics.ListCreateAPIView):
    serializer_class=serializers.CreateRecipeSerializer
    queryset=Recipe.objects.all()


class RecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class=serializers.RecipeSerializer
    queryset=Recipe.objects.all()

    lookup_field="id"





class CreateIngredientView(generics.ListAPIView, generics.CreateAPIView):
    queryset=Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class IngredientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

    lookup_field="id"
