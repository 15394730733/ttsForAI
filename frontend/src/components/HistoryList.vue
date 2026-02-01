<template>
  <div class="history-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>生成历史</span>
          <div>
            <el-button
              size="small"
              :icon="Refresh"
              @click="refresh"
              :loading="loading"
            >
              刷新
            </el-button>
            <el-button
              size="small"
              :icon="Delete"
              type="danger"
              @click="confirmClearAll"
              :disabled="!hasRecords"
            >
              清空
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="hasRecords" class="history-content">
        <el-table :data="records" style="width: 100%">
          <el-table-column prop="text_summary" label="文本内容" min-width="200">
            <template #default="{ row }">
              <div class="text-cell">{{ row.text_summary }}</div>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="生成时间" width="180">
            <template #default="{ row }">
              {{ formatTime(row.created_at) }}
            </template>
          </el-table-column>

          <el-table-column prop="file_size" label="文件大小" width="100" align="right">
            <template #default="{ row }">
              {{ formatFileSize(row.file_size) }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="180" align="center">
            <template #default="{ row }">
              <el-button
                type="primary"
                size="small"
                :icon="Download"
                @click="downloadAudio(row)"
              >
                下载
              </el-button>
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                @click="confirmDelete(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <el-empty
        v-else
        description="暂无历史记录"
        :image-size="100"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { Refresh, Delete, Download } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useHistoryStore } from '@/stores/history'
import type { HistoryRecord } from '@/services/history'

const historyStore = useHistoryStore()

const records = computed(() => historyStore.records)
const hasRecords = computed(() => historyStore.hasRecords)
const loading = computed(() => historyStore.loading)

async function refresh() {
  await historyStore.fetchHistory()
}

async function downloadAudio(record: HistoryRecord) {
  try {
    // Use filename from record, fallback to task_id if not available
    const filename = record.filename
      ? `${record.filename}.mp3`
      : `tts_${record.task_id}.mp3`
    await historyStore.downloadAudio(record.task_id, filename)
    ElMessage.success('下载成功')
  } catch (err) {
    ElMessage.error('下载失败')
    console.error('Download error:', err)
  }
}

async function confirmDelete(record: HistoryRecord) {
  try {
    await ElMessageBox.confirm(
      `确定要删除这条历史记录吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await historyStore.deleteHistory(record.id)
    ElMessage.success('删除成功')
  } catch {
    // User cancelled
  }
}

async function confirmClearAll() {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有历史记录吗？此操作不可恢复。',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true,
      }
    )

    await historyStore.clearHistory()
    ElMessage.success('清空成功')
  } catch {
    // User cancelled
  }
}

function formatTime(timeStr: string): string {
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

onMounted(() => {
  refresh()
})
</script>

<style scoped>
.history-list {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header > div > * {
  margin-left: 8px;
}

.history-content {
  padding: 10px 0;
}

.text-cell {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
