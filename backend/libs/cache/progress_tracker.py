"""
Progress tracking utility for real-time updates via SSE.

This module provides functions to track task progress in Redis,
allowing SSE endpoints to stream updates to clients.
"""

import json
from typing import Dict, Any, Optional
from libs.cache.cache import CacheService


class ProgressTracker:
    """Track task progress in Redis for SSE streaming."""

    @staticmethod
    def _get_key(task_type: str, task_id: str) -> str:
        """Generate Redis key for task progress."""
        return f"progress:{task_type}:{task_id}"

    @staticmethod
    def set_progress(
        task_type: str,
        task_id: str,
        percentage: float,
        message: str,
        status: str = "processing",
        metadata: Optional[Dict[str, Any]] = None,
        ttl: int = 3600,
    ) -> None:
        """
        Set task progress in Redis.

        Args:
            task_type: Type of task (e.g., "evaluation", "student_response")
            task_id: Unique task identifier
            percentage: Progress percentage (0-100)
            message: Human-readable progress message
            status: Task status (processing, completed, failed)
            metadata: Additional task-specific data
            ttl: Time-to-live in seconds (default 1 hour)
        """
        key = ProgressTracker._get_key(task_type, task_id)

        progress_data = {
            "task_type": task_type,
            "task_id": task_id,
            "percentage": round(percentage, 2),
            "message": message,
            "status": status,
            "metadata": metadata or {},
        }

        # Use raw Redis client (no encryption for progress tracking)
        CacheService.client.setex(key, ttl, json.dumps(progress_data))

    @staticmethod
    def get_progress(task_type: str, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task progress from Redis.

        Args:
            task_type: Type of task
            task_id: Task identifier

        Returns:
            Progress data dict or None if not found
        """
        key = ProgressTracker._get_key(task_type, task_id)
        # Use raw Redis client (no decryption for progress tracking)
        data = CacheService.client.get(key)

        if data:
            # Redis returns bytes, decode to string
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            return json.loads(data)
        return None

    @staticmethod
    def delete_progress(task_type: str, task_id: str) -> None:
        """
        Delete task progress from Redis.

        Args:
            task_type: Type of task
            task_id: Task identifier
        """
        key = ProgressTracker._get_key(task_type, task_id)
        # Use raw Redis client
        CacheService.client.delete(key)

    @staticmethod
    def set_evaluation_progress(
        evaluation_id: str,
        percentage: float,
        message: str,
        status: str = "processing",
        total_questions: Optional[int] = None,
        current_question: Optional[int] = None,
    ) -> None:
        """
        Set evaluation progress (answer key parsing).

        Args:
            evaluation_id: Evaluation ID
            percentage: Progress percentage
            message: Status message
            status: processing/completed/failed
            total_questions: Total questions parsed
            current_question: Current question being processed
        """
        metadata = {}
        if total_questions is not None:
            metadata["total_questions"] = total_questions
        if current_question is not None:
            metadata["current_question"] = current_question

        ProgressTracker.set_progress(
            task_type="evaluation",
            task_id=evaluation_id,
            percentage=percentage,
            message=message,
            status=status,
            metadata=metadata,
        )

    @staticmethod
    def set_student_progress(
        student_response_id: int,
        evaluation_id: str,
        percentage: float,
        message: str,
        status: str = "processing",
        total_questions: Optional[int] = None,
        evaluated_questions: Optional[int] = None,
    ) -> None:
        """
        Set student evaluation progress.

        Args:
            student_response_id: Student response ID
            evaluation_id: Parent evaluation ID
            percentage: Progress percentage
            message: Status message
            status: processing/completed/failed
            total_questions: Total questions
            evaluated_questions: Questions evaluated so far
        """
        metadata = {
            "evaluation_id": evaluation_id,
        }
        if total_questions is not None:
            metadata["total_questions"] = total_questions
        if evaluated_questions is not None:
            metadata["evaluated_questions"] = evaluated_questions

        ProgressTracker.set_progress(
            task_type="student_response",
            task_id=str(student_response_id),
            percentage=percentage,
            message=message,
            status=status,
            metadata=metadata,
        )
