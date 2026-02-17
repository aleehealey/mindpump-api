from rest_framework import serializers
from .models import FlashcardSet, Flashcard


class FlashcardStudyStatusSerializer(serializers.ModelSerializer):
    """Read/write spaced-repetition fields only."""

    class Meta:
        model = Flashcard
        fields = [
            "id",
            "interval_days",
            "ease_factor",
            "due_at",
            "lapses",
            "reps",
        ]
        read_only_fields = ["id"]


class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = [
            "id",
            "front",
            "back",
            "interval_days",
            "ease_factor",
            "due_at",
            "lapses",
            "reps",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FlashcardMinimalSerializer(serializers.ModelSerializer):
    """For create batch: only front/back."""

    class Meta:
        model = Flashcard
        fields = ["front", "back"]


class FlashcardSetSerializer(serializers.ModelSerializer):
    cards = FlashcardSerializer(many=True, read_only=True)
    card_count = serializers.SerializerMethodField()

    class Meta:
        model = FlashcardSet
        fields = [
            "id",
            "name",
            "description",
            "card_count",
            "cards",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_card_count(self, obj):
        return getattr(obj, "_card_count", obj.cards.count())

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request and getattr(request.user, "is_authenticated", False) else None
        return FlashcardSet.objects.create(user=user, **validated_data)


class FlashcardSetListSerializer(serializers.ModelSerializer):
    """List view: no cards, just count."""

    card_count = serializers.SerializerMethodField()

    class Meta:
        model = FlashcardSet
        fields = [
            "id",
            "name",
            "description",
            "card_count",
            "created_at",
            "updated_at",
        ]

    def get_card_count(self, obj):
        return obj.cards.count()


# --- Batch / study request serializers ---


class CreateCardsBatchSerializer(serializers.Serializer):
    cards = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        help_text="List of { front, back }",
    )

    def validate_cards(self, value):
        for i, item in enumerate(value):
            if not isinstance(item, dict):
                raise serializers.ValidationError(f"Item {i} must be {{ front, back }}")
            if "front" not in item or "back" not in item:
                raise serializers.ValidationError(f"Item {i} must have 'front' and 'back'")
        return value


class EditCardsBatchSerializer(serializers.Serializer):
    cards = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of { id, front?, back? }",
    )

    def validate_cards(self, value):
        for i, item in enumerate(value):
            if not isinstance(item, dict) or "id" not in item:
                raise serializers.ValidationError(f"Item {i} must have 'id'")
        return value


class DeleteCardsBatchSerializer(serializers.Serializer):
    card_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of card IDs to delete",
    )


class StudyStatusUpdateSerializer(serializers.Serializer):
    """Update study status for one card. All fields optional."""

    interval_days = serializers.IntegerField(min_value=0, required=False)
    ease_factor = serializers.FloatField(min_value=1.3, required=False)
    due_at = serializers.DateTimeField(required=False, allow_null=True)
    lapses = serializers.IntegerField(min_value=0, required=False)
    reps = serializers.IntegerField(min_value=0, required=False)


class StudyStatusBatchSerializer(serializers.Serializer):
    """Batch update study status. Each item: id + optional study fields."""

    cards = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of { id, interval_days?, ease_factor?, due_at?, lapses?, reps? }",
    )

    def validate_cards(self, value):
        for i, item in enumerate(value):
            if not isinstance(item, dict) or "id" not in item:
                raise serializers.ValidationError(f"Item {i} must have 'id'")
        return value
