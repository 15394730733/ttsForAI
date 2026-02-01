/**
 * Unit tests for history service.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import http from '@/services/http'
import { historyService } from '@/services/history'
import type { HistoryRecord } from '@/services/history'

// Mock the http module
vi.mock('@/services/http', () => ({
  default: {
    get: vi.fn(),
    delete: vi.fn(),
  },
}))

describe('historyService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('getHistory', () => {
    it('fetches history list successfully', async () => {
      const mockRecords: HistoryRecord[] = [
        {
          id: 1,
          task_id: 'task-123',
          text_summary: 'Hello world',
          voice_params: '{"voice_name":"zh-CN-XiaoxiaoNeural"}',
          created_at: '2025-01-27T10:00:00Z',
          file_path: '/path/to/audio.mp3',
          file_size: 1024,
          status: 'completed',
        },
        {
          id: 2,
          task_id: 'task-456',
          text_summary: 'Test text',
          voice_params: '{"voice_name":"zh-CN-YunyangNeural"}',
          created_at: '2025-01-27T11:00:00Z',
          file_path: '/path/to/audio2.mp3',
          file_size: 2048,
          status: 'completed',
        },
      ]

      const mockResponse = {
        records: mockRecords,
        total: 2,
      }

      vi.mocked(http.get).mockResolvedValue({ data: mockResponse } as any)

      const result = await historyService.getHistory(0, 20)

      expect(http.get).toHaveBeenCalledWith('/history?skip=0&limit=20')
      expect(result).toEqual(mockResponse)
    })

    it('fetches history with pagination', async () => {
      const mockResponse = {
        records: [],
        total: 0,
      }

      vi.mocked(http.get).mockResolvedValue({ data: mockResponse } as any)

      await historyService.getHistory(20, 20)

      expect(http.get).toHaveBeenCalledWith('/history?skip=20&limit=20')
    })

    it('handles API errors', async () => {
      const mockError = new Error('Network error') as any
      mockError.response = {
        status: 500,
        data: {
          error: 'Internal Server Error',
          message: 'Failed to fetch history',
        },
      }

      vi.mocked(http.get).mockRejectedValue(mockError)

      try {
        await historyService.getHistory()
        expect(true).toBe(false) // Should not reach here
      } catch (error: any) {
        expect(error).toBeDefined()
      }
    })
  })

  describe('deleteHistory', () => {
    it('deletes history record successfully', async () => {
      vi.mocked(http.delete).mockResolvedValue({ data: {} } as any)

      await historyService.deleteHistory(1)

      expect(http.delete).toHaveBeenCalledWith('/history/1')
    })

    it('handles delete errors', async () => {
      const mockError = new Error('Not found') as any
      mockError.response = {
        status: 404,
        data: {
          error: 'NotFound',
          message: 'History record not found',
        },
      }

      vi.mocked(http.delete).mockRejectedValue(mockError)

      try {
        await historyService.deleteHistory(999)
        expect(true).toBe(false)
      } catch (error: any) {
        expect(error).toBeDefined()
      }
    })
  })

  describe('clearHistory', () => {
    it('clears all history successfully', async () => {
      vi.mocked(http.delete).mockResolvedValue({ data: {} } as any)

      await historyService.clearHistory()

      expect(http.delete).toHaveBeenCalledWith('/history/clear')
    })

    it('handles clear errors', async () => {
      const mockError = new Error('Server error') as any
      mockError.response = {
        status: 500,
        data: {
          error: 'Internal Server Error',
          message: 'Failed to clear history',
        },
      }

      vi.mocked(http.delete).mockRejectedValue(mockError)

      try {
        await historyService.clearHistory()
        expect(true).toBe(false)
      } catch (error: any) {
        expect(error).toBeDefined()
      }
    })
  })

  describe('downloadAudio', () => {
    it('downloads audio successfully', async () => {
      const mockBlob = new Blob(['mock audio data'], { type: 'audio/mpeg' })

      vi.mocked(http.get).mockResolvedValue({ data: mockBlob } as any)

      const result = await historyService.downloadAudio('task-123')

      expect(http.get).toHaveBeenCalledWith('/tts/download/task-123', {
        responseType: 'blob',
      })
      expect(result).toEqual(mockBlob)
    })

    it('handles download errors', async () => {
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
        await historyService.downloadAudio('non-existent')
        expect(true).toBe(false)
      } catch (error: any) {
        expect(error).toBeDefined()
      }
    })
  })

  describe('HistoryRecord type', () => {
    it('has correct structure', () => {
      const record: HistoryRecord = {
        id: 1,
        task_id: 'task-123',
        text_summary: 'Summary',
        voice_params: '{}',
        created_at: '2025-01-27T10:00:00Z',
        file_path: '/path/to/file.mp3',
        file_size: 1024,
        status: 'completed',
      }

      expect(record).toHaveProperty('id')
      expect(record).toHaveProperty('task_id')
      expect(record).toHaveProperty('text_summary')
      expect(record).toHaveProperty('voice_params')
      expect(record).toHaveProperty('created_at')
      expect(record).toHaveProperty('file_path')
      expect(record).toHaveProperty('file_size')
      expect(record).toHaveProperty('status')
    })
  })
})
