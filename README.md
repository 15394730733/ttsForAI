# 离线文字转语音工具 (TTS)

<div align="center">

**一个功能强大的离线文字转语音工具**

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.x-green)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[功能特性](#功能特性) • [快速开始](#快速开始) • [使用指南](#使用指南) • [文档](#文档) • [常见问题](#常见问题)

</div>

---

## 📖 项目简介

离线文字转语音工具是一款基于 edge-tts 引擎的文字转语音（TTS）工具，可以将中文或中英文混合文本转换为高质量的 MP3 音频文件。

### 核心特点

- ✅ **完全离线** - 无需互联网连接，本地运行，数据安全
- ✅ **多种音色** - 内置5种高质量中文音色（女声、男声、童声等）
- ✅ **参数自定义** - 支持调节语速、音调、音量
- ✅ **任务队列** - 智能队列管理，支持批量生成
- ✅ **历史记录** - 自动保存生成历史，方便重新下载
- ✅ **现代界面** - 基于 Vue 3 的响应式 Web 界面
- ✅ **安全可靠** - 完整的错误处理和安全防护

### 技术栈

#### 后端
- **Python** 3.12+ - 现代化的 Python 版本
- **FastAPI** - 高性能异步 Web 框架
- **SQLAlchemy** 2.0 + SQLite - 异步 ORM 和轻量级数据库
- **edge-tts** - 微软 Edge 浏览器的 TTS 引擎
- **asyncio** - 异步任务处理

#### 前端
- **Vue** 3 - 渐进式 JavaScript 框架
- **TypeScript** 5.x - 类型安全的 JavaScript
- **Vite** 5.x - 快速的构建工具
- **Element Plus** - 成熟的 Vue 3 UI 组件库
- **Pinia** - 官方状态管理方案

## 📁 项目结构

```
tts/
├── backend/                   # 后端服务 (Python/FastAPI)
│   ├── src/
│   │   ├── api/              # API路由端点
│   │   │   ├── tts.py        # TTS生成API
│   │   │   ├── queue.py      # 任务队列API
│   │   │   ├── history.py    # 历史记录API
│   │   │   └── health.py     # 健康检查API
│   │   ├── models/           # SQLAlchemy数据模型
│   │   │   ├── task.py       # 任务模型
│   │   │   └── history.py    # 历史记录模型
│   │   ├── services/         # 业务逻辑服务
│   │   │   ├── tts_service.py        # TTS引擎封装
│   │   │   ├── queue_service.py      # 任务队列管理
│   │   │   ├── storage_service.py    # 文件存储管理
│   │   │   └── history_service.py    # 历史记录管理
│   │   └── core/             # 核心配置和工具
│   │       ├── config.py     # 配置管理
│   │       ├── database.py   # 数据库连接
│   │       ├── logger.py     # 日志配置
│   │       └── security.py   # 安全验证
│   ├── tests/                # 测试文件
│   │   ├── unit/             # 单元测试
│   │   ├── integration/      # 集成测试
│   │   └── contract/         # API契约测试
│   ├── data/                 # SQLite数据库文件
│   ├── output/               # 生成的音频文件
│   ├── logs/                 # 日志文件
│   ├── docs/                 # API文档
│   └── requirements.txt      # Python依赖
├── frontend/                  # 前端应用 (Vue 3)
│   ├── src/
│   │   ├── components/       # Vue组件
│   │   │   ├── TTSInput.vue      # 文本输入组件
│   │   │   ├── VoiceParams.vue   # 语音参数组件
│   │   │   ├── QueueStatus.vue   # 队列状态组件
│   │   │   └── HistoryList.vue   # 历史记录组件
│   │   ├── views/            # 页面视图
│   │   │   ├── Home.vue          # 主页面
│   │   │   └── History.vue       # 历史记录页面
│   │   ├── services/         # API服务封装
│   │   │   ├── tts.ts            # TTS API
│   │   │   ├── queue.ts          # 队列API
│   │   │   └── history.ts        # 历史记录API
│   │   ├── stores/           # Pinia状态管理
│   │   │   ├── queue.ts          # 队列状态
│   │   │   └── history.ts        # 历史记录状态
│   │   └── router/           # Vue Router路由
│   └── tests/                # 测试文件
├── docs/                      # 项目文档
│   ├── user-guide.md         # 用户使用手册
│   └── deployment.md         # 部署文档
├── specs/                     # 功能规范文档
│   └── 001-offline-tts/
│       ├── spec.md           # 功能规格说明
│       ├── plan.md           # 实施计划
│       └── tasks.md          # 任务分解
├── scripts/                   # 工具脚本
│   ├── deploy.sh             # 部署脚本
│   └── test-all.sh           # 测试脚本
├── README.md                  # 本文件
├── CHANGELOG.md               # 变更日志
└── LICENSE                    # 许可证
```

## 🚀 快速开始

### 环境要求

- **Python** 3.10 或更高版本
- **Node.js** 18 或更高版本
- **npm** 或 **pnpm**

### 方式1: 使用setup脚本（推荐）

#### Windows用户

```bash
# 运行安装脚本
setup.bat

# 启动服务
cd backend
start_server.bat

# 新终端窗口
cd frontend
npm run dev
```

#### Linux/macOS用户

```bash
# 赋予执行权限并运行
chmod +x setup.sh
./setup.sh

# 启动后端
cd backend
source venv/bin/activate
uvicorn src.main:app --reload

# 新终端窗口启动前端
cd frontend
npm run dev
```

### 方式2: 手动安装

#### 步骤1: 安装后端依赖

```bash
cd backend

# 创建Python虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python -c "from src.core.database import init_database; import asyncio; asyncio.run(init_database())"
```

#### 步骤2: 安装前端依赖

```bash
cd frontend

# 安装npm依赖
npm install

# 或使用pnpm
pnpm install
```

#### 步骤3: 启动开发服务器

**启动后端服务**（终端1）:
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn src.main:app --reload --port 8000
```

**启动前端服务**（终端2）:
```bash
cd frontend
npm run dev
```

#### 步骤4: 访问应用

打开浏览器访问: **http://localhost:5173**

后端API文档: **http://localhost:8000/docs**

---

## ✨ 功能特性

### 核心功能

#### 🎙️ 文本转语音
- 支持中文和中英文混合文本
- 输出高质量 MP3 音频（128kbps, 44.1kHz）
- 文本长度支持：1-5000字符
- 自动过滤特殊字符和控制字符

#### 🎨 多种音色
提供5种预设中文音色：

| 音色 | ID | 特点 |
|------|-----|------|
| 晓晓-女声 | zh-CN-XiaoxiaoNeural | 温柔女声（默认） |
| 云扬-男声 | zh-CN-YunyangNeural | 成熟男声 |
| 晓悠-童声 | zh-CN-XiaoyouNeural | 活泼童声 |
| 晓伊-年轻女声 | zh-CN-XiaoyiNeural | 青春女声 |
| 云健-沉稳男声 | zh-CN-YunjianNeural | 沉稳男声 |

#### 🎛️ 语音参数自定义
- **语速**: 0.5x - 2.0x（默认1.0x）
- **音调**: 0.5x - 2.0x（默认1.0x）
- **音量**: 0% - 100%（默认100%）
- 一键重置参数功能

#### 📋 任务队列管理
- FIFO队列，最多10个任务
- 实时显示队列状态（排队/处理/完成）
- 支持取消排队中的任务
- 自动顺序处理

#### 📚 历史记录
- 自动保存最近20条生成记录
- 显示文本摘要和参数
- 支持重新下载历史音频
- 支持删除单条或全部记录
- 自动清理超限记录（FIFO）

#### 🔒 安全防护
- 文本长度验证
- 路径遍历防护
- 命令注入防护
- 特殊字符过滤
- 完整的错误处理

#### 📊 日志监控
- 任务生命周期日志
- 错误日志追踪
- 日志文件自动滚动（每天）
- 控制台+文件双输出

---

## 📖 使用指南

### 基础使用流程

1. **输入文本**
   - 在文本框中输入或粘贴文字（最多5000字符）
   - 实时显示字符计数

2. **选择音色**
   - 从下拉菜单选择合适的音色
   - 默认使用"晓晓-女声"

3. **调整参数**（可选）
   - 调节语速、音调、音量
   - 或使用"重置参数"恢复默认值

4. **生成语音**
   - 点击"生成语音"按钮
   - 在"队列状态"中查看进度

5. **下载音频**
   - 生成完成后点击"下载音频"
   - 文件保存到浏览器下载目录

### 批量生成

1. 生成第一段文本后，不要关闭页面
2. 修改文本内容继续生成
3. 所有任务自动排队处理
4. 最多支持10个排队任务

更多使用技巧请参考 [用户使用手册](./docs/user-guide.md)

---

## 💻 开发指南

### 代码规范

#### 后端（Python）

```bash
cd backend

# 代码格式化
black src/

# Linter检查
ruff check src/

# 类型检查
mypy src/
```

#### 前端（TypeScript/Vue）

```bash
cd frontend

# Lint检查
npm run lint

# 自动修复
npm run lint:fix

# 格式化
npm run format
```

### 运行测试

#### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 带覆盖率
pytest --cov=src tests/

# 详细输出
pytest -v

# 运行特定测试
pytest tests/unit/test_tts_service.py
```

**测试覆盖率**:
- 总体: 70%
- 数据模型: 88-100%
- 核心服务: 68-94%
- API层: 65-97%

#### 前端测试

```bash
cd frontend

# 运行单元测试
npm run test

# 测试覆盖率
npm run test:coverage

# UI模式
npm run test:ui
```

**测试统计**: 158个测试全部通过 ✅

### API文档

- **在线文档**: http://localhost:8000/docs
- **离线文档**: [backend/docs/api.md](./backend/docs/api.md)

### 数据库管理

```bash
# 初始化数据库
cd backend
python -c "from src.core.database import init_database; import asyncio; asyncio.run(init_database())"

# 查看数据库（使用DB Browser for SQLite）
# 文件位置: backend/data/tts_history.db
```

---

## 📚 文档

- [用户使用手册](./docs/user-guide.md) - 面向最终用户的详细指南
- [部署文档](./docs/deployment.md) - 生产环境部署指南
- [API文档](./backend/docs/api.md) - 完整的API参考
- [功能规格说明](./specs/001-offline-tts/spec.md) - 产品需求文档
- [实施计划](./specs/001-offline-tts/plan.md) - 技术实施方案
- [任务分解](./specs/001-offline-tts/tasks.md) - 开发任务列表
- [快速开始指南](./specs/001-offline-tts/quickstart.md) - 开发环境搭建

---

## ❓ 常见问题

<details>
<summary><b>Q: 首次使用音色为什么很慢？</b></summary>

A: 首次使用某个音色时需要下载音色模型文件（约50-100MB）。模型会缓存到本地，后续使用会快很多。请确保网络连接正常。
</details>

<details>
<summary><b>Q: 生成速度慢怎么办？</b></summary>

A:
- 检查文本长度（越长越慢）
- 关闭其他占用CPU的程序
- 首次使用音色需要下载模型
- 正常速度约50-100字符/秒
</details>

<details>
<summary><b>Q: 支持繁体中文吗？</b></summary>

A: 支持有限。建议转换为简体中文使用以获得最佳效果。
</details>

<details>
<summary><b>Q: 音质不理想怎么办？</b></summary>

A:
- 尝试调整语速（建议0.8-1.2）
- 尝试不同音色
- 调整音调参数
- 使用简体中文
</details>

<details>
<summary><b>Q: 历史记录会一直保存吗？</b></summary>

A: 系统自动保留最近20条记录，超过20条会自动删除最早的记录。建议及时下载重要音频。
</details>

更多问题请参考 [用户使用手册 - 常见问题](./docs/user-guide.md#常见问题)

---

## 🗺️ 路线图

### v1.0.0（当前版本）✅
- [x] 基础文字转语音功能
- [x] 5种预设音色
- [x] 语音参数调节
- [x] 任务队列管理
- [x] 历史记录功能
- [x] 错误处理和安全防护
- [x] 日志系统

### v1.1.0（计划中）
- [ ] 批量文本处理
- [ ] 音频格式转换（WAV, OGG）
- [ ] 实时预览功能
- [ ] 音频片段裁剪
- [ ] 音频合并功能

### v2.0.0（未来）
- [ ] 用户账户系统
- [ ] 云端同步
- [ ] 高级音频编辑
- [ ] 移动端应用

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发规范

- 遵循现有代码风格
- 添加必要的测试
- 更新相关文档
- 确保所有测试通过

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 👥 作者

- **主要开发者**: [Your Name]
- **技术栈**: Python + Vue 3
- **项目地址**: [GitHub Repository]

---

## 🙏 致谢

- [edge-tts](https://github.com/rany2/edge-tts) - 微软Edge TTS引擎的Python封装
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Element Plus](https://element-plus.org/) - 优秀的Vue 3 UI组件库

---

## 📞 联系方式

- **问题反馈**: [GitHub Issues](https://github.com/your-repo/issues)
- **功能建议**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **邮件**: your-email@example.com

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐ Star！**

Made with ❤️ by [Your Name]

</div>


