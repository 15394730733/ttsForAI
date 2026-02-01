/**
 * Queue status store.
 *
 * Manages queue status polling and state.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { queueService } from '@/services/queue'
import type { QueueStatus } from '@/services/queue'

export const useQueueStore = defineStore('queue', () => {
  const status = ref<QueueStatus | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  let pollingTimer: number | null = null

  // Computed
  const queuedCount = computed(() => status.value?.queued_count ?? 0)
  const processingCount = computed(() => status.value?.processing_count ?? 0)
  const completedCount = computed(() => status.value?.completed_count ?? 0)
  const isQueueFull = computed(() => {
    if (!status.value) return false
    return status.value.queued_count >= status.value.max_queue_size
  })

  /**
   * Fetch queue status.
   */
  async function fetchStatus() {
    loading.value = true
    error.value = null
    try {
      status.value = await queueService.getStatus()
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch queue status'
      console.error('Error fetching queue status:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * Start polling queue status every 2 seconds.
   */
  function startPolling() {
    fetchStatus()
    pollingTimer = window.setInterval(() => {
      fetchStatus()
    }, 2000)
  }

  /**
   * Stop polling queue status.
   */
  function stopPolling() {
    if (pollingTimer) {
      clearInterval(pollingTimer)
      pollingTimer = null
    }
  }

  return {
    status,
    loading,
    error,
    queuedCount,
    processingCount,
    completedCount,
    isQueueFull,
    fetchStatus,
    startPolling,
    stopPolling,
  }
})
