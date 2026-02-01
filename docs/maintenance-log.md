# TTS离线工具 - 维护与开发记录

> 文档创建日期：2026-02-01
> 项目分支：001-offline-tts

---

## 📝 本次维护操作

### 日志文件清理 (2026-02-01)

**操作目的：** 清理项目运行过程中累积的临时日志文件

**已删除文件：**
```
logs/
└── tts_app.log                          [已删除]

根目录日志文件：
├── server_final.log                      [已删除]
├── server_reload.log                     [已删除]
├── server_test.log                       [已删除]
├── server_8001.log                       [已删除]
├── server_new.log                        [已删除]
├── server.log                            [已删除]
└── test_output.log                       [已删除]

backend/logs/
├── tts_app.log                           [使用中，保留]
└── tts_app.log.2026-01-{25..29}         [已删除 5 个归档文件]
```

**清理结果：**
- ✅ 删除了 **14 个日志文件**
- ⚠️ 保留当前活动的日志文件（因进程占用）

---

## 🎯 项目当前状态

### 技术栈概览

| 类别 | 技术 | 版本 | 状态 |
|------|------|------|------|
| **后端语言** | Python | 3.12+ | ✅ 稳定 |
| **Web框架** | FastAPI | Latest | ✅ 运行中 |
| **TTS引擎** | edge-tts | - | ✅ 正常 |
| **数据库** | SQLite + aiosqlite | 3.x | ✅ 异步支持 |
| **ORM** | SQLAlchemy | 2.0+ | ✅ 已配置 |
| **前端框架** | Vue.js | 3.x | ✅ 就绪 |
| **前端语言** | TypeScript | 5.x | ✅ 配置完成 |
| **构建工具** | Vite | 5.x | ✅ 就绪 |
| **UI组件库** | Element Plus | Latest | ✅ 已集成 |

### 核心功能实现状态

| 功能模块 | 状态 | 说明 |
|---------|------|------|
| TTS音频生成 | ✅ 完成 | 基于 edge-tts，支持多种中文音色 |
| 任务队列管理 | ✅ 完成 | 异步FIFO队列，最大容量10 |
| 历史记录 | ✅ 完成 | 最多保留20条记录 |
| RESTful API | ✅ 完成 | OpenAPI 3.0 文档自动生成 |
| 前后端分离 | ✅ 完成 | CORS已配置 |
| 日志系统 | ✅ 完成 | 文件滚动日志 |

---

## 📂 项目结构

```
ttsForAI/
├── backend/                      # Python FastAPI 后端
│   ├── src/
│   │   ├── api/                 # API路由
│   │   ├── models/              # SQLAlchemy 数据模型
│   │   ├── services/            # 业务逻辑层
│   │   ├── core/                # 核心配置
│   │   └── main.py              # 应用入口
│   ├── data/                    # SQLite 数据库
│   ├── output/                  # 生成的音频文件
│   ├── logs/                    # 日志文件目录
│   └── requirements.txt         # Python 依赖
│
├── frontend/                     # Vue.js + TypeScript 前端
│   ├── src/
│   │   ├── components/          # Vue 组件
│   │   ├── views/               # 页面视图
│   │   ├── services/            # API 服务封装
│   │   ├── stores/              # Pinia 状态管理
│   │   ├── types/               # TypeScript 类型
│   │   ├── utils/               # 工具函数
│   │   ├── App.vue              # 根组件
│   │   └── main.ts              # 应用入口
│   └── package.json             # npm 配置
│
├── specs/                        # 功能规格文档
│   └── 001-offline-tts/
│       ├── spec.md              # 功能规格
│       ├── plan.md              # 实现计划
│       ├── research.md          # 技术调研
│       ├── tasks.md             # 任务清单
│       └── contracts/           # API 契约
│
├── docs/                         # 项目文档
│   └── maintenance-log.md       # 本文档
│
├── CLAUDE.md                     # 项目开发指南
└── README.md                     # 项目说明
```

---

## 🔧 开发命令速查

### 后端 (Python)

```bash
# 激活虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r backend/requirements.txt

# 启动开发服务器（自动重载）
uvicorn backend.src.main:app --reload --port 8000

# 运行测试
pytest

# 代码格式化
black backend/src/

# 类型检查
mypy backend/src/
```

### 前端 (Vue.js + TypeScript)

```bash
# 安装依赖
npm install  # 或 pnpm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 运行测试
npm run test

# 代码检查
npm run lint
npm run format
```

---

## 🎨 可用音色

| 名称 | 音色ID | 类型 |
|------|--------|------|
| 晓晓 | zh-CN-XiaoxiaoNeural | 女声（默认） |
| 云扬 | zh-CN-YunyangNeural | 男声 |
| 晓悠 | zh-CN-XiaoyouNeural | 童声 |
| 晓伊 | zh-CN-XiaoyiNeural | 年轻女声 |
| 云健 | zh-CN-YunjianNeural | 沉稳男声 |

---

## 📊 环境配置

### 后端 (.env)
```bash
DATABASE_URL=sqlite+aiosqlite:///data/tts_history.db
LOG_LEVEL=INFO
MAX_QUEUE_SIZE=10
MAX_HISTORY_SIZE=20
OUTPUT_DIR=output
LOG_DIR=logs
```

### 前端 (.env.development)
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=离线文字转语音工具
```

---

## 🚀 快速启动指南

1. **后端启动**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn src.main:app --reload --port 8000
   ```
   访问 http://localhost:8000/docs 查看 API 文档

2. **前端启动**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   访问 http://localhost:5173 使用应用

---

## 📖 相关文档

- [功能规格说明](../specs/001-offline-tts/spec.md)
- [实现计划](../specs/001-offline-tts/plan.md)
- [API 契约](../specs/001-offline-tts/contracts/openapi.yaml)
- [快速开始指南](../specs/001-offline-tts/quickstart.md)
- [开发指南](../CLAUDE.md)

---

## 📌 维护建议

### 日常维护
- **日志清理：** 定期清理 `logs/` 目录下的归档日志文件
- **数据库备份：** 定期备份 `data/tts_history.db`
- **依赖更新：** 定期检查并更新 Python 和 npm 依赖

### 性能优化
- 监控任务队列长度，必要时调整 `MAX_QUEUE_SIZE`
- 定期清理超过 20 条的历史记录（自动执行）
- 音频文件定期清理 `output/` 目录

---

**文档版本：** v1.0
**最后更新：** 2026-02-01
**维护者：** AI Assistant
