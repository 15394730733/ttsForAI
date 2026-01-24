# Implementation Plan: 离线文字转语音工具

**Branch**: `001-offline-tts` | **Date**: 2026-01-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-offline-tts/spec.md`

## Summary

本功能旨在实现一个离线版本的文字转语音工具,允许用户输入文本,设置语音参数(语速、音调、音量、音色),生成MP3格式音频文件并下载。系统采用前后端分离架构,后端使用Python 3.10+ + FastAPI + edge-tts引擎,前端使用Vue.js 3.x构建单页应用。支持任务队列管理、生成历史记录(最近20条,SQLite存储)、基础日志记录和错误处理。MVP阶段聚焦核心单文本转换功能,批量处理延后至v2.0版本。

## Technical Context

**Backend/Version**: Python 3.10+ (根据clarification,建议升级到3.12+以满足constitution要求)
**Frontend/Version**: Vue 3.x + TypeScript 5.x + Vite 5.x
**Primary Dependencies**:
- 后端: FastAPI (最新稳定版), edge-tts (TTS引擎), SQLAlchemy (SQLite ORM), asyncio (异步处理)
- 前端: Vue 3 (Composition API), Pinia (状态管理), Axios (HTTP客户端), Element Plus (UI组件库)

**Storage**: SQLite数据库 (data/tts_history.db) + 本地文件系统 (output/音频文件, logs/日志文件)

**Testing**: pytest (后端集成测试), Vitest (前端单元测试)

**Target Platform**:
- 后端: Windows/Linux/macOS (Python 3.10+)
- 前端: 现代浏览器 (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)

**Project Type**: web (前后端分离架构)

**Performance Goals**:
- 单次文本转换(<500字符)生成时间不超过10秒
- 用户完成全流程(输入→生成→下载)不超过30秒
- 任务队列处理采用FIFO模式,最多支持10个排队任务

**Constraints**:
- 单次文本转换最大长度5000字符
- 音频文件格式: MP3 (128kbps比特率, 44.1kHz采样率)
- 历史记录最多保存20条(FIFO自动清理)
- 音色选择: 预设3-5个中文音色(女声/男声/童声)
- 完全离线运行,不依赖在线TTS服务

**Scale/Scope**:
- 单用户本地应用
- 支持中英文混合文本朗读
- 任务队列最大10个任务
- 历史记录最多20条
- 日志文件按日期滚动存储

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

根据 `.specify/memory/constitution.md` 中的五大核心原则进行合规性检查:

### 初始检查 (Phase 0 前)

- [x] **I. 简单至上**: ✅ 通过
- [x] **II. 用户体验优先**: ✅ 通过
- [ ] **III. 技术栈现代化**: ⚠️ 需调整 (Python 3.10+ → 3.12+)
- [ ] **IV. 接口契约优先**: ⚠️ 待Phase 1完成
- [ ] **V. 可测试性**: ⚠️ 待Phase 1完成

**Gate Status**: ⚠️ **有条件通过** - 需在Phase 0解决Python版本问题

---

### 最终检查 (Phase 1 完成后) ✅

- [x] **I. 简单至上**:
  - ✅ 架构设计简洁:前后端分离,SQLite轻量存储,无过度抽象
  - ✅ MVP聚焦核心功能,批量处理延后至v2.0
  - ✅ 优先使用成熟库:FastAPI, Vue.js, edge-tts, SQLAlchemy
  - ✅ 使用asyncio.Queue而非Celery/RQ,避免过度设计

- [x] **II. 用户体验优先**:
  - ✅ 前端界面简洁响应:Vue 3 SPA,实时反馈
  - ✅ 生成过程透明:任务队列状态显示,进度提示
  - ✅ 错误信息友好:具体错误信息+解决建议(FR-011)
  - ✅ 支持常见场景:中英文混合,多种音色,参数自定义

- [x] **III. 技术栈现代化**:
  - ✅ **Python版本已升级到3.12+** (research.md已验证)
  - ✅ 前端: Vue 3.x + TypeScript 5.x + Vite 5.x
  - ✅ 后端框架: FastAPI (最新稳定版)
  - ✅ API标准: RESTful API, OpenAPI 3.0规范(已生成文档)
  - ✅ 依赖管理: 后端使用pip/poetry,前端使用npm/pnpm

- [x] **IV. 接口契约优先**:
  - ✅ **已定义清晰的API契约** (contracts/openapi.yaml)
  - ✅ **已生成完整的OpenAPI 3.0规范**
  - ✅ **已提供API使用指南** (contracts/api-guide.md)
  - ✅ 使用FastAPI自动生成OpenAPI文档
  - ✅ 将遵循语义化版本控制(SEMVER)

- [x] **V. 可测试性**:
  - ✅ 业务逻辑与UI分离:前后端解耦架构
  - ✅ **数据模型已定义** (data-model.md)
  - ✅ **测试策略已明确**: pytest (后端) + Vitest (前端)
  - ✅ 核心API将有集成测试(在quickstart.md中说明)
  - ✅ TTS核心功能将有端到端测试

**Technology Stack Requirements Check:**

- [x] 前端技术栈: Vue 3.x, TypeScript 5.x, Vite 5.x ✅
- [x] 后端技术栈: Python 3.12+, FastAPI ✅ (已升级)
- [x] TTS引擎: edge-tts ✅
- [x] API标准: RESTful API, OpenAPI 3.0规范 ✅ (已完成)
- [x] 代码规范: ESLint + Prettier (前端), Black + Ruff + mypy (后端) ✅ (已在CLAUDE.md中定义)

**Final Gate Status**: ✅ **完全通过** - 所有Constitution要求已满足,可继续Phase 2

## Project Structure

### Documentation (this feature)

```text
specs/001-offline-tts/
├── spec.md              # Feature specification
├── plan.md              # This file (Implementation plan)
├── research.md          # Phase 0 output (Technical research)
├── data-model.md        # Phase 1 output (Data model & Schema)
├── quickstart.md        # Phase 1 output (Quick start guide)
├── contracts/           # Phase 1 output (API contracts)
│   ├── openapi.yaml    # OpenAPI 3.0 specification
│   └── api-guide.md    # API usage guide
└── tasks.md             # Phase 2 output (Task breakdown - NOT created yet)
```

### Source Code (repository root)

```text
# Web application structure (前后端分离)
backend/
├── src/
│   ├── api/              # FastAPI路由和端点
│   │   ├── __init__.py
│   │   ├── tts.py        # TTS生成API
│   │   ├── queue.py      # 任务队列API
│   │   ├── history.py    # 历史记录API
│   │   └── health.py     # 健康检查API
│   ├── models/           # SQLAlchemy数据模型
│   │   ├── __init__.py
│   │   ├── task.py       # 任务模型
│   │   └── history.py    # 历史记录模型
│   ├── services/         # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── tts_service.py    # TTS引擎封装
│   │   ├── queue_service.py  # 任务队列管理
│   │   ├── storage_service.py # 文件存储管理
│   │   └── history_service.py # 历史记录管理
│   ├── core/             # 核心配置和工具
│   │   ├── __init__.py
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
│   ├── tts_history.db    # SQLite数据库
│   └── migrations/       # 数据库迁移脚本
├── output/               # 生成的音频文件
├── logs/                 # 日志文件
├── requirements.txt      # Python依赖
├── pyproject.toml        # 项目配置(Black/Ruff/mypy)
└── .env.example          # 环境变量示例

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

**Structure Decision**: 选择前后端分离的Web应用结构(Option 2)。backend目录包含FastAPI后端服务,frontend目录包含Vue.js前端应用。这种结构符合convention要求的前后端独立开发和部署,支持清晰的接口契约,便于并行开发和测试。

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Python版本3.10+ (vs 3.12+) | Spec在澄清阶段已确定为3.10+,而Constitution要求3.12+ | Constitution要求3.12+以获得最新特性和长期支持,3.10+仍有效但不是最新稳定版。建议升级到3.12+以满足Constitution。 |

**Phase 0 Action**: 需在research.md中研究Python 3.10+到3.12+的迁移影响和最佳实践。

---

## Phase 0: Research & Technical Decisions

**Objective**: Resolve all NEEDS CLARIFICATION items and validate technical choices

**Status**: 🔄 In Progress

**Research Tasks**:
1. Python版本升级: 3.10+ → 3.12+ (迁移指南,兼容性检查)
2. edge-tts引擎最佳实践 (音色列表,性能优化,错误处理)
3. FastAPI + SQLite异步操作最佳实践
4. Vue 3 + TypeScript + Vite项目脚手架和最佳实践
5. 任务队列实现方案 (asyncio队列 vs 第三方库如Celery/RQ)
6. Element Plus vs Naive UI组件库选择

**Output**: `research.md` - Technical research findings and decisions

---

## Phase 1: Design & Contracts

**Objective**: Define data models, API contracts, and integration patterns

**Status**: ⏳ Pending (waiting for Phase 0)

**Deliverables**:
- `data-model.md` - Database schema and entity relationships
- `contracts/openapi.yaml` - OpenAPI 3.0 specification
- `contracts/api-guide.md` - API usage documentation
- `quickstart.md` - Development setup and quick start guide
- Agent context update - Update AI agent context files

---

## Phase 2: Task Breakdown

**Objective**: Break down implementation into actionable tasks

**Status**: ⏳ Not started (will be executed by `/speckit.tasks`)

**Note**: This phase will be executed by the `/speckit.tasks` command, NOT by `/speckit.plan`.
