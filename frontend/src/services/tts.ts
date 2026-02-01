/**
 * TTS API service.
 *
 * Provides methods for interacting with TTS endpoints.
 */
import http from './http'
import type {
  TaskCreateRequest,
  TaskResponse,
  ErrorResponse,
} from '@/types/api'

export const ttsService = {
  /**
   * Create a new TTS generation task.
   */
  async createTask(request: TaskCreateRequest): Promise<TaskResponse> {
    const response = await http.post<TaskResponse>('/tts/generate', request)
    return response.data
  },

  /**
   * Get task status by ID.
   */
  async getTask(taskId: string): Promise<TaskResponse> {
    const response = await http.get<TaskResponse>(`/tts/tasks/${taskId}`)
    return response.data
  },

  /**
   * Cancel a queued task.
   */
  async cancelTask(taskId: string): Promise<{ task_id: string; status: string }> {
    const response = await http.delete<{ task_id: string; status: string }>(
      `/tts/tasks/${taskId}`
    )
    return response.data
  },

  /**
   * Download audio file.
   */
  async downloadAudio(taskId: string): Promise<Blob> {
    const response = await http.get(`/tts/download/${taskId}`, {
      responseType: 'blob',
    })
    return response.data
  },

  /**
   * Get available voices.
   */
  async getVoices(): Promise<{ voices: Array<{ name: string; voice_id: string; description: string; default: boolean }> }> {
    const response = await http.get('/tts/voices')
    return response.data
  },
}
