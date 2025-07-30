"""
Common bulk processing utilities for handling array operations with Celery.
"""
import logging
from typing import Any

from celery import shared_task
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.module_loading import import_string

from django_bulk_drf.bulk_cache import BulkOperationCache

logger = logging.getLogger(__name__)


class BulkOperationResult:
    """Result container for bulk operations."""

    def __init__(self, task_id: str, total_items: int, operation_type: str):
        self.task_id = task_id
        self.total_items = total_items
        self.operation_type = operation_type
        self.success_count = 0
        self.error_count = 0
        self.errors: list[dict[str, Any]] = []
        self.created_ids: list[int] = []
        self.updated_ids: list[int] = []
        self.deleted_ids: list[int] = []

    def add_success(self, item_id: int | None = None, operation: str = "created"):
        self.success_count += 1
        if item_id:
            if operation == "created":
                self.created_ids.append(item_id)
            elif operation == "updated":
                self.updated_ids.append(item_id)
            elif operation == "deleted":
                self.deleted_ids.append(item_id)

    def add_error(self, index: int, error_message: str, item_data: Any = None):
        self.error_count += 1
        self.errors.append({
            "index": index,
            "error": error_message,
            "data": item_data,
        })

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "total_items": self.total_items,
            "operation_type": self.operation_type,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "errors": self.errors,
            "created_ids": self.created_ids,
            "updated_ids": self.updated_ids,
            "deleted_ids": self.deleted_ids,
        }


@shared_task(bind=True)
def bulk_create_task(self, serializer_class_path: str, data_list: list[dict], user_id: int | None = None):
    """
    Celery task for bulk creation of model instances.

    Args:
        serializer_class_path: Full path to the serializer class
            (e.g., 'augend.financial_transactions.api.serializers.FinancialTransactionSerializer')
        data_list: List of dictionaries containing data for each instance
        user_id: Optional user ID for audit purposes
    """
    task_id = self.request.id
    result = BulkOperationResult(task_id, len(data_list), "bulk_create")

    # Initialize progress tracking in Redis
    BulkOperationCache.set_task_progress(task_id, 0, len(data_list), "Starting bulk create...")

    try:
        serializer_class = import_string(serializer_class_path)
        instances_to_create = []

        # Validate all items first
        BulkOperationCache.set_task_progress(task_id, 0, len(data_list), "Validating data...")
        
        for index, item_data in enumerate(data_list):
            try:
                serializer = serializer_class(data=item_data)
                if serializer.is_valid():
                    instances_to_create.append((index, serializer.validated_data))
                else:
                    result.add_error(index, str(serializer.errors), item_data)
            except (ValidationError, ValueError) as e:
                result.add_error(index, str(e), item_data)
            
            # Update progress every 10 items or at the end
            if (index + 1) % 10 == 0 or index == len(data_list) - 1:
                BulkOperationCache.set_task_progress(
                    task_id, index + 1, len(data_list), f"Validated {index + 1}/{len(data_list)} items",
                )

        # Bulk create valid instances
        if instances_to_create:
            BulkOperationCache.set_task_progress(
                task_id, len(data_list), len(data_list), "Creating instances in database...",
            )
            
            with transaction.atomic():
                model_class = serializer_class.Meta.model
                instances = []

                for _, validated_data in instances_to_create:
                    instance = model_class(**validated_data)
                    instances.append(instance)

                created_instances = model_class.objects.bulk_create(instances)

                for instance in created_instances:
                    result.add_success(instance.id, "created")

        # Store final result in cache
        BulkOperationCache.set_task_result(task_id, result.to_dict())

        logger.info(
            "Bulk create task %s completed: %s created, %s errors",
            task_id,
            result.success_count,
            result.error_count,
        )

    except (ImportError, AttributeError) as e:
        logger.exception("Bulk create task %s failed", task_id)
        result.add_error(0, f"Task failed: {e!s}")
        BulkOperationCache.set_task_result(task_id, result.to_dict())

    return result.to_dict()


@shared_task(bind=True)
def bulk_update_task(self, serializer_class_path: str, updates_list: list[dict], user_id: int | None = None):
    """
    Celery task for bulk updating of model instances.

    Args:
        serializer_class_path: Full path to the serializer class
        updates_list: List of dictionaries containing id and update data for each instance
        user_id: Optional user ID for audit purposes
    """
    task_id = self.request.id
    result = BulkOperationResult(task_id, len(updates_list), "bulk_update")

    # Initialize progress tracking in Redis
    BulkOperationCache.set_task_progress(task_id, 0, len(updates_list), "Starting bulk update...")

    try:
        serializer_class = import_string(serializer_class_path)
        model_class = serializer_class.Meta.model

        for index, update_data in enumerate(updates_list):
            try:
                instance_id = update_data.get("id")
                if not instance_id:
                    result.add_error(index, "Missing 'id' field", update_data)
                    continue

                try:
                    instance = model_class.objects.get(id=instance_id)
                except model_class.DoesNotExist:
                    result.add_error(index, f"Instance with id {instance_id} not found", update_data)
                    continue

                serializer = serializer_class(instance, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    result.add_success(instance.id, "updated")
                else:
                    result.add_error(index, str(serializer.errors), update_data)

            except (ValidationError, ValueError) as e:
                result.add_error(index, str(e), update_data)

            # Update progress every 10 items or at the end
            if (index + 1) % 10 == 0 or index == len(updates_list) - 1:
                BulkOperationCache.set_task_progress(
                    task_id, index + 1, len(updates_list), f"Updated {index + 1}/{len(updates_list)} items",
                )

        # Store final result in cache
        BulkOperationCache.set_task_result(task_id, result.to_dict())

        logger.info(
            "Bulk update task %s completed: %s updated, %s errors",
            task_id,
            result.success_count,
            result.error_count,
        )

    except (ImportError, AttributeError) as e:
        logger.exception("Bulk update task %s failed", task_id)
        result.add_error(0, f"Task failed: {e!s}")
        BulkOperationCache.set_task_result(task_id, result.to_dict())

    return result.to_dict()


@shared_task(bind=True)
def bulk_delete_task(self, model_class_path: str, ids_list: list[int], user_id: int | None = None):
    """
    Celery task for bulk deletion of model instances.

    Args:
        model_class_path: Full path to the model class
        ids_list: List of IDs to delete
        user_id: Optional user ID for audit purposes
    """
    task_id = self.request.id
    result = BulkOperationResult(task_id, len(ids_list), "bulk_delete")

    # Initialize progress tracking in Redis
    BulkOperationCache.set_task_progress(task_id, 0, len(ids_list), "Starting bulk delete...")

    try:
        model_class = import_string(model_class_path)

        for index, instance_id in enumerate(ids_list):
            try:
                instance = model_class.objects.get(id=instance_id)
                instance.delete()
                result.add_success(instance_id, "deleted")
            except model_class.DoesNotExist:
                result.add_error(index, f"Instance with id {instance_id} not found", instance_id)
            except (ValidationError, ValueError) as e:
                result.add_error(index, str(e), instance_id)

            # Update progress every 10 items or at the end
            if (index + 1) % 10 == 0 or index == len(ids_list) - 1:
                BulkOperationCache.set_task_progress(
                    task_id, index + 1, len(ids_list), f"Deleted {index + 1}/{len(ids_list)} items",
                )

        # Store final result in cache
        BulkOperationCache.set_task_result(task_id, result.to_dict())

        logger.info(
            "Bulk delete task %s completed: %s deleted, %s errors",
            task_id,
            result.success_count,
            result.error_count,
        )

    except (ImportError, AttributeError) as e:
        logger.exception("Bulk delete task %s failed", task_id)
        result.add_error(0, f"Task failed: {e!s}")
        BulkOperationCache.set_task_result(task_id, result.to_dict())

    return result.to_dict()


@shared_task(bind=True)
def bulk_replace_task(self, serializer_class_path: str, replacements_list: list[dict], user_id: int | None = None):
    """
    Celery task for bulk replacement (full update) of model instances.

    Args:
        serializer_class_path: Full path to the serializer class
        replacements_list: List of dictionaries containing complete data for each instance (must include 'id')
        user_id: Optional user ID for audit purposes
    """
    task_id = self.request.id
    result = BulkOperationResult(task_id, len(replacements_list), "bulk_replace")

    # Initialize progress tracking in Redis
    BulkOperationCache.set_task_progress(task_id, 0, len(replacements_list), "Starting bulk replace...")

    try:
        serializer_class = import_string(serializer_class_path)
        
        # Get the model class from the serializer
        model_class = serializer_class.Meta.model
        
        # Validate all items first
        BulkOperationCache.set_task_progress(task_id, 0, len(replacements_list), "Validating data...")
        
        valid_replacements = []
        for index, item_data in enumerate(replacements_list):
            try:
                # Extract ID for the instance to replace
                instance_id = item_data.get("id")
                if not instance_id:
                    result.add_error(index, "Missing 'id' field for replacement", item_data)
                    continue
                
                # Get the existing instance
                try:
                    instance = model_class.objects.get(id=instance_id)
                except model_class.DoesNotExist:
                    result.add_error(index, f"Instance with id {instance_id} not found", item_data)
                    continue
                
                # Validate the complete replacement data
                serializer = serializer_class(instance, data=item_data)
                if serializer.is_valid():
                    valid_replacements.append((index, instance, serializer.validated_data, instance_id))
                else:
                    result.add_error(index, str(serializer.errors), item_data)
                    
            except (ValidationError, ValueError) as e:
                result.add_error(index, str(e), item_data)
            
            # Update progress every 10 items or at the end
            if (index + 1) % 10 == 0 or index == len(replacements_list) - 1:
                BulkOperationCache.set_task_progress(
                    task_id, index + 1, len(replacements_list), f"Validated {index + 1}/{len(replacements_list)} items",
                )

        # Perform the bulk replacement in the database
        if valid_replacements:
            BulkOperationCache.set_task_progress(
                task_id, len(replacements_list), len(replacements_list), "Replacing instances in database..."
            )
            
            with transaction.atomic():
                for index, instance, validated_data, instance_id in valid_replacements:
                    try:
                        # Update all fields with validated data
                        for field, value in validated_data.items():
                            setattr(instance, field, value)
                        instance.save()
                        result.add_success(instance_id, "updated")
                        
                    except Exception as e:
                        result.add_error(index, f"Database error: {e!s}", validated_data)

        # Store final result in cache
        BulkOperationCache.set_task_result(task_id, result.to_dict())

        logger.info(
            "Bulk replace task %s completed: %s replaced, %s errors",
            task_id,
            result.success_count,
            result.error_count,
        )

    except (ImportError, AttributeError) as e:
        logger.exception("Bulk replace task %s failed", task_id)
        result.add_error(0, f"Task failed: {e!s}")
        BulkOperationCache.set_task_result(task_id, result.to_dict())

    return result.to_dict()


@shared_task(bind=True)
def bulk_get_task(self, model_class_path: str, serializer_class_path: str, query_params: dict, user_id: int | None = None):
    """
    Celery task for bulk retrieval of model instances.

    Args:
        model_class_path: Full path to the model class
        serializer_class_path: Full path to the serializer class
        query_params: Dictionary containing query parameters (ids, filters, etc.)
        user_id: Optional user ID for audit purposes
    """
    task_id = self.request.id
    
    # Initialize progress tracking in Redis
    BulkOperationCache.set_task_progress(task_id, 0, 1, "Starting bulk retrieval...")

    try:
        model_class = import_string(model_class_path)
        serializer_class = import_string(serializer_class_path)
        
        # Build the queryset based on query parameters
        queryset = model_class.objects.all()
        
        # Handle different query types
        if "ids" in query_params:
            # ID-based retrieval
            ids_list = query_params["ids"]
            queryset = queryset.filter(id__in=ids_list)
            total_expected = len(ids_list)
            
        elif "filters" in query_params:
            # Complex filtering
            filters = query_params["filters"]
            for field, value in filters.items():
                # Support various Django ORM lookups
                if isinstance(value, dict):
                    # Handle complex lookups like {'gte': 100, 'lte': 200}
                    for lookup, lookup_value in value.items():
                        filter_key = f"{field}__{lookup}"
                        queryset = queryset.filter(**{filter_key: lookup_value})
                else:
                    # Simple equality filter
                    queryset = queryset.filter(**{field: value})
            
            # Get total count for progress tracking
            total_expected = queryset.count()
            
        else:
            # Default to all records (be careful with this!)
            total_expected = queryset.count()
            
            # Limit large queries to prevent memory issues
            if total_expected > 10000:  # Configurable limit
                raise ValueError("Query would return too many records. Please add filters to limit results.")
        
        # Update progress
        BulkOperationCache.set_task_progress(task_id, 0, total_expected, f"Retrieving {total_expected} records...")
        
        # Execute the query and serialize results
        instances = list(queryset.iterator())  # Use iterator for memory efficiency
        
        # Update progress
        BulkOperationCache.set_task_progress(task_id, len(instances), total_expected, "Serializing results...")
        
        # Serialize in chunks to avoid memory issues
        chunk_size = 100
        serialized_results = []
        
        for i in range(0, len(instances), chunk_size):
            chunk = instances[i:i + chunk_size]
            serializer = serializer_class(chunk, many=True)
            serialized_results.extend(serializer.data)
            
            # Update progress
            processed = min(i + chunk_size, len(instances))
            BulkOperationCache.set_task_progress(
                task_id, processed, len(instances), f"Serialized {processed}/{len(instances)} records"
            )
        
        # Prepare final result
        result = {
            "task_id": task_id,
            "operation_type": "bulk_get",
            "total_records": len(serialized_results),
            "query_params": query_params,
            "results": serialized_results,
            "success": True
        }
        
        # Store result in cache
        BulkOperationCache.set_task_result(task_id, result)
        
        logger.info(
            "Bulk get task %s completed: %s records retrieved",
            task_id,
            len(serialized_results)
        )
        
        return result

    except Exception as e:
        logger.exception("Bulk get task %s failed", task_id)
        error_result = {
            "task_id": task_id,
            "operation_type": "bulk_get",
            "success": False,
            "error": str(e),
            "query_params": query_params
        }
        BulkOperationCache.set_task_result(task_id, error_result)
        return error_result
