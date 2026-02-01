/**
 * Queue API service.
 *
 * Provides methods for interacting with queue endpoints.
 */
import http from './http'

export interface QueueStatus {
  queued_count: number
  processing_count: number
  completed_count: number
  current_task: any
  max_queue_size: number
}

export const queueService = {
  /**
   * Get queue status.
   */
  async getStatus(): Promise<QueueStatus> {
    const response = await http.get<QueueStatus>('/queue/status')
    return response.data
  },
}
