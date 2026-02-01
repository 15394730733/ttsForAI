<template>
  <div v-if="message" class="error-message" :class="typeClass">
    <el-alert
      :title="title"
      :description="message"
      :type="alertType"
      :closable="closable"
      @close="handleClose"
      show-icon
    >
      <template v-if="showDetails && details" #default>
        <div class="error-details">
          <el-button text type="info" size="small" @click="toggleDetails">
            {{ detailsVisible ? '隐藏详情' : '查看详情' }}
          </el-button>
          <el-collapse-transition>
            <div v-show="detailsVisible" class="details-content">
              <pre>{{ formatDetails(details) }}</pre>
            </div>
          </el-collapse-transition>
        </div>
      </template>
    </el-alert>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  message?: string
  type?: 'error' | 'warning' | 'info'
  closable?: boolean
  showDetails?: boolean
  details?: Record<string, unknown> | string | null
}

const props = withDefaults(defineProps<Props>(), {
  message: '',
  type: 'error',
  closable: true,
  showDetails: false,
  details: null,
})

const emit = defineEmits<{
  close: []
}>()

const detailsVisible = ref(false)

const alertType = computed(() => {
  const typeMap = {
    error: 'error' as const,
    warning: 'warning' as const,
    info: 'info' as const,
  }
  return typeMap[props.type]
})

const typeClass = computed(() => `error-message--${props.type}`)

const title = computed(() => {
  const titleMap = {
    error: '错误',
    warning: '警告',
    info: '提示',
  }
  return titleMap[props.type]
})

function toggleDetails() {
  detailsVisible.value = !detailsVisible.value
}

function formatDetails(details: Record<string, unknown> | string): string {
  if (typeof details === 'string') {
    return details
  }
  return JSON.stringify(details, null, 2)
}

function handleClose() {
  emit('close')
}
</script>

<style scoped>
.error-message {
  margin: 16px 0;
}

.error-message--error {
  --el-color-error: #f56c6c;
}

.error-message--warning {
  --el-color-warning: #e6a23c;
}

.error-message--info {
  --el-color-info: #909399;
}

.error-details {
  margin-top: 8px;
}

.details-content {
  margin-top: 8px;
  padding: 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
}

.details-content pre {
  margin: 0;
  font-size: 12px;
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
