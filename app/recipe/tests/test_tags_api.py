"""
Tests for tags API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

def create_user(email="user@example.com", password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)


class PublicTagsAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth required for retrieving tags."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""
        Tag.objects.create(user=self.user, name='Soup')
        Tag.objects.create(user=self.user, name='Mexican')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        tag_1 = Tag.objects.create(user=self.user, name='Soup')
        tag_2 = Tag.objects.create(user=self.user, name='Mexican')

        unauthenticated_user = create_user(
            email='test@example.com',
            password='testpass123',
        )
        Tag.objects.create(user=unauthenticated_user, name='Snack')
        Tag.objects.create(user=unauthenticated_user, name='Seafood')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.filter(user=self.user).order_by('id')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(len(res.data), 2)
        self.assertEqual(tags.first().user_id, self.user.id)
        self.assertEqual(tags.last().user_id, self.user.id)
        self.assertEqual(tags.first().id, tag_1.id)
        self.assertEqual(tags.last().id, tag_2.id)

        self.assertEqual(res.data, serializer.data)
