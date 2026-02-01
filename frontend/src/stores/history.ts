/**
 * History store.
 *
 * Manages history records and state.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { historyService } from '@/services/history'
import type { HistoryRecord } from '@/services/history'

export const useHistoryStore = defineStore('history', () => {
  const records = ref<HistoryRecord[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const hasRecords = computed(() => records.value.length > 0)

  /**
   * Fetch history records.
   */
  async function fetchHistory(skip = 0, limit = 20) {
    loading.value = true
    error.value = null
    try {
      const response = await historyService.getHistory(skip, limit)
      records.value = response.records
      total.value = response.total
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch history'
      console.error('Error fetching history:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * Delete a history record.
   */
  async function deleteHistory(id: number) {
    loading.value = true
    try {
      await historyService.deleteHistory(id)
      // Remove from local state
      records.value = records.value.filter((r) => r.id !== id)
      total.value -= 1
    } catch (err: any) {
      error.value = err.message || 'Failed to delete history'
      console.error('Error deleting history:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Clear all history.
   */
  async function clearHistory() {
    loading.value = true
    try {
      await historyService.clearHistory()
      records.value = []
      total.value = 0
    } catch (err: any) {
      error.value = err.message || 'Failed to clear history'
      console.error('Error clearing history:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Download audio from history.
   */
  async function downloadAudio(taskId: string, filename: string) {
    try {
      const blob = await historyService.downloadAudio(taskId)

      // Create download link
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Error downloading audio:', err)
      throw err
    }
  }

  return {
    records,
    total,
    loading,
    error,
    hasRecords,
    fetchHistory,
    deleteHistory,
    clearHistory,
    downloadAudio,
  }
})
