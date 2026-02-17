from django.contrib.auth import get_user_model

User = get_user_model()


class UserRepository:
    """User lookup by id (for future auth)."""

    @staticmethod
    def get_by_id(pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None
