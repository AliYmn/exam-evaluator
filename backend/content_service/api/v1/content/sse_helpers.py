"""
Server-Sent Events (SSE) streaming helpers
Reusable progress streaming logic
"""

import asyncio
import json
from typing import AsyncGenerator

from libs.cache.progress_tracker import ProgressTracker


async def create_progress_stream(
    resource_type: str, resource_id: str, max_duration_seconds: int = 300, poll_interval: float = 1.0
) -> AsyncGenerator[str, None]:
    """
    Generic SSE progress stream generator.

    Args:
        resource_type: Type of resource ("evaluation" or "student_response")
        resource_id: Resource ID to track
        max_duration_seconds: Maximum stream duration (default 5 minutes)
        poll_interval: Polling interval in seconds (default 1 second)

    Yields:
        SSE formatted messages
    """
    try:
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connected', 'message': 'Connected to progress stream'})}\n\n"

        # Poll Redis for progress updates
        last_progress = None
        max_iterations = int(max_duration_seconds / poll_interval)
        iteration = 0

        while iteration < max_iterations:
            # Get current progress from Redis
            progress_data = ProgressTracker.get_progress(resource_type, resource_id)

            if progress_data:
                # Only send if progress changed
                if progress_data != last_progress:
                    yield f"data: {json.dumps(progress_data)}\n\n"
                    last_progress = progress_data

                # If completed or failed, send final message and close
                if progress_data.get("status") in ["completed", "failed"]:
                    yield f"data: {json.dumps({'type': 'done', 'status': progress_data.get('status')})}\n\n"
                    break

            # Wait before next poll
            await asyncio.sleep(poll_interval)
            iteration += 1

        # If max iterations reached, send timeout message
        if iteration >= max_iterations:
            yield f"data: {json.dumps({'type': 'timeout', 'message': 'Stream timeout'})}\n\n"

    except Exception as e:
        print(f"SSE stream error: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
