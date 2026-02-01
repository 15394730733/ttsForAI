<template>
  <div class="tts-input">
    <el-form :model="formData" label-position="top">
      <el-form-item label="输入文本">
        <el-input
          v-model="formData.text"
          type="textarea"
          :rows="8"
          :maxlength="5000"
          show-word-limit
          placeholder="请输入要转换为语音的文字内容（1-5000字符）"
          clearable
        />
      </el-form-item>

      <div class="char-count">
        <span :class="{ 'error': !isValidLength }">
          {{ formData.text.length }} / 5000 字符
        </span>
      </div>

      <el-alert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        :closable="false"
        show-icon
        style="margin-top: 10px"
      />
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Props {
  modelValue: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formData = ref({
  text: props.modelValue,
})

const errorMessage = computed(() => {
  if (!formData.value.text) return ''
  if (formData.value.text.length > 5000) return '文本长度不能超过5000字符'
  return ''
})

const isValidLength = computed(() => {
  const len = formData.value.text.length
  return len > 0 && len <= 5000
})

// Watch for changes and emit
watch(
  () => formData.value.text,
  (newValue) => {
    emit('update:modelValue', newValue)
  }
)

// Watch for external changes
watch(
  () => props.modelValue,
  (newValue) => {
    formData.value.text = newValue
  }
)
</script>

<style scoped>
.tts-input {
  width: 100%;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.char-count .error {
  color: #f56c6c;
}
</style>
