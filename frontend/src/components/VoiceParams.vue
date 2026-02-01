<template>
  <div class="voice-params">
    <el-form :model="formData" label-width="100px">
      <!-- 音色选择 -->
      <el-form-item label="选择音色">
        <el-select
          v-model="formData.voice_name"
          placeholder="请选择音色"
          style="width: 100%"
        >
          <el-option
            v-for="voice in voices"
            :key="voice.voice_id"
            :label="voice.name"
            :value="voice.voice_id"
          >
            <span>{{ voice.name }}</span>
            <span style="color: #909399; font-size: 12px; margin-left: 10px">
              {{ voice.description }}
            </span>
          </el-option>
        </el-select>
      </el-form-item>

      <!-- 语速 -->
      <el-form-item label="语速">
        <el-slider
          v-model="formData.rate"
          :min="0.5"
          :max="2.0"
          :step="0.1"
          :show-stops="true"
          :marks="rateMarks"
        />
        <div class="param-value">
          {{ formData.rate.toFixed(1) }}x
        </div>
      </el-form-item>

      <!-- 音调 -->
      <el-form-item label="音调">
        <el-slider
          v-model="formData.pitch"
          :min="0.5"
          :max="2.0"
          :step="0.1"
          :show-stops="true"
          :marks="pitchMarks"
        />
        <div class="param-value">
          {{ formData.pitch.toFixed(1) }}x
        </div>
      </el-form-item>

      <!-- 音量 -->
      <el-form-item label="音量">
        <el-slider
          v-model="formData.volume"
          :min="0.0"
          :max="1.0"
          :step="0.1"
          :show-stops="true"
          :marks="volumeMarks"
        />
        <div class="param-value">
          {{ Math.round(formData.volume * 100) }}%
        </div>
      </el-form-item>

      <!-- 重置按钮 -->
      <div class="reset-btn">
        <el-button @click="resetParams" :icon="RefreshLeft">
          重置参数
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { RefreshLeft } from '@element-plus/icons-vue'
import { ttsService } from '@/services/tts'

interface Props {
  voiceName?: string
  rate?: number
  pitch?: number
  volume?: number
}

interface Emits {
  (e: 'update:voiceName', value: string): void
  (e: 'update:rate', value: number): void
  (e: 'update:pitch', value: number): void
  (e: 'update:volume', value: number): void
}

const props = withDefaults(defineProps<Props>(), {
  voiceName: 'zh-CN-XiaoxiaoNeural',
  rate: 1.0,
  pitch: 1.0,
  volume: 1.0,
})

const emit = defineEmits<Emits>()

const formData = ref({
  voice_name: props.voiceName,
  rate: props.rate,
  pitch: props.pitch,
  volume: props.volume,
})

const voices = ref<Array<{ name: string; voice_id: string; description: string }>>([])

// Slider marks
const rateMarks = {
  0.5: '0.5x',
  1.0: '1.0x',
  1.5: '1.5x',
  2.0: '2.0x',
}

const pitchMarks = {
  0.5: '低',
  1.0: '正常',
  1.5: '高',
  2.0: '最高',
}

const volumeMarks = {
  0.0: '静音',
  0.5: '50%',
  1.0: '100%',
}

// Load voices
async function loadVoices() {
  try {
    const response = await ttsService.getVoices()
    voices.value = response.voices
  } catch (err) {
    console.error('Failed to load voices:', err)
  }
}

// Reset to defaults
function resetParams() {
  formData.value = {
    voice_name: 'zh-CN-XiaoxiaoNeural',
    rate: 1.0,
    pitch: 1.0,
    volume: 1.0,
  }
  emitChange()
}

// Emit changes
function emitChange() {
  emit('update:voiceName', formData.value.voice_name)
  emit('update:rate', formData.value.rate)
  emit('update:pitch', formData.value.pitch)
  emit('update:volume', formData.value.volume)
}

// Watch for changes
watch(
  () => formData.value,
  () => {
    emitChange()
  },
  { deep: true }
)

// Load voices on mount
loadVoices()
</script>

<style scoped>
.voice-params {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.param-value {
  text-align: right;
  font-size: 12px;
  color: #606266;
  margin-top: 5px;
}

.reset-btn {
  margin-top: 10px;
  text-align: center;
}
</style>
