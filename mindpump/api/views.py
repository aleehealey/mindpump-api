from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView

from .models import FlashcardSet, Flashcard
from .repositories import FlashcardSetRepository, FlashcardRepository
from .serializers import (
    FlashcardSetSerializer,
    FlashcardSetListSerializer,
    FlashcardSerializer,
    CreateCardsBatchSerializer,
    EditCardsBatchSerializer,
    DeleteCardsBatchSerializer,
    StudyStatusUpdateSerializer,
    StudyStatusBatchSerializer,
)


class FlashcardSetViewSet(ModelViewSet):
    """
    Sets: list, create, retrieve, update, destroy. No auth for MVP.
    """

    def get_queryset(self):
        return FlashcardSetRepository.list_by_user(self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return FlashcardSetListSerializer
        return FlashcardSetSerializer

    def get_object(self):
        obj = FlashcardSetRepository.get_by_id_and_user(
            pk=self.kwargs["pk"],
            user=self.request.user,
        )
        if obj is None:
            from rest_framework.exceptions import NotFound
            raise NotFound()
        return obj

    def perform_update(self, serializer):
        obj = serializer.instance
        FlashcardSetRepository.update(
            obj,
            name=serializer.validated_data.get("name"),
            description=serializer.validated_data.get("description"),
        )

    def perform_destroy(self, instance):
        FlashcardSetRepository.delete(instance)

    @action(detail=True, methods=["post"], url_path="cards/batch")
    def create_cards_batch(self, request, pk=None):
        """POST /api/sets/:id/cards/batch/  Body: { "cards": [ { "front", "back" }, ... ] }"""
        obj = self.get_object()
        ser = CreateCardsBatchSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        created = FlashcardRepository.create_many(obj, ser.validated_data["cards"])
        return Response(
            FlashcardSerializer(created, many=True).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["patch"], url_path="cards/batch")
    def edit_cards_batch(self, request, pk=None):
        """PATCH /api/sets/:id/cards/batch/  Body: { "cards": [ { "id", "front?", "back?" }, ... ] }"""
        obj = self.get_object()
        ser = EditCardsBatchSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        updated = FlashcardRepository.update_batch(obj, ser.validated_data["cards"])
        return Response(FlashcardSerializer(updated, many=True).data)

    @action(detail=True, methods=["delete"], url_path="cards/batch")
    def delete_cards_batch(self, request, pk=None):
        """DELETE /api/sets/:id/cards/batch/  Body: { "card_ids": [ 1, 2, ... ] }"""
        obj = self.get_object()
        ser = DeleteCardsBatchSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        deleted_count = FlashcardRepository.delete_many(
            obj, ser.validated_data["card_ids"]
        )
        return Response({"deleted": deleted_count}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], url_path="cards/study/batch")
    def update_study_batch(self, request, pk=None):
        """PATCH /api/sets/:id/cards/study/batch/  Body: { "cards": [ { "id", "interval_days?", ... }, ... ] }"""
        obj = self.get_object()
        ser = StudyStatusBatchSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        updated = FlashcardRepository.update_study_batch(
            obj, ser.validated_data["cards"]
        )
        return Response(FlashcardSerializer(updated, many=True).data)


class FlashcardStudyView(APIView):
    """
    PATCH /api/cards/:id/study/  Body: { "interval_days?", "ease_factor?", "due_at?", "lapses?", "reps?" }
    Update one card's study status.
    """

    def patch(self, request, pk):
        card = FlashcardRepository.get_by_id(pk)
        if card is None:
            return Response(
                {"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND
            )
        if card.set.user_id is not None and getattr(request.user, "pk", None) != card.set.user_id:
            return Response(
                {"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND
            )
        ser = StudyStatusUpdateSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        FlashcardRepository.update_study(card, ser.validated_data)
        return Response(FlashcardSerializer(card).data)
