<template>
  <div class="home-container">
    <el-container>
      <el-header class="app-header">
        <h1>离线文字转语音工具</h1>
        <div class="header-actions">
          <el-button @click="$router.push('/history')">历史记录</el-button>
        </div>
      </el-header>

      <el-main class="app-main">
        <el-row :gutter="20">
          <!-- 左侧：输入和参数 -->
          <el-col :span="16">
            <el-card class="input-section">
              <template #header>
                <span class="card-title">创建 TTS 任务</span>
              </template>

              <!-- 文本输入 -->
              <TTSInput v-model="text" />

              <!-- 文件名设置 -->
              <el-form-item label="文件名（可选）">
                <el-input
                  v-model="customFilename"
                  placeholder="留空则自动使用文本前10个字作为文件名"
                  clearable
                  maxlength="100"
                  show-word-limit
                >
                  <template #append>
                    <el-button @click="generateDefaultFilename">自动生成</el-button>
                  </template>
                </el-input>
              </el-form-item>

              <!-- 语音参数 -->
              <VoiceParams
                v-model:voice-name="voiceName"
                v-model:rate="rate"
                v-model:pitch="pitch"
                v-model:volume="volume"
              />

              <!-- 生成按钮 -->
              <div class="action-buttons">
                <el-button
                  type="primary"
                  size="large"
                  :icon="VideoPlay"
                  :loading="isGenerating"
                  :disabled="!canGenerate"
                  @click="generateAudio"
                >
                  {{ isGenerating ? '生成中...' : '生成语音' }}
                </el-button>

                <el-button
                  v-if="currentTask"
                  size="large"
                  @click="cancelTask"
                >
                  取消任务
                </el-button>
              </div>

              <!-- 当前任务状态 -->
              <div v-if="currentTask" class="current-task-status">
                <el-alert
                  :type="getTaskStatusType(currentTask.status)"
                  :closable="false"
                  show-icon
                >
                  <template #default>
                    <div>
                      <strong>任务状态:</strong> {{ currentTask.status }}
                    </div>
                    <div v-if="currentTask.progress < 100">
                      <el-progress
                        :percentage="currentTask.progress"
                        :status="getProgressStatus(currentTask.status)"
                      />
                    </div>
                  </template>
                </el-alert>
              </div>

              <!-- 生成结果 -->
              <div v-if="generatedAudio" class="result-section">
                <el-divider />
                <h3>生成成功</h3>
                <audio :src="generatedAudio.url" controls style="width: 100%; margin-top: 10px" />
                <div class="download-btn">
                  <el-button
                    type="success"
                    :icon="Download"
                    @click="downloadAudio"
                  >
                    下载音频文件
                  </el-button>
                </div>
              </div>
            </el-card>
          </el-col>

          <!-- 右侧：队列状态 -->
          <el-col :span="8">
            <QueueStatus />
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { VideoPlay, Download } from '@element-plus/icons-vue'
import { ttsService } from '@/services/tts'
import { useQueueStore } from '@/stores/queue'
import TTSInput from '@/components/TTSInput.vue'
import VoiceParams from '@/components/VoiceParams.vue'
import QueueStatus from '@/components/QueueStatus.vue'

const router = useRouter()
const queueStore = useQueueStore()

// Form data
const text = ref('')
const voiceName = ref('zh-CN-XiaoxiaoNeural')
const rate = ref(1.0)
const pitch = ref(1.0)
const volume = ref(1.0)
const customFilename = ref('')

// State
const isGenerating = ref(false)
const currentTask = ref<any>(null)
const generatedAudio = ref<{ url: string; filename: string; taskId: string } | null>(null)

// Computed
const canGenerate = computed(() => {
  return text.value.trim().length > 0 && !isGenerating.value
})

// Poll task status
let taskPollingTimer: number | null = null

// Generate default filename from text
function generateDefaultFilename() {
  if (!text.value.trim()) {
    ElMessage.warning('请先输入文本')
    return
  }
  // Clean text: remove newlines, tabs, and extra spaces
  const cleanText = text.value
    .replace(/[\n\r\t]+/g, ' ')  // Replace newlines/tabs with space
    .replace(/\s+/g, ' ')         // Replace multiple spaces with single space
    .trim()                       // Remove leading/trailing spaces

  // Take first 10 characters
  customFilename.value = cleanText.substring(0, 10)
  ElMessage.success('已自动生成文件名')
}

async function generateAudio() {
  if (!canGenerate.value) return

  isGenerating.value = true
  generatedAudio.value = null

  try {
    // Determine filename: use custom if provided, otherwise use first 10 chars of text
    let filename = customFilename.value.trim()
    if (!filename) {
      // Clean text before generating filename
      const cleanText = text.value
        .replace(/[\n\r\t]+/g, ' ')  // Replace newlines/tabs with space
        .replace(/\s+/g, ' ')         // Replace multiple spaces with single space
        .trim()
      filename = cleanText.substring(0, 10)
    }

    // Log request data for debugging
    const requestData = {
      text: text.value,
      voice_name: voiceName.value,
      rate: rate.value,
      pitch: pitch.value,
      volume: volume.value,
      filename: filename,
    }
    console.log('Creating TTS task with data:', requestData)

    // Create task
    const task = await ttsService.createTask(requestData)

    currentTask.value = task

    // Start polling task status
    startTaskPolling(task.task_id)
  } catch (err: any) {
    console.error('Failed to create task:', err)
    ElMessage.error(err.message || '创建任务失败')
    isGenerating.value = false
  }
}

function startTaskPolling(taskId: string) {
  taskPollingTimer = window.setInterval(async () => {
    try {
      const task = await ttsService.getTask(taskId)
      currentTask.value = task

      if (task.status === 'completed') {
        stopTaskPolling()

        // Use filename from backend, fallback to task_id if not available
        const downloadFilename = task.filename
          ? `${task.filename}.mp3`
          : `tts_${taskId}.mp3`

        generatedAudio.value = {
          url: `/tts/download/${taskId}`,
          filename: downloadFilename,
          taskId: taskId,  // Store taskId for download
        }

        ElMessage.success('语音生成成功！')
        isGenerating.value = false
        currentTask.value = null

        // Reset form
        text.value = ''
      } else if (task.status === 'failed') {
        stopTaskPolling()
        ElMessage.error(task.error_message || '生成失败')
        isGenerating.value = false
        currentTask.value = null
      }
    } catch (err) {
      console.error('Error polling task:', err)
      // Continue polling on error
    }
  }, 2000)
}

function stopTaskPolling() {
  if (taskPollingTimer) {
    clearInterval(taskPollingTimer)
    taskPollingTimer = null
  }
}

async function cancelTask() {
  if (!currentTask.value) return

  try {
    await ttsService.cancelTask(currentTask.value.task_id)
    stopTaskPolling()
    ElMessage.info('任务已取消')
    isGenerating.value = false
    currentTask.value = null
  } catch (err) {
    ElMessage.error('取消任务失败')
  }
}

async function downloadAudio() {
  if (!generatedAudio.value) return

  try {
    const blob = await ttsService.downloadAudio(generatedAudio.value.taskId)
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = generatedAudio.value.filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (err) {
    ElMessage.error('下载失败')
  }
}

function getTaskStatusType(status: string): 'success' | 'warning' | 'info' | 'error' {
  switch (status) {
    case 'completed':
      return 'success'
    case 'failed':
      return 'error'
    case 'processing':
      return 'warning'
    case 'queued':
      return 'info'
    default:
      return 'info'
  }
}

function getProgressStatus(status: string): '' | 'success' | 'exception' | 'warning' {
  switch (status) {
    case 'completed':
      return 'success'
    case 'failed':
      return 'exception'
    default:
      return ''
  }
}

onUnmounted(() => {
  stopTaskPolling()
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: #f0f2f5;
}

.app-header {
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.header-actions {
  display: flex;
  align-items: center;
}

.app-main {
  padding: 20px;
}

.input-section {
  margin-bottom: 20px;
}

.card-title {
  font-size: 18px;
  font-weight: bold;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.action-buttons .el-button {
  flex: 1;
}

.current-task-status {
  margin-top: 20px;
}

.result-section {
  margin-top: 20px;
}

.download-btn {
  margin-top: 10px;
  text-align: center;
}
</style>
