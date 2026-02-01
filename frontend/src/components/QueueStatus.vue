<template>
  <div class="queue-status">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>队列状态</span>
          <el-button
            size="small"
            :icon="Refresh"
            @click="refresh"
            :loading="loading"
          >
            刷新
          </el-button>
        </div>
      </template>

      <div v-if="status" class="status-info">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-label">排队中</div>
              <div class="stat-value queued">{{ status.queued_count }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-label">处理中</div>
              <div class="stat-value processing">{{ status.processing_count }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-label">已完成</div>
              <div class="stat-value completed">{{ status.completed_count }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-label">队列容量</div>
              <div class="stat-value">
                {{ status.queued_count }}/{{ status.max_queue_size }}
              </div>
            </div>
          </el-col>
        </el-row>

        <el-alert
          v-if="isFull"
          type="warning"
          :closable="false"
          style="margin-top: 15px"
        >
          队列已满，请等待当前任务完成
        </el-alert>

        <div v-if="status.current_task" class="current-task" style="margin-top: 15px">
          <div class="task-label">当前任务:</div>
          <div class="task-info">
            <div>文本: {{ truncateText(status.current_task.text, 50) }}</div>
            <div class="task-meta">
              状态: {{ status.current_task.status }} |
              进度: {{ status.current_task.progress }}%
            </div>
          </div>
        </div>
      </div>

      <el-empty v-else description="暂无任务" :image-size="80" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { useQueueStore } from '@/stores/queue'

const queueStore = useQueueStore()

const status = computed(() => queueStore.status)
const loading = computed(() => queueStore.loading)
const isFull = computed(() => queueStore.isQueueFull)

function refresh() {
  queueStore.fetchStatus()
}

function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

onMounted(() => {
  queueStore.fetchStatus()
  queueStore.startPolling()
})

onUnmounted(() => {
  queueStore.stopPolling()
})
</script>

<style scoped>
.queue-status {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-info {
  padding: 10px 0;
}

.stat-item {
  text-align: center;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 6px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-value.queued {
  color: #409eff;
}

.stat-value.processing {
  color: #e6a23c;
}

.stat-value.completed {
  color: #67c23a;
}

.current-task {
  padding: 15px;
  background: #fdf6ec;
  border-radius: 6px;
  border-left: 4px solid #e6a23c;
}

.task-label {
  font-weight: bold;
  margin-bottom: 8px;
  color: #606266;
}

.task-info {
  font-size: 14px;
  color: #303133;
}

.task-meta {
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}
</style>
