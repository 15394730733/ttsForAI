<!--
Sync Impact Report:
Version change: INITIAL → 1.0.0
List of modified principles: N/A (Initial version)
Added sections:
  - Core Principles (5 principles)
  - Technology Stack Requirements
  - Development Workflow
Removed sections: N/A
Templates requiring updates:
  ✅ plan-template.md - Aligned with technology stack requirements
  ✅ spec-template.md - No updates needed
  ✅ tasks-template.md - No updates needed
Follow-up TODOs: None
-->

# TTS (Text-to-Speech) Constitution

## Core Principles

### I. 简单至上 (Simplicity First)

系统架构必须保持简洁明了,避免不必要的复杂性。每个模块都应有明确的单一职责,优先选择最直观的实现方案。

**规则:**
- 任何新增功能都必须有明确的业务需求支撑,不得为"未来可能"的需求预留代码
- 优先使用成熟、广泛采用的库和框架,避免重复造轮子
- 代码复杂度必须随功能需求自然增长,而非过早优化
- 对于有多个实现方案的问题,选择最容易理解和维护的方案

**理由:** 简单的代码更容易理解、测试和维护,减少bug产生,提升开发效率

### II. 用户体验优先 (User Experience First)

文字转语音工具的核心价值在于提供流畅、直观的语音合成体验。所有技术决策都必须以用户体验为出发点。

**规则:**
- 前端界面必须简洁、响应迅速,提供实时反馈
- 语音生成过程必须透明,显示明确的进度提示
- 错误信息必须友好、可操作,避免技术术语
- 支持常见格式和常见使用场景,满足90%用户的日常需求

**理由:** 良好的用户体验是工具成功的关键,技术应服务于用户需求

### III. 技术栈现代化 (Modern Technology Stack)

使用最新的稳定版本技术栈,确保项目可维护性和安全性,同时享受新特性带来的开发效率提升。

**规则:**
- **前端:** Vue 3.x + TypeScript 5.x + Vite 5.x (构建工具)
- **后端:** Python 3.12+ (最新稳定版)
- **依赖管理:** 前端使用 npm/pnpm,后端使用 poetry/pip
- **API标准:** RESTful API,遵循OpenAPI 3.0规范
- **所有依赖必须使用最新稳定版本**,定期更新并记录在CHANGELOG中

**理由:** 现代技术栈提供更好的类型安全、性能和开发体验,降低长期维护成本

### IV. 接口契约优先 (Interface Contracts)

前后端之间必须定义清晰的API契约,所有接口变更必须遵循版本化原则。

**规则:**
- 所有API端点必须有明确的请求/响应Schema定义
- 使用OpenAPI/Swagger文档作为唯一真实来源
- 接口变更必须遵循语义化版本控制(SEMVER)
- 向后兼容性破坏必须通过主版本号升级体现
- 前端和后端可以基于契约独立开发和测试

**理由:** 清晰的契约使前后端解耦,支持并行开发,减少集成问题

### V. 可测试性 (Testability)

代码必须易于测试,核心逻辑必须有相应的测试覆盖。

**规则:**
- 业务逻辑必须与UI/基础设施分离,便于单元测试
- 关键API端点必须有集成测试
- TTS核心功能必须有端到端测试验证
- 测试代码必须易于阅读和维护,测试用例命名清晰

**理由:** 测试是代码质量的保证,防止回归,支持重构

## Technology Stack Requirements

### 前端技术栈

- **框架:** Vue 3.x (Composition API)
- **语言:** TypeScript 5.x
- **构建工具:** Vite 5.x
- **状态管理:** Pinia (如需)
- **UI组件库:** Element Plus / Naive UI (根据实际需求选择)
- **HTTP客户端:** Axios / Fetch API
- **代码规范:** ESLint + Prettier

### 后端技术栈

- **语言:** Python 3.12+
- **框架:** FastAPI (最新稳定版)
- **TTS引擎:** 优先选择edge-tts / pyttsx3 / gTTS (根据需求确定)
- **异步处理:** asyncio / aiofiles
- **API文档:** FastAPI自动生成的OpenAPI文档
- **CORS:** fastapi-cors-middleware
- **环境配置:** python-dotenv
- **代码规范:** Black + Ruff + mypy

### 依赖管理原则

- 所有依赖必须在首次安装时固定版本号
- 定期(至少每月)检查并更新依赖到最新稳定版本
- 使用自动化工具监控安全漏洞
- 依赖变更必须在PR中明确说明原因和影响

## Development Workflow

### 代码提交流程

1. **功能开发:** 基于spec.md创建feature分支
2. **代码审查:** 所有代码必须经过review才能合并
3. **测试验证:** 必须通过所有测试(包括人工测试)
4. **文档更新:** API变更必须更新OpenAPI文档
5. **提交信息:** 遵循Conventional Commits规范

### 质量门禁

- [ ] 代码通过Linter检查(前端ESLint,后端Black/Ruff)
- [ ] TypeScript类型检查无错误(前端mypy --strict,后端类型检查)
- [ ] 所有测试通过
- [ ] API文档与实现一致
- [ ] 无已知安全漏洞

### 版本发布

- **版本号:** 遵循语义化版本(MAJOR.MINOR.PATCH)
- **CHANGELOG:** 每次发布必须更新CHANGELOG.md
- **标签:** 每个发布版本必须打Git tag
- **向后兼容:** MINOR和PATCH版本必须保持向后兼容

## Governance

**章程权威性:** 本章程是项目开发的最高准则,所有技术决策和代码实现都必须遵循。当出现争议时,以本章程为准。

**修订流程:**
1. 任何团队成员都可以提出修订建议
2. 修订必须说明理由和预期影响
3. 重大修订(MAJOR版本)需要团队讨论和共识
4. 修订后必须更新本文件,并记录版本历史
5. 修订必须同步更新到所有相关模板和指南文档

**合规审查:**
- 每个PR合并前必须确认符合章程要求
- 每个迭代(冲刺)结束时进行章程合规审查
- 发现违规情况必须记录并计划修正

**复杂度说明:**
- 引入新的依赖必须说明必要性
- 增加抽象层次必须解决具体问题
- 任何模式或架构的使用必须有清晰的理由

**运行时指南:**
- 开发过程中的具体技术指导见项目README.md
- API设计参考OpenAPI文档
- 代码风格参考工程配置文件(.eslintrc, pyproject.toml等)

**Version**: 1.0.0 | **Ratified**: 2026-01-23 | **Last Amended**: 2026-01-23
