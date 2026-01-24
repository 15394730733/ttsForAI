# API使用指南

**Feature**: 离线文字转语音工具 (001-offline-tts)
**API Version**: v1.0.0
**Base URL**: `http://localhost:8000/api/v1`

## 目录

- [快速开始](#快速开始)
- [认证](#认证)
- [端点详解](#端点详解)
- [错误处理](#错误处理)
- [速率限制](#速率限制)
- [代码示例](#代码示例)

---

## 快速开始

### 1. 健康检查

首先检查API服务是否正常运行:

```bash
curl http://localhost:8000/api/v1/health
```

**响应示例**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-24T12:00:00Z",
  "database": {
    "status": "connected",
    "path": "data/tts_history.db"
  },
  "tts_engine": {
    "status": "ready",
    "name": "edge-tts"
  }
}
```

### 2. 创建第一个TTS任务

```bash
curl -X POST http://localhost:8000/api/v1/tts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好,世界!",
    "voice_name": "晓晓-女声",
    "rate": 1.0,
    "pitch": 1.0,
    "volume": 1.0
  }'
```

**响应示例**:
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "text": "你好,世界!",
  "voice_name": "晓晓-女声",
  "rate": 1.0,
  "pitch": 1.0,
  "volume": 1.0,
  "status": "queued",
  "progress": 0.0,
  "file_path": null,
  "error_message": null,
  "created_at": "2026-01-24T12:00:00Z",
  "started_at": null,
  "completed_at": null
}
```

### 3. 查询任务状态

```bash
curl http://localhost:8000/api/v1/tts/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### 4. 下载音频文件

```bash
curl -O -J http://localhost:8000/api/v1/tts/download/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

## 认证

**当前版本**: 无需认证

API当前不需要任何认证。所有端点都可以直接访问。

**未来计划**:
- 可能添加API密钥认证(`X-API-Key`请求头)
- 可能添加CORS配置限制访问来源

---

## 端点详解

### TTS生成端点

#### POST /api/v1/tts/generate

创建新的TTS生成任务。

**请求体**:

| 字段 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| text | string | ✅ | - | 要转换的文本(1-5000字符) |
| voice_name | string | ❌ | "晓晓-女声" | 音色名称 |
| rate | float | ❌ | 1.0 | 语速倍率(0.5-2.0) |
| pitch | float | ❌ | 1.0 | 音调倍率(0.5-2.0) |
| volume | float | ❌ | 1.0 | 音量倍率(0.0-1.0) |

**可用音色列表**:
- "晓晓-女声" (默认)
- "云扬-男声"
- "晓悠-童声"
- "晓伊-年轻女声"
- "云健-沉稳男声"

**成功响应**: `201 Created`
- 返回创建的任务对象

**错误响应**:
- `400 Bad Request`: 请求参数错误
- `422 Unprocessable Entity`: 验证失败
- `429 Too Many Requests`: 队列已满(最多10个任务)

#### GET /api/v1/tts/tasks/{task_id}

获取任务详情。

**路径参数**:
- `task_id` (string, UUID): 任务ID

**成功响应**: `200 OK`
- 返回任务对象

**错误响应**:
- `404 Not Found`: 任务不存在

#### DELETE /api/v1/tts/tasks/{task_id}

取消任务。

**限制**:
- 仅可取消状态为`queued`的任务
- 正在处理或已完成的任务无法取消

**成功响应**: `200 OK`

**错误响应**:
- `400 Bad Request`: 任务无法取消
- `404 Not Found`: 任务不存在

#### GET /api/v1/tts/download/{task_id}

下载生成的音频文件。

**限制**:
- 任务状态必须为`completed`

**成功响应**: `200 OK`
- Content-Type: `audio/mpeg`
- 返回MP3文件二进制数据
- 文件名格式: `tts_{task_id}_{timestamp}.mp3`

**错误响应**:
- `404 Not Found`: 任务不存在
- `425 Too Early`: 任务未完成

#### GET /api/v1/voices

获取可用音色列表。

**成功响应**: `200 OK`
```json
{
  "voices": [
    {
      "name": "晓晓-女声",
      "voice_id": "zh-CN-XiaoxiaoNeural",
      "description": "温柔女声",
      "default": true
    },
    ...
  ]
}
```

---

### 队列管理端点

#### GET /api/v1/queue/status

获取队列状态统计。

**成功响应**: `200 OK`
```json
{
  "queued_count": 3,
  "processing_count": 1,
  "completed_count": 15,
  "current_task": {
    "task_id": "...",
    "text": "...",
    "status": "processing",
    "progress": 45.5
  },
  "max_queue_size": 10
}
```

**字段说明**:
- `queued_count`: 排队中的任务数量
- `processing_count`: 正在处理的任务数量(最多1个)
- `completed_count`: 已完成的任务数量
- `current_task`: 当前正在处理的任务(可能为null)
- `max_queue_size`: 队列最大容量

---

### 历史记录端点

#### GET /api/v1/history

获取生成历史记录。

**查询参数**:
- `limit` (integer, 可选): 返回记录数量(1-20,默认20)

**成功响应**: `200 OK`
```json
{
  "total": 20,
  "records": [
    {
      "id": 1,
      "task_id": "...",
      "text_summary": "你好,世界!",
      "voice_params": {
        "voice_name": "晓晓-女声",
        "voice_id": "zh-CN-XiaoxiaoNeural",
        "rate": 1.0,
        "pitch": 1.0,
        "volume": 1.0
      },
      "created_at": "2026-01-24T12:00:00Z",
      "file_path": "output/tts_..._20260124_120000.mp3",
      "file_size": 12345,
      "status": "completed"
    },
    ...
  ]
}
```

**说明**:
- 按时间倒序排列(最新的在前)
- 最多保存20条记录
- 自动清理旧记录(FIFO)

#### DELETE /api/v1/history/{history_id}

删除单条历史记录。

**路径参数**:
- `history_id` (integer): 历史记录ID

**成功响应**: `200 OK`
```json
{
  "message": "History record deleted successfully",
  "history_id": 1
}
```

**注意**: 同时删除关联的音频文件

#### DELETE /api/v1/history/clear

清空所有历史记录。

**成功响应**: `200 OK`
```json
{
  "message": "All history records cleared",
  "deleted_count": 20
}
```

**注意**: 删除所有历史记录和关联的音频文件

---

### 健康检查端点

#### GET /api/v1/health

检查API服务状态。

**成功响应**: `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-24T12:00:00Z",
  "database": {
    "status": "connected",
    "path": "data/tts_history.db"
  },
  "tts_engine": {
    "status": "ready",
    "name": "edge-tts"
  }
}
```

---

## 错误处理

所有错误响应都遵循统一格式:

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "details": {
    // 额外的错误详情(可选)
  }
}
```

### 常见错误类型

| HTTP状态码 | 错误类型 | 说明 |
|-----------|---------|------|
| 400 | BadRequest | 请求参数错误或逻辑错误 |
| 404 | NotFound | 资源不存在 |
| 422 | ValidationError | 请求验证失败 |
| 425 | TaskNotReady | 任务未完成 |
| 429 | QueueFull | 队列已满 |
| 500 | InternalError | 服务器内部错误 |

### 错误示例

**验证失败** (422):
```json
{
  "error": "ValidationError",
  "message": "Validation failed",
  "details": {
    "text": ["ensure this value has at least 1 characters"],
    "rate": ["ensure this value is greater than or equal to 0.5"]
  }
}
```

**任务不存在** (404):
```json
{
  "error": "NotFound",
  "message": "Task not found",
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**队列已满** (429):
```json
{
  "error": "QueueFull",
  "message": "Task queue is full (max 10 tasks), please try again later",
  "max_size": 10
}
```

---

## 速率限制

**当前版本**: 无全局速率限制

**队列限制**:
- 最多10个任务同时排队
- 超过后返回`429 Too Many Requests`

**文本长度限制**:
- 单次请求最大5000字符
- 超过后返回`422 ValidationError`

**建议**:
- 前端应实现节流(debounce),避免快速重复提交
- 查询队列状态后再决定是否提交新任务

---

## 代码示例

### JavaScript/TypeScript (Axios)

```typescript
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api/v1'

// 创建TTS任务
async function createTTSTask(text: string, voiceName = '晓晓-女声') {
  try {
    const response = await axios.post(`${API_BASE}/tts/generate`, {
      text,
      voice_name: voiceName,
      rate: 1.0,
      pitch: 1.0,
      volume: 1.0
    })
    return response.data // 返回任务对象
  } catch (error) {
    console.error('创建任务失败:', error.response.data)
    throw error
  }
}

// 查询任务状态
async function getTaskStatus(taskId: string) {
  const response = await axios.get(`${API_BASE}/tts/tasks/${taskId}`)
  return response.data
}

// 轮询任务直到完成
async function waitForTaskCompletion(taskId: string, interval = 1000) {
  while (true) {
    const task = await getTaskStatus(taskId)
    if (task.status === 'completed') {
      return task
    } else if (task.status === 'failed' || task.status === 'cancelled') {
      throw new Error(task.error_message || 'Task failed')
    }
    await new Promise(resolve => setTimeout(resolve, interval))
  }
}

// 下载音频文件
async function downloadAudio(taskId: string, filename?: string) {
  const response = await axios.get(`${API_BASE}/tts/download/${taskId}`, {
    responseType: 'blob'
  })

  // 创建下载链接
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename || `tts_${taskId}.mp3`)
  document.body.appendChild(link)
  link.click()
  link.remove()
}

// 完整工作流示例
async function generateAndDownloadTTS(text: string) {
  // 1. 创建任务
  const task = await createTTSTask(text)
  console.log('任务已创建:', task.task_id)

  // 2. 等待完成
  const completedTask = await waitForTaskCompletion(task.task_id)
  console.log('任务已完成:', completedTask)

  // 3. 下载音频
  await downloadAudio(completedTask.task_id)
  console.log('音频已下载')
}
```

### Python (requests)

```python
import requests
import time

API_BASE = "http://localhost:8000/api/v1"

def create_tts_task(text: str, voice_name: str = "晓晓-女声"):
    """创建TTS任务"""
    response = requests.post(
        f"{API_BASE}/tts/generate",
        json={
            "text": text,
            "voice_name": voice_name,
            "rate": 1.0,
            "pitch": 1.0,
            "volume": 1.0
        }
    )
    response.raise_for_status()
    return response.json()

def get_task_status(task_id: str):
    """查询任务状态"""
    response = requests.get(f"{API_BASE}/tts/tasks/{task_id}")
    response.raise_for_status()
    return response.json()

def wait_for_task_completion(task_id: str, interval: float = 1.0):
    """等待任务完成"""
    while True:
        task = get_task_status(task_id)
        if task["status"] == "completed":
            return task
        elif task["status"] in ["failed", "cancelled"]:
            raise Exception(task.get("error_message", "Task failed"))
        time.sleep(interval)

def download_audio(task_id: str, filename: str = None):
    """下载音频文件"""
    response = requests.get(f"{API_BASE}/tts/download/{task_id}", stream=True)
    response.raise_for_status()

    filename = filename or f"tts_{task_id}.mp3"
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return filename

# 完整工作流
def generate_and_download_tts(text: str):
    # 1. 创建任务
    task = create_tts_task(text)
    print(f"任务已创建: {task['task_id']}")

    # 2. 等待完成
    completed_task = wait_for_task_completion(task['task_id'])
    print(f"任务已完成: {completed_task}")

    # 3. 下载音频
    filename = download_audio(completed_task['task_id'])
    print(f"音频已下载: {filename}")

    return filename
```

### cURL

```bash
# 创建任务
curl -X POST http://localhost:8000/api/v1/tts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好,世界!",
    "voice_name": "晓晓-女声",
    "rate": 1.0,
    "pitch": 1.0,
    "volume": 1.0
  }'

# 查询任务
curl http://localhost:8000/api/v1/tts/tasks/{task_id}

# 下载音频
curl -O -J http://localhost:8000/api/v1/tts/download/{task_id}

# 获取队列状态
curl http://localhost:8000/api/v1/queue/status

# 获取历史记录
curl http://localhost:8000/api/v1/history?limit=10

# 健康检查
curl http://localhost:8000/api/v1/health
```

---

## 最佳实践

### 1. 轮询任务状态

```typescript
// 推荐: 使用指数退避
async function pollTaskWithBackoff(taskId: string) {
  let delay = 500 // 初始500ms
  const maxDelay = 5000 // 最大5秒

  while (true) {
    const task = await getTaskStatus(taskId)
    if (task.status === 'completed') return task
    if (task.status === 'failed' || task.status === 'cancelled') {
      throw new Error(task.error_message)
    }

    await new Promise(resolve => setTimeout(resolve, delay))
    delay = Math.min(delay * 1.5, maxDelay) // 指数退避
  }
}
```

### 2. 错误重试

```typescript
// 对临时错误(如网络问题)进行重试
async function createTaskWithRetry(text: string, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await createTTSTask(text)
    } catch (error) {
      if (i === maxRetries - 1) throw error
      if (error.response?.status >= 500) {
        // 服务器错误,等待后重试
        await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)))
      } else {
        // 客户端错误,不重试
        throw error
      }
    }
  }
}
```

### 3. 队列管理

```typescript
// 提交前检查队列状态
async function submitTaskSafely(text: string) {
  const status = await axios.get(`${API_BASE}/queue/status`)
  if (status.data.queued_count >= status.data.max_queue_size) {
    throw new Error('队列已满,请稍后重试')
  }

  return await createTTSTask(text)
}
```

---

## 总结

本API文档涵盖了离线TTS工具的所有端点、参数、响应格式和错误处理。如有疑问或建议,请参考OpenAPI规范(`openapi.yaml`)或联系开发团队。

**相关文档**:
- [OpenAPI规范](./openapi.yaml)
- [数据模型](../data-model.md)
- [快速开始](../quickstart.md)
