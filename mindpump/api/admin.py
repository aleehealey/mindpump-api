from django.contrib import admin
from .models import FlashcardSet, Flashcard


@admin.register(FlashcardSet)
class FlashcardSetAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "created_at", "updated_at"]
    list_filter = ["user"]
    raw_id_fields = ["user"]


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ["id", "set", "front_preview", "interval_days", "due_at", "reps", "lapses"]
    list_filter = ["set"]
    raw_id_fields = ["set"]

    def front_preview(self, obj):
        return (obj.front[:50] + "...") if len(obj.front) > 50 else obj.front
    front_preview.short_description = "Front"
