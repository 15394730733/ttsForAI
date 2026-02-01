/**
 * Unit tests for History store.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useHistoryStore } from '@/stores/history'
import { historyService } from '@/services/history'

// Mock history service
vi.mock('@/services/history', () => ({
  historyService: {
    getHistory: vi.fn(),
    deleteHistory: vi.fn(),
    clearHistory: vi.fn(),
    downloadAudio: vi.fn(),
  },
}))

// Mock document methods for download
global.document.createElement = vi.fn(() => ({
  href: '',
  download: '',
  click: vi.fn(),
})) as any

global.document.body.appendChild = vi.fn() as any
global.document.body.removeChild = vi.fn() as any
global.URL.createObjectURL = vi.fn(() => 'mock-url') as any
global.URL.revokeObjectURL = vi.fn() as any

describe('History Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('State Initialization', () => {
    it('initializes with empty state', () => {
      const store = useHistoryStore()

      expect(store.records).toEqual([])
      expect(store.total).toBe(0)
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
      expect(store.hasRecords).toBe(false)
    })

    it('hasRecords computed property works correctly', () => {
      const store = useHistoryStore()

      expect(store.hasRecords).toBe(false)

      // Add a record
      store.records = [{
        id: 1,
        task_id: 'task-123',
        text_summary: 'Test',
        voice_params: '{}',
        created_at: '2025-01-27T10:00:00Z',
        file_path: '/path/to/file.mp3',
        file_size: 1024,
        status: 'completed',
      }]

      expect(store.hasRecords).toBe(true)
    })
  })

  describe('fetchHistory', () => {
    it('fetches history records successfully', async () => {
      const mockRecords = [
        {
          id: 1,
          task_id: 'task-123',
          text_summary: 'Hello world',
          voice_params: '{}',
          created_at: '2025-01-27T10:00:00Z',
          file_path: '/path/to/file.mp3',
          file_size: 1024,
          status: 'completed',
        },
        {
          id: 2,
          task_id: 'task-456',
          text_summary: 'Test text',
          voice_params: '{}',
          created_at: '2025-01-27T11:00:00Z',
          file_path: '/path/to/file2.mp3',
          file_size: 2048,
          status: 'completed',
        },
      ]

      vi.mocked(historyService.getHistory).mockResolvedValue({
        records: mockRecords,
        total: 2,
      })

      const store = useHistoryStore()
      await store.fetchHistory(0, 20)

      expect(historyService.getHistory).toHaveBeenCalledWith(0, 20)
      expect(store.records).toEqual(mockRecords)
      expect(store.total).toBe(2)
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
    })

    it('sets loading state during fetch', async () => {
      vi.mocked(historyService.getHistory).mockImplementation(
        () => new Promise((resolve) => {
          setTimeout(() => resolve({ records: [], total: 0 }), 100)
        })
      )

      const store = useHistoryStore()
      const fetchPromise = store.fetchHistory()

      expect(store.loading).toBe(true)

      await fetchPromise

      expect(store.loading).toBe(false)
    })

    it('handles fetch errors correctly', async () => {
      const mockError = new Error('Network error')
      vi.mocked(historyService.getHistory).mockRejectedValue(mockError)

      const store = useHistoryStore()
      await store.fetchHistory()

      expect(store.error).toBe('Network error')
      expect(store.records).toEqual([])
      expect(store.loading).toBe(false)
    })

    it('uses default pagination parameters', async () => {
      vi.mocked(historyService.getHistory).mockResolvedValue({
        records: [],
        total: 0,
      })

      const store = useHistoryStore()
      await store.fetchHistory()

      expect(historyService.getHistory).toHaveBeenCalledWith(0, 20)
    })

    it('accepts custom pagination parameters', async () => {
      vi.mocked(historyService.getHistory).mockResolvedValue({
        records: [],
        total: 0,
      })

      const store = useHistoryStore()
      await store.fetchHistory(20, 10)

      expect(historyService.getHistory).toHaveBeenCalledWith(20, 10)
    })
  })

  describe('deleteHistory', () => {
    it('deletes history record successfully', async () => {
      const mockRecords = [
        {
          id: 1,
          task_id: 'task-123',
          text_summary: 'Test',
          voice_params: '{}',
          created_at: '2025-01-27T10:00:00Z',
          file_path: '/path/to/file.mp3',
          file_size: 1024,
          status: 'completed',
        },
        {
          id: 2,
          task_id: 'task-456',
          text_summary: 'Test 2',
          voice_params: '{}',
          created_at: '2025-01-27T11:00:00Z',
          file_path: '/path/to/file2.mp3',
          file_size: 2048,
          status: 'completed',
        },
      ]

      vi.mocked(historyService.deleteHistory).mockResolvedValue(undefined)

      const store = useHistoryStore()
      store.records = mockRecords
      store.total = 2

      await store.deleteHistory(1)

      expect(historyService.deleteHistory).toHaveBeenCalledWith(1)
      expect(store.records).toEqual([mockRecords[1]])
      expect(store.total).toBe(1)
      expect(store.loading).toBe(false)
    })

    it('sets loading state during delete', async () => {
      vi.mocked(historyService.deleteHistory).mockImplementation(
        () => new Promise((resolve) => {
          setTimeout(() => resolve(undefined), 100)
        })
      )

      const store = useHistoryStore()
      const deletePromise = store.deleteHistory(1)

      expect(store.loading).toBe(true)

      await deletePromise

      expect(store.loading).toBe(false)
    })

    it('handles delete errors correctly', async () => {
      const mockError = new Error('Delete failed')
      vi.mocked(historyService.deleteHistory).mockRejectedValue(mockError)

      const store = useHistoryStore()
      store.records = [
        {
          id: 1,
          task_id: 'task-123',
          text_summary: 'Test',
          voice_params: '{}',
          created_at: '2025-01-27T10:00:00Z',
          file_path: '/path/to/file.mp3',
          file_size: 1024,
          status: 'completed',
        },
      ]

      await expect(store.deleteHistory(1)).rejects.toThrow('Delete failed')
      expect(store.error).toBe('Delete failed')
      expect(store.loading).toBe(false)
    })

    it('throws error on failure', async () => {
      vi.mocked(historyService.deleteHistory).mockRejectedValue(new Error('Not found'))

      const store = useHistoryStore()

      await expect(store.deleteHistory(999)).rejects.toThrow()
    })
  })

  describe('clearHistory', () => {
    it('clears all history successfully', async () => {
      const mockRecords = [
        {
          id: 1,
          task_id: 'task-123',
          text_summary: 'Test',
          voice_params: '{}',
          created_at: '2025-01-27T10:00:00Z',
          file_path: '/path/to/file.mp3',
          file_size: 1024,
          status: 'completed',
        },
      ]

      vi.mocked(historyService.clearHistory).mockResolvedValue(undefined)

      const store = useHistoryStore()
      store.records = mockRecords
      store.total = 1

      await store.clearHistory()

      expect(historyService.clearHistory).toHaveBeenCalled()
      expect(store.records).toEqual([])
      expect(store.total).toBe(0)
      expect(store.loading).toBe(false)
    })

    it('sets loading state during clear', async () => {
      vi.mocked(historyService.clearHistory).mockImplementation(
        () => new Promise((resolve) => {
          setTimeout(() => resolve(undefined), 100)
        })
      )

      const store = useHistoryStore()
      const clearPromise = store.clearHistory()

      expect(store.loading).toBe(true)

      await clearPromise

      expect(store.loading).toBe(false)
    })

    it('handles clear errors correctly', async () => {
      const mockError = new Error('Clear failed')
      vi.mocked(historyService.clearHistory).mockRejectedValue(mockError)

      const store = useHistoryStore()
      store.records = [
        {
          id: 1,
          task_id: 'task-123',
          text_summary: 'Test',
          voice_params: '{}',
          created_at: '2025-01-27T10:00:00Z',
          file_path: '/path/to/file.mp3',
          file_size: 1024,
          status: 'completed',
        },
      ]

      await expect(store.clearHistory()).rejects.toThrow('Clear failed')
      expect(store.error).toBe('Clear failed')
      expect(store.loading).toBe(false)
    })

    it('throws error on failure', async () => {
      vi.mocked(historyService.clearHistory).mockRejectedValue(new Error('Server error'))

      const store = useHistoryStore()

      await expect(store.clearHistory()).rejects.toThrow()
    })
  })

  describe('downloadAudio', () => {
    it('downloads audio successfully', async () => {
      const mockBlob = new Blob(['mock audio data'], { type: 'audio/mpeg' })
      vi.mocked(historyService.downloadAudio).mockResolvedValue(mockBlob)

      const store = useHistoryStore()
      await store.downloadAudio('task-123', 'audio.mp3')

      // historyService.downloadAudio only takes taskId parameter
      expect(historyService.downloadAudio).toHaveBeenCalledWith('task-123')
    })

    it('handles download errors', async () => {
      const mockError = new Error('Download failed')
      vi.mocked(historyService.downloadAudio).mockRejectedValue(mockError)

      const store = useHistoryStore()

      await expect(store.downloadAudio('task-123', 'audio.mp3')).rejects.toThrow()
      expect(store.error).toBeDefined()
    })
  })

  describe('Computed Properties', () => {
    it('hasRecords returns false when empty', () => {
      const store = useHistoryStore()

      expect(store.hasRecords).toBe(false)
    })

    it('hasRecords returns true when has records', () => {
      const store = useHistoryStore()
      store.records = [
        {
          id: 1,
          task_id: 'task-123',
          text_summary: 'Test',
          voice_params: '{}',
          created_at: '2025-01-27T10:00:00Z',
          file_path: '/path/to/file.mp3',
          file_size: 1024,
          status: 'completed',
        },
      ]

      expect(store.hasRecords).toBe(true)
    })

    it('hasRecords updates reactively', () => {
      const store = useHistoryStore()

      expect(store.hasRecords).toBe(false)

      store.records = [
        {
          id: 1,
          task_id: 'task-123',
          text_summary: 'Test',
          voice_params: '{}',
          created_at: '2025-01-27T10:00:00Z',
          file_path: '/path/to/file.mp3',
          file_size: 1024,
          status: 'completed',
        },
      ]

      expect(store.hasRecords).toBe(true)

      store.records = []

      expect(store.hasRecords).toBe(false)
    })
  })

  describe('Error Handling', () => {
    it('sets error on fetch failure', async () => {
      const mockError = new Error('Fetch failed')
      vi.mocked(historyService.getHistory).mockRejectedValue(mockError)

      const store = useHistoryStore()
      await store.fetchHistory()

      expect(store.error).toBe('Fetch failed')
    })

    it('sets error on delete failure', async () => {
      vi.mocked(historyService.deleteHistory).mockRejectedValue(new Error('Delete failed'))

      const store = useHistoryStore()
      store.records = [
        {
          id: 1,
          task_id: 'task-123',
          text_summary: 'Test',
          voice_params: '{}',
          created_at: '2025-01-27T10:00:00Z',
          file_path: '/path/to/file.mp3',
          file_size: 1024,
          status: 'completed',
        },
      ]

      await expect(store.deleteHistory(1)).rejects.toThrow('Delete failed')
      expect(store.error).toBe('Delete failed')
    })

    it('sets error on clear failure', async () => {
      vi.mocked(historyService.clearHistory).mockRejectedValue(new Error('Clear failed'))

      const store = useHistoryStore()

      await expect(store.clearHistory()).rejects.toThrow('Clear failed')
      expect(store.error).toBe('Clear failed')
    })
  })

  describe('State Updates', () => {
    it('updates records correctly after fetch', async () => {
      const mockRecords = [
        {
          id: 1,
          task_id: 'task-123',
          text_summary: 'Test',
          voice_params: '{}',
          created_at: '2025-01-27T10:00:00Z',
          file_path: '/path/to/file.mp3',
          file_size: 1024,
          status: 'completed',
        },
      ]

      vi.mocked(historyService.getHistory).mockResolvedValue({
        records: mockRecords,
        total: 1,
      })

      const store = useHistoryStore()
      await store.fetchHistory()

      expect(store.records.length).toBe(1)
      expect(store.records[0]).toEqual(mockRecords[0])
    })

    it('updates total count correctly', async () => {
      vi.mocked(historyService.getHistory).mockResolvedValue({
        records: [],
        total: 42,
      })

      const store = useHistoryStore()
      await store.fetchHistory()

      expect(store.total).toBe(42)
    })

    it('removes deleted record from state', async () => {
      const mockRecords = [
        {
          id: 1,
          task_id: 'task-1',
          text_summary: 'First',
          voice_params: '{}',
          created_at: '2025-01-27T10:00:00Z',
          file_path: '/file1.mp3',
          file_size: 1024,
          status: 'completed',
        },
        {
          id: 2,
          task_id: 'task-2',
          text_summary: 'Second',
          voice_params: '{}',
          created_at: '2025-01-27T11:00:00Z',
          file_path: '/file2.mp3',
          file_size: 2048,
          status: 'completed',
        },
      ]

      vi.mocked(historyService.deleteHistory).mockResolvedValue(undefined)

      const store = useHistoryStore()
      store.records = mockRecords
      store.total = 2

      await store.deleteHistory(1)

      expect(store.records.length).toBe(1)
      expect(store.records[0].id).toBe(2)
      expect(store.total).toBe(1)
    })

    it('clears all records on clear', async () => {
      const mockRecords = [
        {
          id: 1,
          task_id: 'task-1',
          text_summary: 'Test',
          voice_params: '{}',
          created_at: '2025-01-27T10:00:00Z',
          file_path: '/file.mp3',
          file_size: 1024,
          status: 'completed',
        },
      ]

      vi.mocked(historyService.clearHistory).mockResolvedValue(undefined)

      const store = useHistoryStore()
      store.records = mockRecords
      store.total = 1

      await store.clearHistory()

      expect(store.records).toEqual([])
      expect(store.total).toBe(0)
    })
  })
})
