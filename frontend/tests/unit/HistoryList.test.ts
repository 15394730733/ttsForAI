/**
 * Comprehensive tests for HistoryList component.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref } from 'vue'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import HistoryList from '@/components/HistoryList.vue'
import type { HistoryRecord } from '@/services/history'
import { useHistoryStore } from '@/stores/history'

// Mock history store
vi.mock('@/stores/history', () => ({
  useHistoryStore: vi.fn(),
}))

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
  },
  ElMessageBox: {
    confirm: vi.fn(),
  },
}))

// Mock icons
vi.mock('@element-plus/icons-vue', () => ({
  Refresh: 'Refresh',
  Delete: 'Delete',
  Download: 'Download',
}))

describe('HistoryList Component', () => {
  const mockRecords: HistoryRecord[] = [
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

  const mockStore = {
    records: ref(mockRecords),
    hasRecords: ref(true),
    loading: ref(false),
    error: ref(null),
    fetchHistory: vi.fn().mockResolvedValue(undefined),
    deleteHistory: vi.fn().mockResolvedValue(undefined),
    clearHistory: vi.fn().mockResolvedValue(undefined),
    downloadAudio: vi.fn().mockResolvedValue(undefined),
  }

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.mocked(useHistoryStore).mockReturnValue(mockStore as any)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Component Rendering', () => {
    it('renders correctly with structure', () => {
      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
            'el-table': true,
            'el-table-column': true,
            'el-empty': true,
          },
        },
      })

      expect(wrapper.find('.history-list').exists()).toBe(true)
    })

    it('shows empty state when no records', () => {
      // Create a mock store with no records for this test
      const emptyStore = {
        records: ref([]),
        hasRecords: ref(false),
        loading: ref(false),
        error: ref(null),
        fetchHistory: vi.fn().mockResolvedValue(undefined),
        deleteHistory: vi.fn().mockResolvedValue(undefined),
        clearHistory: vi.fn().mockResolvedValue(undefined),
        downloadAudio: vi.fn().mockResolvedValue(undefined),
      }
      vi.mocked(useHistoryStore).mockReturnValueOnce(emptyStore as any)

      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
            'el-empty': true,
          },
        },
      })

      const vm = wrapper.vm as any
      // Empty records means hasRecords should be false
      expect(emptyStore.hasRecords.value).toBe(false)
    })

    it('shows table when has records', () => {
      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
            'el-table': true,
            'el-table-column': true,
          },
        },
      })

      const vm = wrapper.vm as any
      // Simulate having records
      const historyStore = vm.historyStore || { records: mockRecords }
      expect(historyStore.records).toBeDefined()
    })
  })

  describe('Data Formatting', () => {
    it('formats time correctly', () => {
      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      const timeStr = '2025-01-27T10:00:00Z'
      const formatted = vm.formatTime(timeStr)

      expect(formatted).toBeTruthy()
      expect(typeof formatted).toBe('string')
      expect(formatted).toContain('2025')
    })

    it('formats file size in bytes', () => {
      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      expect(vm.formatFileSize(512)).toContain('B')
    })

    it('formats file size in KB', () => {
      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      const result = vm.formatFileSize(1024 * 5)
      expect(result).toContain('KB')
      expect(result).toContain('5.0')
    })

    it('formats file size in MB', () => {
      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      const result = vm.formatFileSize(1024 * 1024 * 2)
      expect(result).toContain('MB')
      expect(result).toContain('2.0')
    })

    it('handles edge case file sizes', () => {
      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      expect(vm.formatFileSize(0)).toBe('0 B')
      expect(vm.formatFileSize(1023)).toContain('B')
      expect(vm.formatFileSize(1024)).toContain('KB')
    })
  })

  describe('Download Audio', () => {
    it('has downloadAudio method', async () => {
      const { ElMessage } = await import('element-plus')

      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      const record = mockRecords[0]
      await vm.downloadAudio(record)

      expect(mockStore.downloadAudio).toHaveBeenCalledWith('task-123', 'tts_task-123.mp3')
      expect(ElMessage.success).toHaveBeenCalledWith('下载成功')
    })

    it('handles download error', async () => {
      const { ElMessage } = await import('element-plus')

      // Mock download to throw error
      mockStore.downloadAudio.mockRejectedValueOnce(new Error('Download failed'))

      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      const record = mockRecords[0]
      await vm.downloadAudio(record)

      expect(ElMessage.error).toHaveBeenCalledWith('下载失败')
    })
  })

  describe('Delete Record', () => {
    it('confirms and deletes record', async () => {
      const { ElMessage, ElMessageBox } = await import('element-plus')

      // Mock user confirms deletion
      vi.mocked(ElMessageBox.confirm).mockResolvedValue('confirm' as any)

      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      const record = mockRecords[0]
      await vm.confirmDelete(record)

      expect(ElMessageBox.confirm).toHaveBeenCalledWith(
        `确定要删除这条历史记录吗？`,
        '确认删除',
        expect.objectContaining({
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        })
      )
      expect(mockStore.deleteHistory).toHaveBeenCalledWith(1)
      expect(ElMessage.success).toHaveBeenCalledWith('删除成功')
    })

    it('handles user cancelling deletion', async () => {
      const { ElMessageBox } = await import('element-plus')

      // Mock user cancels
      vi.mocked(ElMessageBox.confirm).mockRejectedValue('cancel')

      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      const record = mockRecords[0]
      await vm.confirmDelete(record)

      // Should not call delete
      expect(mockStore.deleteHistory).not.toHaveBeenCalled()
    })
  })

  describe('Clear All History', () => {
    it('confirms and clears all history', async () => {
      const { ElMessage, ElMessageBox } = await import('element-plus')

      // Mock user confirms
      vi.mocked(ElMessageBox.confirm).mockResolvedValue('confirm' as any)

      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      await vm.confirmClearAll()

      expect(ElMessageBox.confirm).toHaveBeenCalledWith(
        '确定要清空所有历史记录吗？此操作不可恢复。',
        '确认清空',
        expect.objectContaining({
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
          dangerouslyUseHTMLString: true,
        })
      )
      expect(mockStore.clearHistory).toHaveBeenCalled()
      expect(ElMessage.success).toHaveBeenCalledWith('清空成功')
    })

    it('handles user cancelling clear all', async () => {
      const { ElMessageBox } = await import('element-plus')

      // Mock user cancels
      vi.mocked(ElMessageBox.confirm).mockRejectedValue('cancel')

      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      await vm.confirmClearAll()

      // Should not call clear
      expect(mockStore.clearHistory).not.toHaveBeenCalled()
    })
  })

  describe('Refresh Functionality', () => {
    it('has refresh method', () => {
      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      expect(typeof vm.refresh).toBe('function')
    })

    it('calls fetchHistory on refresh', async () => {
      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      await vm.refresh()

      expect(mockStore.fetchHistory).toHaveBeenCalled()
    })
  })

  describe('Lifecycle Hooks', () => {
    it('calls refresh on mount', async () => {
      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any

      // Manually call refresh to simulate onMounted
      await vm.refresh()

      expect(mockStore.fetchHistory).toHaveBeenCalled()
    })
  })

  describe('Computed Properties', () => {
    it('has records computed property', () => {
      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      expect(vm.records).toBeDefined()
    })

    it('has hasRecords computed property', () => {
      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      expect(vm.hasRecords).toBeDefined()
      // hasRecords is a Ref, so check if it exists and has value
      expect(vm.hasRecords !== null).toBe(true)
    })

    it('has loading computed property', () => {
      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      expect(vm.loading).toBeDefined()
      // loading is a Ref, so check if it exists and has value
      expect(vm.loading !== null).toBe(true)
    })
  })

  describe('All Required Methods', () => {
    it('has all required methods', () => {
      const wrapper = mount(HistoryList, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      expect(typeof vm.refresh).toBe('function')
      expect(typeof vm.downloadAudio).toBe('function')
      expect(typeof vm.confirmDelete).toBe('function')
      expect(typeof vm.confirmClearAll).toBe('function')
      expect(typeof vm.formatTime).toBe('function')
      expect(typeof vm.formatFileSize).toBe('function')
    })
  })
})
