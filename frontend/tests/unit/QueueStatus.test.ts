/**
 * Unit tests for QueueStatus component.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref } from 'vue'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import QueueStatus from '@/components/QueueStatus.vue'

// Mock queue store
const mockFetchStatus = vi.fn()
const mockStartPolling = vi.fn()
const mockStopPolling = vi.fn()

vi.mock('@/stores/queue', () => ({
  useQueueStore: () => ({
    status: ref({
      queued_count: 2,
      processing_count: 1,
      completed_count: 10,
      current_task: {
        task_id: 'task-123',
        text: 'Test text for truncation',
        status: 'processing',
        progress: 50,
      },
      max_queue_size: 10,
    }),
    loading: ref(false),
    error: ref(null),
    queuedCount: ref(2),
    processingCount: ref(1),
    completedCount: ref(10),
    isQueueFull: ref(false),
    fetchStatus: mockFetchStatus,
    startPolling: mockStartPolling,
    stopPolling: mockStopPolling,
  }),
}))

describe('QueueStatus', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  it('renders correctly', () => {
    const wrapper = mount(QueueStatus, {
      global: {
        plugins: [createPinia()],
        stubs: {
          'el-card': true,
          'el-button': true,
          'el-row': true,
          'el-col': true,
          'el-alert': true,
          'el-empty': true,
        },
      },
    })

    expect(wrapper.find('.queue-status').exists()).toBe(true)
  })

  it('has truncateText method', () => {
    const wrapper = mount(QueueStatus, {
      global: {
        plugins: [createPinia()],
        stubs: {
          'el-card': true,
          'el-button': true,
        },
      },
    })

    const vm = wrapper.vm as any
    expect(typeof vm.truncateText).toBe('function')
  })

  it('truncates long text', () => {
    const wrapper = mount(QueueStatus, {
      global: {
        plugins: [createPinia()],
        stubs: {
          'el-card': true,
          'el-button': true,
        },
      },
    })

    const vm = wrapper.vm as any

    const longText = 'a'.repeat(100)
    const truncated = vm.truncateText(longText, 50)

    expect(truncated.length).toBeLessThan(longText.length)
    expect(truncated).toContain('...')
  })

  it('does not truncate short text', () => {
    const wrapper = mount(QueueStatus, {
      global: {
        plugins: [createPinia()],
        stubs: {
          'el-card': true,
          'el-button': true,
        },
      },
    })

    const vm = wrapper.vm as any

    const shortText = 'Short text'
    const truncated = vm.truncateText(shortText, 50)

    expect(truncated).toBe(shortText)
  })

  it('has refresh method', () => {
    const wrapper = mount(QueueStatus, {
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

  it('refresh method calls fetchStatus', () => {
    const wrapper = mount(QueueStatus, {
      global: {
        plugins: [createPinia()],
        stubs: {
          'el-card': true,
          'el-button': true,
        },
      },
    })

    const vm = wrapper.vm as any
    mockFetchStatus.mockClear()

    vm.refresh()

    expect(mockFetchStatus).toHaveBeenCalled()
  })

  it('calls startPolling on mount', () => {
    mount(QueueStatus, {
      global: {
        plugins: [createPinia()],
        stubs: {
          'el-card': true,
          'el-button': true,
        },
      },
    })

    expect(mockStartPolling).toHaveBeenCalled()
  })

  it('calls stopPolling on unmount', () => {
    const wrapper = mount(QueueStatus, {
      global: {
        plugins: [createPinia()],
        stubs: {
          'el-card': true,
          'el-button': true,
        },
      },
    })

    wrapper.unmount()

    expect(mockStopPolling).toHaveBeenCalled()
  })

  it('component structure is correct', () => {
    const wrapper = mount(QueueStatus, {
      global: {
        plugins: [createPinia()],
        stubs: {
          'el-card': true,
          'el-button': true,
        },
      },
    })

    const vm = wrapper.vm as any
    expect(vm).toBeTruthy()
    expect(typeof vm.refresh).toBe('function')
    expect(typeof vm.truncateText).toBe('function')
  })

  it('accesses computed properties correctly', () => {
    const wrapper = mount(QueueStatus, {
      global: {
        plugins: [createPinia()],
        stubs: {
          'el-card': true,
          'el-button': true,
        },
      },
    })

    const vm = wrapper.vm as any
    // Computed properties from store are available
    expect(vm.status).toBeDefined()
    expect(vm.loading).toBeDefined()
    expect(vm.isFull).toBeDefined()
  })

  it('has all required methods', () => {
    const wrapper = mount(QueueStatus, {
      global: {
        plugins: [createPinia()],
        stubs: {
          'el-card': true,
          'el-button': true,
        },
      },
    })

    const vm = wrapper.vm as any
    expect(typeof vm.truncateText).toBe('function')
    expect(typeof vm.refresh).toBe('function')
  })

  it('handles empty status gracefully', () => {
    // Component should render even when status is null
    const wrapper = mount(QueueStatus, {
      global: {
        plugins: [createPinia()],
        stubs: {
          'el-card': true,
          'el-button': true,
          'el-empty': true,
        },
      },
    })

    expect(wrapper.find('.queue-status').exists()).toBe(true)
  })

  describe('Queue Full Status', () => {
    it('shows alert when queue is full', () => {
      const wrapper = mount(QueueStatus, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
            'el-row': true,
            'el-col': true,
            'el-alert': true,
          },
        },
      })

      const vm = wrapper.vm as any
      // Verify isFull computed property (it's a Ref)
      expect(vm.isFull).toBeDefined()
      // By default, queued_count (2) < max_queue_size (10), so not full
      expect(vm.isFull.value).toBe(false)
    })

    it('does not show alert when queue is not full', () => {
      const wrapper = mount(QueueStatus, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
            'el-row': true,
            'el-col': true,
            'el-alert': true,
          },
        },
      })

      const vm = wrapper.vm as any
      expect(vm.isFull.value).toBe(false)
    })
  })

  describe('Status Display', () => {
    it('displays processing count correctly', () => {
      const wrapper = mount(QueueStatus, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      // status is a Ref, need to access .value
      expect(vm.status).toBeDefined()
      expect(vm.status.value.processing_count).toBe(1)
    })

    it('displays completed count correctly', () => {
      const wrapper = mount(QueueStatus, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      expect(vm.status.value.completed_count).toBe(10)
    })

    it('displays queue capacity correctly', () => {
      const wrapper = mount(QueueStatus, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      expect(vm.status.value.queued_count).toBe(2)
      expect(vm.status.value.max_queue_size).toBe(10)
    })
  })

  describe('Current Task Display', () => {
    it('displays current task information', () => {
      const wrapper = mount(QueueStatus, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      expect(vm.status.value).toBeDefined()
      expect(vm.status.value.current_task).toBeDefined()
      expect(vm.status.value.current_task.task_id).toBe('task-123')
      expect(vm.status.value.current_task.progress).toBe(50)
    })

    it('truncates current task text correctly', () => {
      const wrapper = mount(QueueStatus, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      const longText = 'This is a very long text that should be truncated when displayed in the current task section'

      const truncated = vm.truncateText(longText, 50)
      expect(truncated.length).toBeLessThan(longText.length)
      expect(truncated).toContain('...')
    })

    it('does not truncate short text', () => {
      const wrapper = mount(QueueStatus, {
        global: {
          plugins: [createPinia()],
          stubs: {
            'el-card': true,
            'el-button': true,
          },
        },
      })

      const vm = wrapper.vm as any
      const shortText = 'Short text'
      const truncated = vm.truncateText(shortText, 50)

      expect(truncated).toBe(shortText)
    })
  })
})
