"""
Serializers for the user API view.
"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5},
            'name': {'max_length': 20},
            }

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop('password', None)
        # call the update method on the model serializer base class
        # that is the one that is provided by the model serializer
        # it will perform all the steps for updating the object.
        # Used to leverage the existing logic from the model serializer
        # And it will only override and change what we need to change
        # it prevents us from reinventing the wheel.
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user.
        This is called at the validation stage of the view,
        when data is posted to the view, it's going to pass it to
        the serializer, and then it's going to call the
        validate method to validate that the data is correct"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _('unable to authenticate with provided credentials.')
            # this will be translated by the view to a http 400 bad request
            # and include the message
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
