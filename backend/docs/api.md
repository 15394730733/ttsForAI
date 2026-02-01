# TTS API 文档

## 概述

离线文字转语音工具提供了完整的RESTful API接口，支持文本转语音、任务队列管理、历史记录查询等功能。

**Base URL**: `http://localhost:8000/api/v1`

**API版本**: v1.0

**内容类型**: `application/json`

---

## 目录

- [TTS任务管理](#tts任务管理)
  - [创建TTS任务](#创建tts任务)
  - [获取任务详情](#获取任务详情)
  - [取消任务](#取消任务)
  - [下载音频文件](#下载音频文件)
  - [获取可用音色列表](#获取可用音色列表)
- [队列管理](#队列管理)
  - [获取队列状态](#获取队列状态)
- [历史记录](#历史记录)
  - [获取历史记录列表](#获取历史记录列表)
  - [删除历史记录](#删除历史记录)
  - [清空所有历史记录](#清空所有历史记录)
- [健康检查](#健康检查)
- [错误码说明](#错误码说明)

---

## TTS任务管理

### 创建TTS任务

创建一个新的文字转语音任务。

**端点**: `POST /api/v1/tts/generate`

**请求参数**:

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| text | string | 是 | - | 要转换的文本内容（1-5000字符） |
| voice_name | string | 否 | `zh-CN-XiaoxiaoNeural` | 音色名称或ID |
| rate | float | 否 | `1.0` | 语速倍率（0.5-2.0） |
| pitch | float | 否 | `1.0` | 音调倍率（0.5-2.0） |
| volume | float | 否 | `1.0` | 音量（0.0-1.0） |

**请求示例**:

```bash
curl -X POST "http://localhost:8000/api/v1/tts/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，世界！",
    "voice_name": "晓晓-女声",
    "rate": 1.0,
    "pitch": 1.0,
    "volume": 1.0
  }'
```

**成功响应** (201 Created):

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "你好，世界！",
  "voice_name": "zh-CN-XiaoxiaoNeural",
  "rate": 1.0,
  "pitch": 1.0,
  "volume": 1.0,
  "status": "queued",
  "progress": 0,
  "file_path": null,
  "error_message": null,
  "created_at": "2026-01-29T10:30:00",
  "started_at": null,
  "completed_at": null
}
```

**错误响应**:

| HTTP状态码 | 错误类型 | 说明 |
|-----------|---------|------|
| 400 | Bad Request | 文本为空、超长、包含非法字符或音色无效 |
| 429 | Too Many Requests | 队列已满 |

---

### 获取任务详情

根据任务ID获取任务的状态和详细信息。

**端点**: `GET /api/v1/tts/tasks/{task_id}`

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| task_id | string | 任务唯一标识符 |

**请求示例**:

```bash
curl -X GET "http://localhost:8000/api/v1/tts/tasks/550e8400-e29b-41d4-a716-446655440000"
```

**成功响应** (200 OK):

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "你好，世界！",
  "voice_name": "zh-CN-XiaoxiaoNeural",
  "rate": 1.0,
  "pitch": 1.0,
  "volume": 1.0,
  "status": "completed",
  "progress": 100,
  "file_path": "output/tts_550e8400-e29b-41d4-a716-446655440000_1706522400.mp3",
  "error_message": null,
  "created_at": "2026-01-29T10:30:00",
  "started_at": "2026-01-29T10:30:01",
  "completed_at": "2026-01-29T10:30:05"
}
```

**任务状态说明**:

| 状态 | 说明 |
|------|------|
| `queued` | 任务已排队，等待处理 |
| `processing` | 任务正在处理中 |
| `completed` | 任务已完成 |
| `failed` | 任务失败 |
| `cancelled` | 任务已取消 |

**错误响应**:

| HTTP状态码 | 错误类型 | 说明 |
|-----------|---------|------|
| 404 | Not Found | 任务不存在 |

---

### 取消任务

取消一个排队中的任务。

**端点**: `DELETE /api/v1/tts/tasks/{task_id}`

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| task_id | string | 任务唯一标识符 |

**请求示例**:

```bash
curl -X DELETE "http://localhost:8000/api/v1/tts/tasks/550e8400-e29b-41d4-a716-446655440000"
```

**成功响应** (200 OK):

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "cancelled"
}
```

**错误响应**:

| HTTP状态码 | 错误类型 | 说明 |
|-----------|---------|------|
| 400 | Bad Request | 任务不存在或无法取消（已开始处理） |
| 404 | Not Found | 任务不存在 |

**注意**: 只能取消状态为 `queued` 的任务。正在处理或已完成的任务无法取消。

---

### 下载音频文件

下载已完成的任务生成的音频文件。

**端点**: `GET /api/v1/tts/download/{task_id}`

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| task_id | string | 任务唯一标识符 |

**请求示例**:

```bash
curl -X GET "http://localhost:8000/api/v1/tts/download/550e8400-e29b-41d4-a716-446655440000" \
  --output audio.mp3
```

**成功响应** (200 OK):

- **Content-Type**: `audio/mpeg`
- **Content-Disposition**: `attachment; filename="{task_id}.mp3"`
- **Body**: 音频文件二进制数据

**错误响应**:

| HTTP状态码 | 错误类型 | 说明 |
|-----------|---------|------|
| 400 | Bad Request | 任务未完成或文件不可用 |
| 404 | Not Found | 任务或文件不存在 |

---

### 获取可用音色列表

获取系统支持的所有音色列表。

**端点**: `GET /api/v1/tts/voices`

**请求示例**:

```bash
curl -X GET "http://localhost:8000/api/v1/tts/voices"
```

**成功响应** (200 OK):

```json
{
  "voices": [
    {
      "name": "晓晓-女声",
      "voice_id": "zh-CN-XiaoxiaoNeural",
      "description": "默认女声",
      "default": true
    },
    {
      "name": "云扬-男声",
      "voice_id": "zh-CN-YunyangNeural",
      "description": "云扬-男声",
      "default": false
    },
    {
      "name": "晓悠-童声",
      "voice_id": "zh-CN-XiaoyouNeural",
      "description": "晓悠-童声",
      "default": false
    },
    {
      "name": "晓伊-年轻女声",
      "voice_id": "zh-CN-XiaoyiNeural",
      "description": "晓伊-年轻女声",
      "default": false
    },
    {
      "name": "云健-沉稳男声",
      "voice_id": "zh-CN-YunjianNeural",
      "description": "云健-沉稳男声",
      "default": false
    }
  ]
}
```

**说明**:
- `default` 字段标记了默认音色
- 创建任务时可以使用 `name` 或 `voice_id` 指定音色

---

## 队列管理

### 获取队列状态

获取当前任务队列的状态信息。

**端点**: `GET /api/v1/queue/status`

**请求示例**:

```bash
curl -X GET "http://localhost:8000/api/v1/queue/status"
```

**成功响应** (200 OK):

```json
{
  "queued_count": 3,
  "processing_count": 1,
  "completed_count": 15,
  "current_task": null,
  "max_queue_size": 10
}
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| queued_count | int | 排队中的任务数量 |
| processing_count | int | 正在处理的任务数量 |
| completed_count | int | 已完成的任务数量 |
| current_task | object/null | 当前正在处理的任务（暂未实现） |
| max_queue_size | int | 队列最大容量 |

---

## 历史记录

### 获取历史记录列表

获取TTS生成历史记录列表，支持分页。

**端点**: `GET /api/v1/history`

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| skip | int | 否 | `0` | 跳过的记录数（用于分页） |
| limit | int | 否 | `20` | 返回的最大记录数 |

**请求示例**:

```bash
curl -X GET "http://localhost:8000/api/v1/history?skip=0&limit=10"
```

**成功响应** (200 OK):

```json
{
  "records": [
    {
      "id": 1,
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "text_summary": "你好，世界！",
      "voice_params": "{\"voice_name\":\"zh-CN-XiaoxiaoNeural\",\"rate\":1.0,\"pitch\":1.0,\"volume\":1.0}",
      "created_at": "2026-01-29T10:30:00",
      "file_path": "output/tts_550e8400-e29b-41d4-a716-446655440000_1706522400.mp3",
      "file_size": 24568,
      "status": "completed"
    }
  ],
  "total": 20
}
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 历史记录ID（自增主键） |
| task_id | string | 关联的任务ID |
| text_summary | string | 文本摘要（前100字符） |
| voice_params | string | 语音参数JSON字符串 |
| created_at | string | 创建时间（ISO 8601格式） |
| file_path | string | 音频文件路径 |
| file_size | int | 文件大小（字节） |
| status | string | 任务状态 |

**分页说明**:
- 系统最多保留20条历史记录
- 使用 `skip` 和 `limit` 参数实现分页
- `total` 字段返回总记录数

---

### 删除历史记录

删除指定的单条历史记录。

**端点**: `DELETE /api/v1/history/{history_id}`

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| history_id | int | 历史记录ID |

**请求示例**:

```bash
curl -X DELETE "http://localhost:8000/api/v1/history/1"
```

**成功响应** (200 OK):

```json
{
  "id": 1,
  "deleted": true,
  "message": "历史记录 1 已删除"
}
```

**错误响应**:

| HTTP状态码 | 错误类型 | 说明 |
|-----------|---------|------|
| 404 | Not Found | 历史记录不存在 |

**注意**: 删除历史记录时会同步删除关联的音频文件。

---

### 清空所有历史记录

清空所有历史记录及其关联的音频文件。

**端点**: `DELETE /api/v1/history/clear`

**请求示例**:

```bash
curl -X DELETE "http://localhost:8000/api/v1/history/clear"
```

**成功响应** (200 OK):

```json
{
  "deleted_count": 20,
  "message": "已删除 20 条历史记录"
}
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| deleted_count | int | 删除的记录数量 |
| message | string | 操作结果消息 |

**注意**: 此操作不可逆，会删除所有历史记录和关联的音频文件。

---

## 健康检查

### 检查服务健康状态

检查API服务是否正常运行。

**端点**: `GET /health`

**请求示例**:

```bash
curl -X GET "http://localhost:8000/health"
```

**成功响应** (200 OK):

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## 错误码说明

### HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 429 | 请求过多（队列满） |
| 500 | 服务器内部错误 |

### 错误响应格式

所有错误响应遵循统一格式：

```json
{
  "detail": "错误描述消息"
}
```

**常见错误示例**:

1. **文本为空或超长**
```json
{
  "detail": "Text must be 1-5000 characters"
}
```

2. **队列已满**
```json
{
  "detail": "Queue is full (10 tasks)"
}
```

3. **任务不存在**
```json
{
  "detail": "Task not found"
}
```

4. **音色无效**
```json
{
  "detail": "Invalid voice name. Allowed voices: 晓晓-女声, 云扬-男声, 晓悠-童声, 晓伊-年轻女声, 云健-沉稳男声"
}
```

5. **文件未就绪**
```json
{
  "detail": "Audio file not ready"
}
```

---

## 使用示例

### 完整工作流示例

1. **创建任务**
```bash
TASK_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/tts/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "欢迎使用离线文字转语音工具",
    "voice_name": "晓晓-女声",
    "rate": 1.2,
    "pitch": 1.0,
    "volume": 0.9
  }')

TASK_ID=$(echo $TASK_RESPONSE | jq -r '.task_id')
echo "任务已创建，ID: $TASK_ID"
```

2. **查询任务状态**
```bash
curl -X GET "http://localhost:8000/api/v1/tts/tasks/$TASK_ID"
```

3. **等待任务完成（轮询）**
```bash
while true; do
  STATUS=$(curl -s "http://localhost:8000/api/v1/tts/tasks/$TASK_ID" | jq -r '.status')
  if [ "$STATUS" == "completed" ]; then
    echo "任务完成"
    break
  elif [ "$STATUS" == "failed" ]; then
    echo "任务失败"
    exit 1
  fi
  echo "任务状态: $STATUS，等待中..."
  sleep 2
done
```

4. **下载音频文件**
```bash
curl -X GET "http://localhost:8000/api/v1/tts/download/$TASK_ID" \
  --output speech.mp3
```

### Python示例

```python
import requests
import time

API_BASE = "http://localhost:8000/api/v1"

# 创建任务
response = requests.post(
    f"{API_BASE}/tts/generate",
    json={
        "text": "你好，世界！",
        "voice_name": "晓晓-女声",
        "rate": 1.0,
        "pitch": 1.0,
        "volume": 1.0
    }
)
task = response.json()
task_id = task["task_id"]
print(f"任务已创建: {task_id}")

# 轮询任务状态
while True:
    response = requests.get(f"{API_BASE}/tts/tasks/{task_id}")
    task = response.json()
    status = task["status"]

    if status == "completed":
        print("任务完成")
        break
    elif status == "failed":
        print(f"任务失败: {task['error_message']}")
        exit(1)

    print(f"任务状态: {status}，进度: {task['progress']}%")
    time.sleep(2)

# 下载音频
response = requests.get(f"{API_BASE}/tts/download/{task_id}")
with open("speech.mp3", "wb") as f:
    f.write(response.content)
print("音频已下载: speech.mp3")
```

### JavaScript示例

```javascript
const API_BASE = "http://localhost:8000/api/v1";

// 创建任务
async function createTask(text, voice = "晓晓-女声") {
  const response = await fetch(`${API_BASE}/tts/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      voice_name: voice,
      rate: 1.0,
      pitch: 1.0,
      volume: 1.0
    })
  });

  if (!response.ok) {
    throw new Error(`创建任务失败: ${response.statusText}`);
  }

  return await response.json();
}

// 查询任务状态
async function getTaskStatus(taskId) {
  const response = await fetch(`${API_BASE}/tts/tasks/${taskId}`);
  return await response.json();
}

// 等待任务完成
async function waitForCompletion(taskId) {
  while (true) {
    const task = await getTaskStatus(taskId);

    if (task.status === "completed") {
      console.log("任务完成");
      return task;
    }

    if (task.status === "failed") {
      throw new Error(`任务失败: ${task.error_message}`);
    }

    console.log(`任务状态: ${task.status}，进度: ${task.progress}%`);
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
}

// 下载音频
async function downloadAudio(taskId, filename = "speech.mp3") {
  const response = await fetch(`${API_BASE}/tts/download/${taskId}`);
  const blob = await response.blob();

  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// 完整示例
async function main() {
  try {
    const task = await createTask("你好，世界！");
    console.log(`任务已创建: ${task.task_id}`);

    await waitForCompletion(task.task_id);
    await downloadAudio(task.task_id, "speech.mp3");
    console.log("音频已下载");
  } catch (error) {
    console.error("错误:", error.message);
  }
}

main();
```

---

## 性能指标

- **任务创建**: < 100ms
- **任务状态查询**: < 50ms
- **音频生成速度**: 约50-100字符/秒
- **并发支持**: 单任务处理（队列模式）
- **队列容量**: 最多10个排队任务

---

## 注意事项

1. **文本长度限制**: 单次转换文本最长5000字符
2. **队列限制**: 最多支持10个排队任务
3. **历史记录**: 系统自动保留最近20条历史记录
4. **文件存储**: 生成的音频文件存储在 `backend/output/` 目录
5. **任务超时**: 单个任务处理时间建议不超过60秒
6. **音色首次使用**: 首次使用某个音色时需要下载模型文件（约50-100MB）

---

## 相关文档

- [OpenAPI规范](./contracts/openapi.yaml)
- [用户使用手册](../../docs/user-guide.md)
- [部署文档](../../docs/deployment.md)
