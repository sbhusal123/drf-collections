from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


from django.urls import reverse
from ..models import Ingredient, Recipe
from ..serializers import RecipeSerializer

CREATE_RECIPE_URL = "new_recipe"
EDIT_RECIPE_URL = "RUD_recipe"


def create_ingredient_object(name, payload_only):
    ingredient_info = {
        "name": name
    }

    if payload_only:
        return ingredient_info
    else:
        ingredient_obj = Ingredient.objects.create(**ingredient_info)
        return ingredient_obj, ingredient_info


class RecipeApiTest(TestCase):
    """Test case for Recipe Api endpoints"""

    def setUp(self):
        self.client = APIClient()

    def test_create_recipe_with_existing_name(self):
        """Test creating recipe with existing name failed"""
        payload = {
            'name': 'Mutton Curry'
        }
        Recipe.objects.create(**payload)
        

        res = self.client.post(
            reverse(CREATE_RECIPE_URL),
            payload,
            format="json"
        )
        recipe_obj_count = Recipe.objects.filter(**payload).count()

        self.assertEqual(recipe_obj_count, 1)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_existing_ingredient_to_recipe(self):
        """Test adding existing ingredient to recipe"""
        recipe = Recipe.objects.create(name="Lassi")
        _, ing1_info = create_ingredient_object(name="Curd", payload_only=False)
        _, ing2_info = create_ingredient_object(name="Banana", payload_only=False)

        payload = {
            "name": recipe.name,
            "ingredients":[
                ing1_info,
                ing2_info
            ]
        }

        res = self.client.patch(
            reverse(EDIT_RECIPE_URL, kwargs={'id': recipe.id}),
            payload,
            format="json"
        )

        recipe = Recipe.objects.get(name=payload["name"])
        serializer = RecipeSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_add_new_ingredient_to_recipe(self):
        """Test adding new ingredient to recipe successful"""
        recipe = Recipe.objects.create(name="Pickle")
        ing1_info = create_ingredient_object(name="Tomato", payload_only=True)
        ing2_info = create_ingredient_object(name="Turmeric", payload_only=True)

        payload = {
            "name": recipe.name,
            "ingredients": [
                ing1_info,
                ing2_info
            ]
        }

        res = self.client.patch(
            reverse(EDIT_RECIPE_URL, kwargs={'id': recipe.id}),
            payload,
            format="json"
        )

        recipe = Recipe.objects.get(name=payload["name"])
        serializer = RecipeSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_remove_existing_ingredient_from_recipe(self):
        """"Test removing existing ingredient from recipe successful"""
        recipe = Recipe.objects.create(name="Grilled Mutton")
        ing1_obj, ing1_info = create_ingredient_object(name="Mutton", payload_only=False)
        ing1_info["action"] = "remove"

        payload = {
            "name": recipe.name,
            "ingredients": [ing1_info]
        }

        res = self.client.patch(
            reverse(EDIT_RECIPE_URL, kwargs={'id': recipe.id}),
            payload,
            format="json"
        )

        recipe_ingredient = recipe.ingredients.all()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(ing1_obj, recipe_ingredient)

    def test_remove_non_existing_ingredient_from_recipe(self):
        """"Test removing non existing ingredient from recipe failed"""
        recipe = Recipe.objects.create(name="Grilled Fish")
        ing1_info = create_ingredient_object(name="Fish", payload_only=True)
        ing1_info["action"] = "remove"

        payload = {
            "name": recipe.name,
            "ingredients": [ing1_info]
        }

        res = self.client.patch(
            reverse(EDIT_RECIPE_URL, kwargs={'id': recipe.id}),
            payload,
            format="json"
        )

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
