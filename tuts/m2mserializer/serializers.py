from rest_framework import serializers
from .models import Recipe, Ingredient
from django.shortcuts import get_object_or_404


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient objects"""
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model=Ingredient
        fields='__all__'
        read_only_fields=('id', 'url')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """"Serializer for creating Recipe Object"""
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model=Recipe
        fields=('id','name','url','ingredients')
        read_only_fields=('id', 'url')

    def create(self, validated_data):
        recipe = Recipe.objects.create(**validated_data)
        return recipe


class NestedIngredientSerializer(serializers.ModelSerializer):
    """Serializer for performing action with multiple
        Ingredient objects in Recipe objects.
    """
    # Removes ingredient or delete from recipe's object based on field check of action
    # More at update
    ACTION_CHOICE = (
        ('remove', 'remove'),
        ('delete', 'delete')
    )
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    action = serializers.ChoiceField(
        choices=ACTION_CHOICE,
        required=False
    )

    class Meta:
        model=Ingredient
        fields=('id', 'name', 'url', 'action')
        extra_kwargs = {
            'name': {'validators': []},  # escape validation for unique name
            'action': {'validators': []}
        }
        read_only_fields = ('id', 'url')
    
        # If using custom validation define this, else dont
        # def validate_name(self, value):
        #     pass


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Updating Recipe objects"""
    ingredients = NestedIngredientSerializer(many=True, read_only=False)

    class Meta:
        model=Recipe
        fields=('id', 'name', 'ingredients')
        read_only_fields=('id', 'url')
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        ingredients_info = validated_data.pop('ingredients')
        
        for ingredient_info in ingredients_info:
            action = ingredient_info.pop('action', None)
            if action:
                ingredient_obj = get_object_or_404(Ingredient, **ingredient_info)
                if action == "remove":
                    instance.ingredients.remove(ingredient_obj)
                elif action == "delete":
                    ingredient_obj.delete()
            else:
                ingredient_name = ingredient_info.pop('name', None)
                ingredient_obj, _ = Ingredient.objects.get_or_create(
                    name=ingredient_name,
                    defaults=ingredient_info
                )
                instance.ingredients.add(ingredient_obj)
        instance.save()
        return instance
