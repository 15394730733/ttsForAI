# 离线文字转语音工具 (TTS) 开发指南

Auto-generated from feature plan. Last updated: 2026-01-24

## Active Technologies

### Backend
- **Python**: 3.12+ (最新稳定版)
- **Web框架**: FastAPI (最新稳定版)
- **TTS引擎**: edge-tts (微软Edge浏览器TTS引擎封装)
- **数据库ORM**: SQLAlchemy 2.0 + aiosqlite (异步SQLite)
- **异步处理**: asyncio
- **API文档**: FastAPI自动生成的OpenAPI 3.0文档
- **测试框架**: pytest + pytest-asyncio

### Frontend
- **框架**: Vue 3.x (Composition API)
- **语言**: TypeScript 5.x
- **构建工具**: Vite 5.x
- **状态管理**: Pinia
- **UI组件库**: Element Plus
- **HTTP客户端**: Axios
- **测试框架**: Vitest
- **代码规范**: ESLint + Prettier

### Infrastructure
- **数据库**: SQLite 3.x
- **日志**: Python logging模块 + 文件滚动
- **环境配置**: python-dotenv

## Project Structure

```text
backend/
├── src/
│   ├── api/              # FastAPI路由和端点
│   │   ├── tts.py        # TTS生成API
│   │   ├── queue.py      # 任务队列API
│   │   ├── history.py    # 历史记录API
│   │   └── health.py     # 健康检查API
│   ├── models/           # SQLAlchemy数据模型
│   │   ├── task.py       # 任务模型
│   │   └── history.py    # 历史记录模型
│   ├── services/         # 业务逻辑服务
│   │   ├── tts_service.py    # TTS引擎封装
│   │   ├── queue_service.py  # 任务队列管理
│   │   ├── storage_service.py # 文件存储管理
│   │   └── history_service.py # 历史记录管理
│   ├── core/             # 核心配置和工具
│   │   ├── config.py     # 配置管理
│   │   ├── database.py   # 数据库连接
│   │   ├── logger.py     # 日志配置
│   │   └── security.py   # 安全验证
│   └── main.py           # FastAPI应用入口
├── tests/
│   ├── contract/         # API契约测试
│   ├── integration/      # 集成测试
│   └── unit/             # 单元测试
├── data/                 # 数据目录
│   └── tts_history.db    # SQLite数据库
├── output/               # 生成的音频文件
├── logs/                 # 日志文件
├── requirements.txt      # Python依赖
└── pyproject.toml        # 项目配置(Black/Ruff/mypy)

frontend/
├── src/
│   ├── components/       # Vue组件
│   │   ├── TTSInput.vue      # 文本输入组件
│   │   ├── VoiceParams.vue   # 语音参数设置组件
│   │   ├── QueueStatus.vue   # 队列状态显示组件
│   │   ├── HistoryList.vue   # 历史记录列表组件
│   │   └── AudioPlayer.vue   # 音频播放器组件
│   ├── views/           # 页面视图
│   │   ├── Home.vue          # 主页面
│   │   └── History.vue       # 历史记录页面
│   ├── services/        # API服务
│   │   ├── tts.ts            # TTS API封装
│   │   ├── queue.ts          # 队列API封装
│   │   └── history.ts        # 历史记录API封装
│   ├── stores/          # Pinia状态管理
│   │   ├── queue.ts          # 队列状态
│   │   └── history.ts        # 历史记录状态
│   ├── types/           # TypeScript类型定义
│   │   └── api.ts            # API类型定义
│   ├── utils/           # 工具函数
│   │   └── validators.ts     # 输入验证
│   ├── App.vue          # 根组件
│   └── main.ts          # 应用入口
├── public/
├── tests/
│   ├── unit/            # 单元测试
│   └── integration/     # 集成测试
├── package.json         # npm配置
├── tsconfig.json        # TypeScript配置
├── vite.config.ts       # Vite配置
├── .eslintrc.cjs        # ESLint配置
└── .prettierrc          # Prettier配置
```

## Commands

### Backend (Python)

**开发**:
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器(自动重载)
uvicorn src.main:app --reload --port 8000

# 或
python -m src.main
```

**测试**:
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_tts_api.py

# 带覆盖率
pytest --cov=src tests/

# 详细输出
pytest -v
```

**代码质量**:
```bash
# 代码格式化
black src/

# Linter检查
ruff check src/

# 类型检查
mypy src/
```

**数据库**:
```bash
# 初始化数据库(自动创建表)
python -c "from backend.src.core.database import init_database; import asyncio; asyncio.run(init_database())"

# 查看数据库(使用DB Browser for SQLite)
# data/tts_history.db
```

### Frontend (Vue.js + TypeScript)

**开发**:
```bash
# 安装依赖
npm install
# 或
pnpm install

# 启动开发服务器
npm run dev
# 或
pnpm dev

# 构建生产版本
npm run build
```

**测试**:
```bash
# 运行单元测试
npm run test

# 测试覆盖率
npm run test:coverage

# UI模式(交互式)
npm run test:ui
```

**代码质量**:
```bash
# Lint检查
npm run lint

# 自动修复
npm run lint:fix

# 格式化
npm run format
```

### TTS引擎 (edge-tts)

**可用音色**:
```python
PRESET_VOICES = {
    "晓晓-女声": "zh-CN-XiaoxiaoNeural",  # 默认
    "云扬-男声": "zh-CN-YunyangNeural",
    "晓悠-童声": "zh-CN-XiaoyouNeural",
    "晓伊-年轻女声": "zh-CN-XiaoyiNeural",
    "云健-沉稳男声": "zh-CN-YunjianNeural"
}
```

**使用示例**:
```python
import edge_tts

async def generate_tts(text: str, voice: str, output_file: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
```

## Code Style

### Backend (Python)

**遵循规范**:
- **格式化**: Black (最大行长度88)
- **Linter**: Ruff
- **类型检查**: mypy (--strict模式)
- **导入顺序**: isort (Black内置)

**命名约定**:
- 模块: `snake_case`
- 类: `PascalCase`
- 函数/变量: `snake_case`
- 常量: `UPPER_SNAKE_CASE`

**文档字符串**:
```python
async def create_task(
    request: TaskCreateRequest,
    db: AsyncSession
) -> Task:
    """创建新的TTS生成任务.

    Args:
        request: 任务创建请求
        db: 数据库会话

    Returns:
        创建的任务对象

    Raises:
        HTTPException: 当验证失败时
    """
    pass
```

### Frontend (TypeScript + Vue)

**遵循规范**:
- **格式化**: Prettier (2空格,单引号)
- **Linter**: ESLint (@typescript-eslint)
- **Vue风格指南**: https://vuejs.org/style-guide/

**命名约定**:
- 组件: `PascalCase.vue`
- 文件: `kebab-case.ts` / `PascalCase.test.ts`
- 变量/函数: `camelCase`
- 常量: `UPPER_SNAKE_CASE`
- 接口/类型: `PascalCase`

**Vue组件最佳实践**:
```vue
<script setup lang="ts">
// 1. 导入
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

// 2. Props定义
interface Props {
  modelValue: string
  maxLength?: number
}
const props = withDefaults(defineProps<Props>(), {
  maxLength: 5000
})

// 3. Emits定义
const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

// 4. 响应式状态
const text = ref(props.modelValue)

// 5. 计算属性
const charCount = computed(() => text.value.length)

// 6. 方法
const handleChange = () => {
  emit('update:modelValue', text.value)
}
</script>
```

### API设计规范

**RESTful约定**:
- POST: 创建资源
- GET: 获取资源
- DELETE: 删除资源
- PUT/PATCH: 更新资源

**端点命名**:
- 名词复数: `/api/v1/tts/generate` (而非 `/api/v1/tt`)
- 层级结构: `/api/v1/tts/tasks/{task_id}`

**响应格式**:
```typescript
// 成功
{
  "task_id": "...",
  "status": "queued",
  ...
}

// 错误
{
  "error": "ValidationError",
  "message": "Validation failed",
  "details": {...}
}
```

## Recent Changes

### Feature: 离线文字转语音工具 (001-offline-tts) - 2026-01-24

**Added**:
- ✅ FastAPI后端服务架构
- ✅ Vue 3 + TypeScript前端应用
- ✅ edge-tts引擎集成
- ✅ SQLite数据库 + SQLAlchemy 2.0 ORM
- ✅ 任务队列管理(asyncio.Queue)
- ✅ 生成历史记录(最多20条)
- ✅ 基础日志和错误处理
- ✅ RESTful API设计(OpenAPI 3.0)
- ✅ Element Plus UI组件库

**Technical Decisions**:
- Python版本: 3.12+ (从3.10+升级)
- 数据库: SQLite + aiosqlite (异步)
- 任务队列: asyncio.Queue (轻量级,单用户)
- 前端框架: Vue 3 + TypeScript + Vite
- UI库: Element Plus (成熟稳定,中文文档)

**Architecture**:
- 前后端分离
- 异步API设计
- FIFO任务队列
- 自动历史记录清理

## Design Patterns

### Backend

**依赖注入**:
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
) -> Task:
    pass
```

**服务层模式**:
```python
# 服务封装业务逻辑
class TTSService:
    async def generate_audio(self, task: Task) -> str:
        pass

# API层调用服务
@router.post("/generate")
async def create_task(
    request: TaskCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    service = TTSService()
    return await service.generate_audio(task)
```

### Frontend

**组合式API (Composition API)**:
```typescript
import { ref, computed } from 'vue'

export function useTaskQueue() {
  const tasks = ref<Task[]>([])

  const addTask = (task: Task) => {
    tasks.value.push(task)
  }

  const taskCount = computed(() => tasks.value.length)

  return { tasks, addTask, taskCount }
}
```

**API服务封装**:
```typescript
export const ttsService = {
  async createTask(request: TaskCreateRequest): Promise<Task> {
    const response = await axios.post('/api/v1/tts/generate', request)
    return response.data
  }
}
```

## Environment Variables

### Backend (.env)
```bash
DATABASE_URL=sqlite+aiosqlite:///data/tts_history.db
LOG_LEVEL=INFO
MAX_QUEUE_SIZE=10
MAX_HISTORY_SIZE=20
OUTPUT_DIR=output
LOG_DIR=logs
```

### Frontend (.env.development)
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=离线文字转语音工具
```

## Testing Strategy

### Backend
- **单元测试**: pytest + pytest-asyncio
- **集成测试**: TestClient (FastAPI)
- **契约测试**: OpenAPI规范验证

### Frontend
- **单元测试**: Vitest
- **组件测试**: Vitest + Vue Test Utils
- **E2E测试**: Playwright (可选)

## Key Files Reference

### Backend
- `backend/src/main.py` - 应用入口
- `backend/src/models/task.py` - 任务数据模型
- `backend/src/services/tts_service.py` - TTS核心服务
- `backend/src/api/tts.py` - TTS API端点
- `backend/src/core/database.py` - 数据库配置

### Frontend
- `frontend/src/main.ts` - 应用入口
- `frontend/src/views/Home.vue` - 主页面
- `frontend/src/services/tts.ts` - TTS API服务
- `frontend/src/stores/queue.ts` - 队列状态管理
- `frontend/vite.config.ts` - Vite配置

## Troubleshooting

### Common Issues

1. **SQLite数据库锁定**:
   - 确保只有一个进程写入数据库
   - 使用`check_same_thread=False`配置

2. **CORS错误**:
   - 检查FastAPI CORS中间件配置
   - 确保前端URL在`allow_origins`中

3. **edge-tts首次使用慢**:
   - 首次使用需要下载音色模型(~50-100MB)
   - 耐心等待下载完成

4. **TypeScript类型错误**:
   - 运行`npm run type-check`
   - 确保所有导入都有类型定义

## Related Documentation

- [Feature Specification](./specs/001-offline-tts/spec.md)
- [Implementation Plan](./specs/001-offline-tts/plan.md)
- [Technical Research](./specs/001-offline-tts/research.md)
- [Data Model](./specs/001-offline-tts/data-model.md)
- [API Documentation](./specs/001-offline-tts/contracts/openapi.yaml)
- [Quick Start Guide](./specs/001-offline-tts/quickstart.md)

---

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
