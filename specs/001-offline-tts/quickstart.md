# 开发快速开始指南

**Feature**: 离线文字转语音工具 (001-offline-tts)
**Last Updated**: 2026-01-24

## 目录

- [前置要求](#前置要求)
- [项目结构](#项目结构)
- [环境搭建](#环境搭建)
- [开发指南](#开发指南)
- [测试](#测试)
- [常见问题](#常见问题)
- [部署](#部署)

---

## 前置要求

### 系统要求

- **操作系统**: Windows 10+, Linux, macOS
- **Python**: 3.12 或更高版本
- **Node.js**: 18.x 或更高版本
- **Git**: 用于版本控制

### 开发工具 (推荐)

- **IDE**: VSCode / PyCharm / WebStorm
- **API测试**: Postman / Insomnia / HTTPie
- **数据库管理**: DB Browser for SQLite

---

## 项目结构

```
tts/
├── backend/                   # 后端服务
│   ├── src/
│   │   ├── api/              # FastAPI路由
│   │   ├── models/           # 数据模型
│   │   ├── services/         # 业务逻辑
│   │   ├── core/             # 核心配置
│   │   └── main.py           # 应用入口
│   ├── tests/                # 后端测试
│   ├── data/                 # 数据库文件
│   ├── output/               # 音频文件输出
│   ├── logs/                 # 日志文件
│   ├── requirements.txt      # Python依赖
│   └── pyproject.toml        # 项目配置
│
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── components/       # Vue组件
│   │   ├── views/            # 页面视图
│   │   ├── services/         # API服务
│   │   ├── stores/           # Pinia状态
│   │   ├── types/            # TypeScript类型
│   │   ├── utils/            # 工具函数
│   │   ├── App.vue
│   │   └── main.ts
│   ├── public/
│   ├── tests/                # 前端测试
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .eslintrc.cjs
│
├── specs/                     # 规范文档
│   └── 001-offline-tts/
│       ├── spec.md           # 功能规范
│       ├── plan.md           # 实施计划
│       ├── research.md       # 技术研究
│       ├── data-model.md     # 数据模型
│       ├── quickstart.md     # 本文档
│       └── contracts/        # API契约
│
├── .gitignore
└── README.md
```

---

## 环境搭建

### 1. 克隆项目

```bash
git clone <repository-url>
cd tts
git checkout 001-offline-tts
```

### 2. 后端环境搭建

#### 2.1 创建Python虚拟环境

**Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS**:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 2.2 安装Python依赖

```bash
# 进入backend目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 或使用poetry (推荐)
poetry install
```

**requirements.txt**:
```txt
# FastAPI和服务器
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.6

# 数据库
sqlalchemy>=2.0.25
aiosqlite>=0.19.0

# TTS引擎
edge-tts>=6.1.9

# 工具库
python-dotenv>=1.0.0
pydantic>=2.5.0

# 开发工具
pytest>=7.4.0
pytest-asyncio>=0.23.0
httpx>=0.26.0
black>=24.1.0
ruff>=0.1.0
mypy>=1.8.0
```

#### 2.3 配置环境变量

创建`.env`文件:

```bash
# backend/.env
DATABASE_URL=sqlite+aiosqlite:///data/tts_history.db
LOG_LEVEL=INFO
MAX_QUEUE_SIZE=10
MAX_HISTORY_SIZE=20
OUTPUT_DIR=output
LOG_DIR=logs
```

#### 2.4 初始化数据库

```bash
# 数据库会在首次运行时自动创建
# 或手动创建:
python -c "from backend.src.core.database import init_database; import asyncio; asyncio.run(init_database())"
```

#### 2.5 启动后端服务

```bash
# 开发模式 (自动重载)
cd backend
uvicorn src.main:app --reload --port 8000

# 或使用python直接运行
python -m src.main
```

验证后端服务:
```bash
curl http://localhost:8000/api/v1/health
```

访问API文档:
```
http://localhost:8000/docs
```

---

### 3. 前端环境搭建

#### 3.1 安装Node.js依赖

```bash
# 进入frontend目录
cd frontend

# 安装依赖
npm install

# 或使用pnpm (更快)
pnpm install
```

**package.json** 主要依赖:
```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0",
    "element-plus": "^2.5.0",
    "@element-plus/icons-vue": "^2.3.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vitest": "^1.1.0",
    "eslint": "^8.56.0",
    "prettier": "^3.1.0"
  }
}
```

#### 3.2 配置开发环境

创建`.env.development`:

```bash
# frontend/.env.development
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=离线文字转语音工具
```

#### 3.3 启动前端开发服务器

```bash
# 开发模式
cd frontend
npm run dev

# 或
pnpm dev
```

访问前端应用:
```
http://localhost:5173
```

---

## 开发指南

### 后端开发

#### 目录结构

```
backend/src/
├── api/
│   ├── __init__.py
│   ├── tts.py          # TTS生成API
│   ├── queue.py        # 队列管理API
│   ├── history.py      # 历史记录API
│   └── health.py       # 健康检查API
├── models/
│   ├── __init__.py
│   ├── task.py         # 任务模型
│   └── history.py      # 历史记录模型
├── services/
│   ├── __init__.py
│   ├── tts_service.py  # TTS引擎封装
│   ├── queue_service.py # 队列管理
│   └── history_service.py # 历史记录管理
├── core/
│   ├── __init__.py
│   ├── config.py       # 配置管理
│   ├── database.py     # 数据库连接
│   ├── logger.py       # 日志配置
│   └── security.py     # 安全验证
└── main.py             # 应用入口
```

#### 代码示例

**创建API端点** (`backend/src/api/tts.py`):

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ..core.database import get_db
from ..models.task import Task, TaskStatus
from ..services.tts_service import TTSService

router = APIRouter(prefix="/tts", tags=["tts"])

class TaskCreateRequest(BaseModel):
    text: str
    voice_name: str = "晓晓-女声"
    rate: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0

@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def create_task(
    request: TaskCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建TTS生成任务"""

    # 验证输入
    if not request.text or len(request.text) > 5000:
        raise HTTPException(
            status_code=422,
            detail="text must be 1-5000 characters"
        )

    # 创建任务
    task = Task(
        text=request.text,
        voice_name=request.voice_name,
        rate=request.rate,
        pitch=request.pitch,
        volume=request.volume
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    # 加入队列
    tts_service = TTSService()
    await tts_service.enqueue_task(task)

    return task
```

**运行服务** (`backend/src/main.py`):

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import tts, queue, history, health
from .core.database import init_database

app = FastAPI(
    title="TTS Service",
    version="1.0.0",
    description="离线文字转语音工具API"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(tts.router, prefix="/api/v1")
app.include_router(queue.router, prefix="/api/v1")
app.include_router(history.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    await init_database()
    print("✅ TTS Service started successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

---

### 前端开发

#### 目录结构

```
frontend/src/
├── components/           # 可复用组件
│   ├── TTSInput.vue
│   ├── VoiceParams.vue
│   ├── QueueStatus.vue
│   └── HistoryList.vue
├── views/               # 页面视图
│   ├── Home.vue
│   └── History.vue
├── services/            # API服务
│   ├── tts.ts
│   ├── queue.ts
│   └── history.ts
├── stores/              # Pinia状态
│   ├── queue.ts
│   └── history.ts
├── types/               # TypeScript类型
│   └── api.ts
├── utils/               # 工具函数
│   └── validators.ts
├── App.vue
└── main.ts
```

#### 代码示例

**API服务** (`frontend/src/services/tts.ts`):

```typescript
import axios from 'axios'
import type { Task, TaskCreateRequest } from '@/types/api'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export const ttsService = {
  // 创建TTS任务
  async createTask(request: TaskCreateRequest): Promise<Task> {
    const response = await axios.post(`${API_BASE}/tts/generate`, request)
    return response.data
  },

  // 获取任务详情
  async getTask(taskId: string): Promise<Task> {
    const response = await axios.get(`${API_BASE}/tts/tasks/${taskId}`)
    return response.data
  },

  // 下载音频文件
  async downloadAudio(taskId: string): Promise<Blob> {
    const response = await axios.get(
      `${API_BASE}/tts/download/${taskId}`,
      { responseType: 'blob' }
    )
    return response.data
  },

  // 取消任务
  async cancelTask(taskId: string): Promise<void> {
    await axios.delete(`${API_BASE}/tts/tasks/${taskId}`)
  }
}
```

**Vue组件** (`frontend/src/views/Home.vue`):

```vue
<template>
  <div class="home">
    <h1>离线文字转语音工具</h1>

    <!-- 文本输入 -->
    <TTSInput v-model="text" :max-length="5000" />

    <!-- 语音参数 -->
    <VoiceParams v-model="params" />

    <!-- 生成按钮 -->
    <el-button
      type="primary"
      :loading="isGenerating"
      @click="handleGenerate"
    >
      生成语音
    </el-button>

    <!-- 任务状态 -->
    <div v-if="currentTask" class="task-status">
      <el-progress :percentage="currentTask.progress" />
      <p>状态: {{ currentTask.status }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import TTSInput from '@/components/TTSInput.vue'
import VoiceParams from '@/components/VoiceParams.vue'
import { ttsService } from '@/services/tts'
import type { TaskCreateRequest } from '@/types/api'

const text = ref('')
const params = ref<TaskCreateRequest>({
  voice_name: '晓晓-女声',
  rate: 1.0,
  pitch: 1.0,
  volume: 1.0
})

const isGenerating = ref(false)
const currentTask = ref<any>(null)

const handleGenerate = async () => {
  if (!text.value) {
    ElMessage.error('请输入文本')
    return
  }

  isGenerating.value = true

  try {
    // 创建任务
    const task = await ttsService.createTask({
      text: text.value,
      ...params.value
    })

    currentTask.value = task

    // 轮询任务状态
    const interval = setInterval(async () => {
      const updated = await ttsService.getTask(task.task_id)
      currentTask.value = updated

      if (updated.status === 'completed') {
        clearInterval(interval)
        isGenerating.value = false
        ElMessage.success('生成成功!')

        // 下载音频
        const blob = await ttsService.downloadAudio(task.task_id)
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `tts_${task.task_id}.mp3`
        a.click()
      } else if (updated.status === 'failed') {
        clearInterval(interval)
        isGenerating.value = false
        ElMessage.error(updated.error_message || '生成失败')
      }
    }, 1000)

  } catch (error: any) {
    isGenerating.value = false
    ElMessage.error(error.response?.data?.message || '创建任务失败')
  }
}
</script>
```

---

## 测试

### 后端测试

```bash
# 运行所有测试
cd backend
pytest

# 运行特定测试文件
pytest tests/test_tts_api.py

# 带覆盖率报告
pytest --cov=src tests/

# 查看详细输出
pytest -v
```

**测试示例** (`backend/tests/test_tts_api.py`):

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ..src.main import app
from ..src.core.database import get_db

@pytest.mark.asyncio
async def test_create_task():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/tts/generate",
            json={
                "text": "测试文本",
                "voice_name": "晓晓-女声"
            }
        )
    assert response.status_code == 201
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "queued"
```

### 前端测试

```bash
# 运行单元测试
cd frontend
npm run test

# 运行测试并生成覆盖率报告
npm run test:coverage

# UI模式(交互式)
npm run test:ui
```

**测试示例** (`frontend/src/services/__tests__/tts.test.ts`):

```typescript
import { describe, it, expect, vi } from 'vitest'
import { ttsService } from '../tts'
import axios from 'axios'

vi.mock('axios')

describe('TTSService', () => {
  it('should create task successfully', async () => {
    const mockTask = {
      task_id: '123',
      status: 'queued',
      text: '测试'
    }

    vi.mocked(axios.post).mockResolvedValue({
      data: mockTask
    })

    const result = await ttsService.createTask({
      text: '测试',
      voice_name: '晓晓-女声'
    })

    expect(result).toEqual(mockTask)
  })
})
```

---

## 常见问题

### Q1: 后端启动失败 "ModuleNotFoundError"

**解决方案**:
```bash
# 确保虚拟环境已激活
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

# 重新安装依赖
pip install -r backend/requirements.txt
```

### Q2: 前端无法连接后端API

**解决方案**:
1. 检查后端是否运行: `curl http://localhost:8000/api/v1/health`
2. 检查CORS配置 (`backend/src/main.py`)
3. 检查前端代理配置 (`frontend/vite.config.ts`)

### Q3: edge-tts音色下载失败

**解决方案**:
```bash
# 检查网络连接(首次使用需要下载音色模型)
# 或手动指定音色路径
```

### Q4: SQLite数据库锁定

**解决方案**:
```bash
# 确保没有其他进程占用数据库
# Windows: 使用Process Explorer查找锁定进程
# Linux/macOS: lsof | grep tts_history.db
```

---

## 部署

### 开发部署

**后端**:
```bash
cd backend
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**前端**:
```bash
cd frontend
npm run dev
```

### 生产部署

**后端 (使用systemd)**:

创建服务文件 `/etc/systemd/system/tts-api.service`:

```ini
[Unit]
Description=TTS API Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/tts/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl start tts-api
sudo systemctl enable tts-api
```

**前端 (构建静态文件)**:

```bash
cd frontend
npm run build
```

将`frontend/dist`目录部署到Nginx:

```nginx
server {
    listen 80;
    server_name tts.example.com;
    root /path/to/frontend/dist;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 开发工作流

### 代码规范

**后端**:
```bash
# 代码格式化
cd backend
black src/
ruff check src/

# 类型检查
mypy src/
```

**前端**:
```bash
# 代码格式化和检查
cd frontend
npm run lint
npm run format
```

### Git提交规范

遵循Conventional Commits:

```bash
# 功能
git commit -m "feat: 添加批量下载功能"

# 修复
git commit -m "fix: 修复任务状态更新错误"

# 文档
git commit -m "docs: 更新API文档"

# 样式
git commit -m "style: 统一代码格式"

# 重构
git commit -m "refactor: 优化队列管理逻辑"

# 测试
git commit -m "test: 添加TTS API测试"
```

---

## 相关资源

- [功能规范](./spec.md)
- [实施计划](./plan.md)
- [数据模型](./data-model.md)
- [API文档](./contracts/openapi.yaml)
- [API使用指南](./contracts/api-guide.md)

---

**Happy Coding!** 🚀

如有问题,请查看项目README.md或联系开发团队。
