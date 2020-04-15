from django.urls import path
from . import views

urlpatterns = [
    path('ingredient/', views.CreateIngredientView.as_view(), name="new_ingredient"),
    path('ingredient/<int:id>/',views.IngredientDetailView.as_view(),name="RUD_ingredient"),
    
    path('recipe/', views.CreateRecipeView.as_view(), name="new_recipe"),
    path('recipe/<int:id>/', views.RecipeDetailView.as_view(), name="RUD_recipe")
]
