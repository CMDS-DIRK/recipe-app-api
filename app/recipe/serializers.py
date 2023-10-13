"""
Serializers for recipe APIs
"""

from rest_framework import serializers

# this import does not work but it does work in the code
from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes"""

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']
