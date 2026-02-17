"""
HTTP Basic Auth using a single master username/password from settings.
Credentials are configured in settings.py; they are not stored in the Django User table.
"""
import base64
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from rest_framework import authentication, exceptions

User = get_user_model()


class SettingsBasicAuthentication(authentication.BaseAuthentication):
    """
    Authenticate using Authorization: Basic <base64(username:password)>.
    Username and password are compared to settings.API_BASIC_AUTH_USERNAME
    and settings.API_BASIC_AUTH_PASSWORD. On success, returns the same
    Django User (get_or_create by username) so request.user is stable.
    """

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header or not auth_header.startswith("Basic "):
            return None

        try:
            encoded = auth_header[6:].strip()
            decoded = base64.b64decode(encoded).decode("latin1")
            parts = force_str(decoded).split(":", 1)
            if len(parts) != 2:
                raise exceptions.AuthenticationFailed("Invalid Basic auth header.")
            username, password = parts[0], parts[1]
        except (ValueError, UnicodeDecodeError, IndexError):
            raise exceptions.AuthenticationFailed("Invalid Basic auth header.")

        expected_username = getattr(settings, "API_BASIC_AUTH_USERNAME", None)
        expected_password = getattr(settings, "API_BASIC_AUTH_PASSWORD", None)

        if not expected_username or expected_password is None:
            raise exceptions.AuthenticationFailed(
                "Server misconfiguration: API_BASIC_AUTH_USERNAME and API_BASIC_AUTH_PASSWORD must be set."
            )

        if not (
            _constant_time_compare(username, expected_username)
            and _constant_time_compare(password, expected_password)
        ):
            raise exceptions.AuthenticationFailed("Invalid username or password.")

        user, _ = User.objects.get_or_create(
            username=expected_username,
            defaults={"email": ""},
        )
        return (user, None)


def _constant_time_compare(a, b):
    """Constant-time string comparison to reduce timing attack surface."""
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0
