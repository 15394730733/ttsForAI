<template>
  <div class="history-container">
    <el-container>
      <el-header class="app-header">
        <h1>历史记录</h1>
        <div class="header-actions">
          <el-button @click="$router.push('/')">返回主页</el-button>
        </div>
      </el-header>

      <el-main class="app-main">
        <HistoryList />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import HistoryList from '@/components/HistoryList.vue'

const router = useRouter()
</script>

<style scoped>
.history-container {
  min-height: 100vh;
  background: #f0f2f5;
}

.app-header {
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
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
</style>
