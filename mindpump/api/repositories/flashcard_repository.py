from django.db.models import QuerySet

from ..models import Flashcard

STUDY_FIELDS = {"interval_days", "ease_factor", "due_at", "lapses", "reps"}


class FlashcardRepository:
    """
    Flashcard (card) CRUD and study-status updates, using Django ORM.
    Study status lives on the card model.
    """

    @staticmethod
    def list_by_set(flashcard_set) -> QuerySet:
        return flashcard_set.cards.all().order_by("id")

    @staticmethod
    def get_by_id(pk):
        try:
            return Flashcard.objects.select_related("set").get(pk=pk)
        except Flashcard.DoesNotExist:
            return None

    @staticmethod
    def create(flashcard_set, *, front, back):
        return Flashcard.objects.create(
            set=flashcard_set,
            front=front,
            back=back,
        )

    @staticmethod
    def create_many(flashcard_set, items):
        """items: list of dicts with 'front' and 'back'. Returns list of created cards."""
        created = []
        for item in items:
            card = Flashcard.objects.create(
                set=flashcard_set,
                front=item["front"],
                back=item["back"],
            )
            created.append(card)
        return created

    @staticmethod
    def update(card, *, front=None, back=None):
        if front is not None:
            card.front = front
        if back is not None:
            card.back = back
        card.save(update_fields=["front", "back", "updated_at"])
        return card

    @staticmethod
    def update_batch(flashcard_set, items):
        """
        items: list of dicts with 'id' and optional 'front', 'back'.
        Returns list of updated cards.
        """
        updated = []
        for item in items:
            card_id = item.get("id")
            try:
                card = flashcard_set.cards.get(pk=card_id)
            except Flashcard.DoesNotExist:
                continue
            if "front" in item:
                card.front = item["front"]
            if "back" in item:
                card.back = item["back"]
            card.save()
            updated.append(card)
        return updated

    @staticmethod
    def delete_many(flashcard_set, card_ids):
        """Returns count of deleted cards."""
        deleted, _ = flashcard_set.cards.filter(pk__in=card_ids).delete()
        return deleted

    @staticmethod
    def update_study(card, data):
        """
        data: dict with optional interval_days, ease_factor, due_at, lapses, reps.
        Updates only provided keys. Returns the card.
        """
        update_fields = ["updated_at"]
        for key in STUDY_FIELDS:
            if key in data:
                setattr(card, key, data[key])
                update_fields.append(key)
        card.save(update_fields=update_fields)
        return card

    @staticmethod
    def update_study_batch(flashcard_set, items):
        """
        items: list of dicts with 'id' and optional study fields.
        Returns list of updated cards.
        """
        updated = []
        for item in items:
            card_id = item.get("id")
            try:
                card = flashcard_set.cards.get(pk=card_id)
            except Flashcard.DoesNotExist:
                continue
            for key in STUDY_FIELDS:
                if key in item:
                    setattr(card, key, item[key])
            card.save()
            updated.append(card)
        return updated
