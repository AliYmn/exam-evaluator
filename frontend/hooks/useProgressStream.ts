/**
 * React hook for Server-Sent Events (SSE) progress streaming
 *
 * Usage:
 * ```typescript
 * const { progress, isConnected, error } = useProgressStream(
 *   'evaluation',
 *   evaluationId,
 *   token
 * );
 * ```
 */

import { useState, useEffect, useRef } from 'react';

const CONTENT_API_URL = process.env.NEXT_PUBLIC_CONTENT_API_URL || 'http://localhost:8001/api/v1';

export interface ProgressData {
  task_type: string;
  task_id: string;
  percentage: number;
  message: string;
  status: 'processing' | 'completed' | 'failed';
  metadata?: {
    total_questions?: number;
    current_question?: number;
    evaluated_questions?: number;
    evaluation_id?: string;
  };
}

export interface StreamMessage {
  type?: 'connected' | 'done' | 'timeout' | 'error';
  message?: string;
  status?: string;
}

export function useProgressStream(
  taskType: 'evaluation' | 'student',
  taskId: string | number,
  token: string | null,
  enabled: boolean = true
) {
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!enabled || !token || !taskId) {
      return;
    }

    // Build SSE endpoint URL with token as query parameter
    // EventSource doesn't support custom headers, so we pass token as query param
    const cleanToken = token.replace('Bearer ', ''); // Remove Bearer prefix
    const baseEndpoint = taskType === 'evaluation'
      ? `${CONTENT_API_URL}/exam/${taskId}/progress-stream`
      : `${CONTENT_API_URL}/exam/student/${taskId}/progress-stream`;

    const endpoint = `${baseEndpoint}?token=${encodeURIComponent(cleanToken)}`;

    console.log(`Connecting to SSE: ${baseEndpoint}`);

    try {
      // Create EventSource with token in URL query parameter
      const eventSource = new EventSource(endpoint);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        console.log('SSE connection opened');
        setIsConnected(true);
        setError(null);
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('SSE message:', data);

          // Check if this is a control message
          if (data.type) {
            const streamMsg = data as StreamMessage;

            if (streamMsg.type === 'connected') {
              setIsConnected(true);
            } else if (streamMsg.type === 'done') {
              console.log('SSE stream completed');
              eventSource.close();
              setIsConnected(false);
            } else if (streamMsg.type === 'timeout' || streamMsg.type === 'error') {
              console.error('SSE error:', streamMsg.message);
              setError(streamMsg.message || 'Stream error');
              eventSource.close();
              setIsConnected(false);
            }
          } else {
            // This is progress data
            setProgress(data as ProgressData);
          }
        } catch (err) {
          console.error('Failed to parse SSE message:', err);
        }
      };

      eventSource.onerror = (err) => {
        console.error('SSE error:', err);
        setError('Connection error');
        setIsConnected(false);
        eventSource.close();
      };

      // Cleanup on unmount
      return () => {
        console.log('Closing SSE connection');
        eventSource.close();
        setIsConnected(false);
      };
    } catch (err) {
      console.error('Failed to create EventSource:', err);
      setError('Failed to connect to progress stream');
    }
  }, [taskType, taskId, token, enabled]);

  return {
    progress,
    isConnected,
    error,
    disconnect: () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        setIsConnected(false);
      }
    },
  };
}
