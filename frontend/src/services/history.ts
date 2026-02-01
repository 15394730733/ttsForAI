/**
 * History API service.
 *
 * Provides methods for interacting with history endpoints.
 */
import http from './http'

export interface HistoryRecord {
  id: number
  task_id: string
  text_summary: string
  voice_params: string
  created_at: string
  file_path: string
  file_size: number
  status: string
}

export const historyService = {
  /**
   * Get history list.
   */
  async getHistory(skip = 0, limit = 20): Promise<{ records: HistoryRecord[]; total: number }> {
    const response = await http.get<{ records: HistoryRecord[]; total: number }>(
      `/history?skip=${skip}&limit=${limit}`
    )
    return response.data
  },

  /**
   * Delete history record.
   */
  async deleteHistory(id: number): Promise<void> {
    await http.delete(`/history/${id}`)
  },

  /**
   * Clear all history.
   */
  async clearHistory(): Promise<void> {
    await http.delete('/history/clear')
  },

  /**
   * Download audio from history.
   */
  async downloadAudio(taskId: string): Promise<Blob> {
    const response = await http.get(`/tts/download/${taskId}`, {
      responseType: 'blob',
    })
    return response.data
  },
}
