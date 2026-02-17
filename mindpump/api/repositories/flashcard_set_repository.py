from django.db.models import QuerySet

from ..models import FlashcardSet


class FlashcardSetRepository:
    """FlashcardSet CRUD scoped by user, using Django ORM."""

    @staticmethod
    def list_by_user(user) -> QuerySet:
        if getattr(user, "is_authenticated", False):
            return FlashcardSet.objects.filter(user=user).prefetch_related("cards").order_by("-updated_at")
        return FlashcardSet.objects.filter(user__isnull=True).prefetch_related("cards").order_by("-updated_at")

    @staticmethod
    def get_by_id_and_user(pk, user):
        if getattr(user, "is_authenticated", False):
            try:
                return FlashcardSet.objects.prefetch_related("cards").get(pk=pk, user=user)
            except FlashcardSet.DoesNotExist:
                return None
        try:
            return FlashcardSet.objects.prefetch_related("cards").get(pk=pk, user__isnull=True)
        except FlashcardSet.DoesNotExist:
            return None

    @staticmethod
    def create(user, *, name, description=""):
        return FlashcardSet.objects.create(
            user=user,
            name=name,
            description=description or "",
        )

    @staticmethod
    def update(flashcard_set, *, name=None, description=None):
        if name is not None:
            flashcard_set.name = name
        if description is not None:
            flashcard_set.description = description
        flashcard_set.save(update_fields=["name", "description", "updated_at"])
        return flashcard_set

    @staticmethod
    def delete(flashcard_set):
        flashcard_set.delete()
