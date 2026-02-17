from django.conf import settings
from django.db import models


class FlashcardSet(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="flashcard_sets",
        null=True,  # allow existing rows; new sets always have user from auth
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name


class Flashcard(models.Model):
    set = models.ForeignKey(
        FlashcardSet,
        on_delete=models.CASCADE,
        related_name="cards",
    )
    front = models.TextField()
    back = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Spaced repetition (study status)
    interval_days = models.PositiveIntegerField(default=0)
    ease_factor = models.FloatField(default=2.5)
    due_at = models.DateTimeField(null=True, blank=True)
    lapses = models.PositiveIntegerField(default=0)
    reps = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.front[:50]}..." if len(self.front) > 50 else self.front
