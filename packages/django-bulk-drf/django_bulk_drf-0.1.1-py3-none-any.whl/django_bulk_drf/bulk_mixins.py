"""
Bulk operation mixins for DRF ViewSets.
"""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from django_bulk_drf.bulk_processing import (
    bulk_create_task,
    bulk_delete_task,
    bulk_replace_task,
    bulk_update_task,
)


class BulkOperationsMixin:
    """Mixin providing bulk operations through a single endpoint with different HTTP methods."""

    @action(detail=False, methods=["post", "patch", "put", "delete"], url_path="bulk")
    def bulk(self, request):
        """
        Handle bulk operations based on HTTP method:
        - POST: Create multiple instances
        - PATCH: Update multiple instances (partial updates)
        - PUT: Replace multiple instances (full updates)
        - DELETE: Delete multiple instances
        
        Returns a task ID for tracking the bulk operation.
        """
        if request.method == "POST":
            return self._bulk_create(request)
        elif request.method == "PATCH":
            return self._bulk_update(request)
        elif request.method == "PUT":
            return self._bulk_replace(request)
        elif request.method == "DELETE":
            return self._bulk_delete(request)
    
    def _bulk_create(self, request):
        """
        Create multiple instances asynchronously.

        Expects a JSON array of objects to create.
        Returns a task ID for tracking the bulk operation.
        """
        data_list = request.data
        if not isinstance(data_list, list):
            return Response(
                {"error": "Expected a list of objects"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not data_list:
            return Response(
                {"error": "Empty list provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the serializer class path
        serializer_class = self.get_serializer_class()
        serializer_class_path = f"{serializer_class.__module__}.{serializer_class.__name__}"

        # Start the bulk create task
        user_id = request.user.id if request.user.is_authenticated else None
        task = bulk_create_task.delay(serializer_class_path, data_list, user_id)

        return Response(
            {
                "message": f"Bulk create task started for {len(data_list)} items",
                "task_id": task.id,
                "total_items": len(data_list),
                "status_url": f"/api/bulk-operations/{task.id}/status/",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    def _bulk_update(self, request):
        """
        Update multiple instances asynchronously.

        Expects a JSON array of objects with 'id' and update data.
        Returns a task ID for tracking the bulk operation.
        """
        updates_list = request.data
        if not isinstance(updates_list, list):
            return Response(
                {"error": "Expected a list of objects"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not updates_list:
            return Response(
                {"error": "Empty list provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate that all items have an 'id' field
        for i, item in enumerate(updates_list):
            if not isinstance(item, dict) or "id" not in item:
                return Response(
                    {"error": f"Item at index {i} is missing 'id' field"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Get the serializer class path
        serializer_class = self.get_serializer_class()
        serializer_class_path = f"{serializer_class.__module__}.{serializer_class.__name__}"

        # Start the bulk update task
        user_id = request.user.id if request.user.is_authenticated else None
        task = bulk_update_task.delay(serializer_class_path, updates_list, user_id)

        return Response(
            {
                "message": f"Bulk update task started for {len(updates_list)} items",
                "task_id": task.id,
                "total_items": len(updates_list),
                "status_url": f"/api/bulk-operations/{task.id}/status/",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    def _bulk_replace(self, request):
        """
        Replace multiple instances asynchronously (full updates).

        Expects a JSON array of complete objects with 'id' and all required fields.
        Returns a task ID for tracking the bulk operation.
        """
        replacements_list = request.data
        if not isinstance(replacements_list, list):
            return Response(
                {"error": "Expected a list of objects"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not replacements_list:
            return Response(
                {"error": "Empty list provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate that all items have an 'id' field
        for i, item in enumerate(replacements_list):
            if not isinstance(item, dict) or "id" not in item:
                return Response(
                    {"error": f"Item at index {i} is missing 'id' field"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Get the serializer class path
        serializer_class = self.get_serializer_class()
        serializer_class_path = f"{serializer_class.__module__}.{serializer_class.__name__}"

        # Start the bulk replace task
        user_id = request.user.id if request.user.is_authenticated else None
        task = bulk_update_task.delay(serializer_class_path, replacements_list, user_id)

        return Response(
            {
                "message": f"Bulk replace task started for {len(replacements_list)} items",
                "task_id": task.id,
                "total_items": len(replacements_list),
                "status_url": f"/api/bulk-operations/{task.id}/status/",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    def _bulk_delete(self, request):
        """
        Delete multiple instances asynchronously.

        Expects a JSON array of IDs to delete.
        Returns a task ID for tracking the bulk operation.
        """
        ids_list = request.data
        if not isinstance(ids_list, list):
            return Response(
                {"error": "Expected a list of IDs"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not ids_list:
            return Response(
                {"error": "Empty list provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate that all items are integers (IDs)
        for i, item_id in enumerate(ids_list):
            if not isinstance(item_id, int):
                return Response(
                    {"error": f"Item at index {i} is not a valid ID"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Get the model class path
        model_class = self.get_queryset().model
        model_class_path = f"{model_class.__module__}.{model_class.__name__}"

        # Start the bulk delete task
        user_id = request.user.id if request.user.is_authenticated else None
        task = bulk_delete_task.delay(model_class_path, ids_list, user_id)

        return Response(
            {
                "message": f"Bulk delete task started for {len(ids_list)} items",
                "task_id": task.id,
                "total_items": len(ids_list),
                "status_url": f"/api/bulk-operations/{task.id}/status/",
            },
            status=status.HTTP_202_ACCEPTED,
        )


# Keep individual mixins for backward compatibility
class BulkCreateMixin:
    """Mixin to add bulk create functionality to ViewSets."""

    @action(detail=False, methods=["post"], url_path="bulk")
    def bulk_create(self, request):
        """
        Create multiple instances asynchronously.

        Expects a JSON array of objects to create.
        Returns a task ID for tracking the bulk operation.
        """
        return BulkOperationsMixin._bulk_create(self, request)


class BulkUpdateMixin:
    """Mixin to add bulk update functionality to ViewSets."""

    @action(detail=False, methods=["patch"], url_path="bulk")
    def bulk_update(self, request):
        """
        Update multiple instances asynchronously.

        Expects a JSON array of objects with 'id' and update data.
        Returns a task ID for tracking the bulk operation.
        """
        return BulkOperationsMixin._bulk_update(self, request)


class BulkDeleteMixin:
    """Mixin to add bulk delete functionality to ViewSets."""

    @action(detail=False, methods=["delete"], url_path="bulk")
    def bulk_delete(self, request):
        """
        Delete multiple instances asynchronously.

        Expects a JSON array of IDs to delete.
        Returns a task ID for tracking the bulk operation.
        """
        return BulkOperationsMixin._bulk_delete(self, request)


class BulkReplaceMixin:
    """Mixin to add bulk replace functionality to ViewSets."""

    @action(detail=False, methods=["put"], url_path="bulk")
    def bulk_replace(self, request):
        """
        Replace multiple instances asynchronously (full updates).

        Expects a JSON array of complete objects with 'id' and all required fields.
        Returns a task ID for tracking the bulk operation.
        """
        return BulkOperationsMixin._bulk_replace(self, request)
