/**
 * Unit tests for TTS service.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ttsService } from '@/services/tts'
import http from '@/services/http'
import type { TaskCreateRequest, TaskResponse } from '@/types/api'

// Mock the http module
vi.mock('@/services/http', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    delete: vi.fn(),
  },
}))

describe('ttsService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('createTask', () => {
    it('creates a new TTS task successfully', async () => {
      const mockRequest: TaskCreateRequest = {
        text: 'Hello world',
        voice_name: 'zh-CN-XiaoxiaoNeural',
        rate: 1.0,
        pitch: 1.0,
        volume: 1.0,
      }

      const mockResponse: TaskResponse = {
        task_id: 'task-123',
        text: 'Hello world',
        voice_name: 'zh-CN-XiaoxiaoNeural',
        rate: 1.0,
        pitch: 1.0,
        volume: 1.0,
        status: 'queued' as any,
        progress: 0,
        file_path: null,
        error_message: null,
        created_at: '2025-01-27T10:00:00Z',
        started_at: null,
        completed_at: null,
      }

      vi.mocked(http.post).mockResolvedValue({ data: mockResponse } as any)

      const result = await ttsService.createTask(mockRequest)

      expect(http.post).toHaveBeenCalledWith('/tts/generate', mockRequest)
      expect(result).toEqual(mockResponse)
    })

    it('handles API errors', async () => {
      const mockRequest: TaskCreateRequest = {
        text: 'Hello',
      }

      const mockError = new Error('Request failed') as any
      mockError.response = {
        status: 422,
        data: {
          error: 'ValidationError',
          message: 'Text too short',
          details: {},
        },
      }

      vi.mocked(http.post).mockRejectedValue(mockError)

      try {
        await ttsService.createTask(mockRequest)
        expect(true).toBe(false) // Should not reach here
      } catch (error: any) {
        expect(error).toBeDefined()
        expect(error.message).toBeDefined()
      }
    })

    it('sends request with minimal required fields', async () => {
      const mockRequest: TaskCreateRequest = {
        text: 'Test text',
      }

      const mockResponse: TaskResponse = {
        task_id: 'task-456',
        text: 'Test text',
        voice_name: 'zh-CN-XiaoxiaoNeural',
        rate: 1.0,
        pitch: 1.0,
        volume: 1.0,
        status: 'queued' as any,
        progress: 0,
        file_path: null,
        error_message: null,
        created_at: '2025-01-27T10:00:00Z',
        started_at: null,
        completed_at: null,
      }

      vi.mocked(http.post).mockResolvedValue({ data: mockResponse } as any)

      await ttsService.createTask(mockRequest)

      expect(http.post).toHaveBeenCalledWith('/tts/generate', mockRequest)
    })
  })

  describe('getTask', () => {
    it('retrieves task status by ID', async () => {
      const taskId = 'task-123'

      const mockResponse: TaskResponse = {
        task_id: taskId,
        text: 'Hello world',
        voice_name: 'zh-CN-XiaoxiaoNeural',
        rate: 1.0,
        pitch: 1.0,
        volume: 1.0,
        status: 'processing' as any,
        progress: 50,
        file_path: null,
        error_message: null,
        created_at: '2025-01-27T10:00:00Z',
        started_at: '2025-01-27T10:01:00Z',
        completed_at: null,
      }

      vi.mocked(http.get).mockResolvedValue({ data: mockResponse } as any)

      const result = await ttsService.getTask(taskId)

      expect(http.get).toHaveBeenCalledWith(`/tts/tasks/${taskId}`)
      expect(result).toEqual(mockResponse)
    })

    it('handles task not found error', async () => {
      const taskId = 'non-existent-task'

      const mockError = new Error('Not found') as any
      mockError.response = {
        status: 404,
        data: {
          error: 'NotFound',
          message: 'Task not found',
        },
      }

      vi.mocked(http.get).mockRejectedValue(mockError)

      try {
        await ttsService.getTask(taskId)
        expect(true).toBe(false) // Should not reach here
      } catch (error: any) {
        expect(error).toBeDefined()
      }
    })
  })

  describe('cancelTask', () => {
    it('cancels a queued task successfully', async () => {
      const taskId = 'task-123'

      const mockResponse = {
        task_id: taskId,
        status: 'cancelled',
      }

      vi.mocked(http.delete).mockResolvedValue({ data: mockResponse } as any)

      const result = await ttsService.cancelTask(taskId)

      expect(http.delete).toHaveBeenCalledWith(`/tts/tasks/${taskId}`)
      expect(result).toEqual(mockResponse)
    })

    it('handles cancellation of already completed task', async () => {
      const taskId = 'task-123'

      const mockError = new Error('Invalid state') as any
      mockError.response = {
        status: 400,
        data: {
          error: 'InvalidState',
          message: 'Cannot cancel completed task',
        },
      }

      vi.mocked(http.delete).mockRejectedValue(mockError)

      try {
        await ttsService.cancelTask(taskId)
        expect(true).toBe(false) // Should not reach here
      } catch (error: any) {
        expect(error).toBeDefined()
      }
    })
  })

  describe('downloadAudio', () => {
    it('downloads audio file successfully', async () => {
      const taskId = 'task-123'

      const mockBlob = new Blob(['mock audio data'], { type: 'audio/mpeg' })

      vi.mocked(http.get).mockResolvedValue({ data: mockBlob } as any)

      const result = await ttsService.downloadAudio(taskId)

      expect(http.get).toHaveBeenCalledWith(`/tts/download/${taskId}`, {
        responseType: 'blob',
      })
      expect(result).toEqual(mockBlob)
    })

    it('handles download error', async () => {
      const taskId = 'task-123'

      const mockError = new Error('Not found') as any
      mockError.response = {
        status: 404,
        data: {
          error: 'NotFound',
          message: 'Audio file not found',
        },
      }

      vi.mocked(http.get).mockRejectedValue(mockError)

      try {
        await ttsService.downloadAudio(taskId)
        expect(true).toBe(false) // Should not reach here
      } catch (error: any) {
        expect(error).toBeDefined()
      }
    })
  })

  describe('getVoices', () => {
    it('returns list of available voices', async () => {
      // Mock http.get to return voice list
      const mockVoicesResponse = {
        voices: [
          {
            name: '晓晓-女声',
            voice_id: 'zh-CN-XiaoxiaoNeural',
            description: '默认女声',
            default: true,
          },
          {
            name: '云扬-男声',
            voice_id: 'zh-CN-YunyangNeural',
            description: '男声',
            default: false,
          },
          {
            name: '晓悠-童声',
            voice_id: 'zh-CN-XiaoyouNeural',
            description: '童声',
            default: false,
          },
          {
            name: '晓伊-年轻女声',
            voice_id: 'zh-CN-XiaoyiNeural',
            description: '年轻女声',
            default: false,
          },
          {
            name: '云健-沉稳男声',
            voice_id: 'zh-CN-YunjianNeural',
            description: '沉稳男声',
            default: false,
          },
        ],
      }

      vi.mocked(http.get).mockResolvedValueOnce({ data: mockVoicesResponse } as any)

      const result = await ttsService.getVoices()

      expect(result).toEqual(mockVoicesResponse)
      expect(http.get).toHaveBeenCalledWith('/tts/voices')
    })

    it('returns consistent voice list structure', async () => {
      // Mock http.get
      const mockVoicesResponse = {
        voices: [
          {
            name: '晓晓-女声',
            voice_id: 'zh-CN-XiaoxiaoNeural',
            description: '默认女声',
            default: true,
          },
        ],
      }

      vi.mocked(http.get).mockResolvedValueOnce({ data: mockVoicesResponse } as any)

      const result = await ttsService.getVoices()

      expect(result.voices).toBeInstanceOf(Array)
      expect(result.voices.length).toBeGreaterThan(0)

      result.voices.forEach((voice) => {
        expect(voice).toHaveProperty('name')
        expect(voice).toHaveProperty('voice_id')
        expect(voice).toHaveProperty('description')
        expect(voice).toHaveProperty('default')
        expect(typeof voice.name).toBe('string')
        expect(typeof voice.voice_id).toBe('string')
        expect(typeof voice.description).toBe('string')
        expect(typeof voice.default).toBe('boolean')
      })
    })
  })
})
