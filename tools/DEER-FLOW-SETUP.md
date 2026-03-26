# DeerFlow 安装与使用指南

更新时间：2026-03-26

## 安装状态 ✅

### 已完成
- [x] 仓库克隆：`tools/deer-flow`
- [x] 系统依赖：nginx 已安装 (`brew install nginx`)
- [x] 配置生成：`make config` 已运行
- [x] 后端依赖：uv sync 完成 (Python 3.12.12)
- [x] 前端依赖：pnpm install 完成 (937 个包)

### 当前状态
- 位置：`/Users/a123456/.openclaw/workspace/tools/deer-flow`
- 版本：DeerFlow 2.0 (最新版)
- 访问地址：`http://localhost:2026` (启动后)

---

## 关键配置文件

### 1. config.yaml
位置：`tools/deer-flow/config.yaml`

这是主配置文件，你需要配置：
- **models**: 至少配置一个 LLM 模型
- **sandbox**: 沙箱模式 (本地/Docker)
- **skills**: 启用的技能

### 2. .env
位置：`tools/deer-flow/.env`

存放 API Key，当前是空的，你需要填入：
```bash
# 至少填一个模型 Key
OPENAI_API_KEY=your-key-here
# 或其他 provider
ANTHROPIC_API_KEY=your-key-here
VOLCENGINE_API_KEY=your-key-here
```

---

## 下一步：配置模型

### 推荐模型 (官方推荐)
DeerFlow 官方推荐使用：
1. **Doubao-Seed-2.0-Code** (字节火山引擎)
2. **DeepSeek v3.2**
3. **Kimi 2.5**

### 快速配置方案

#### 方案 A：用 OpenAI / OpenRouter
编辑 `config.yaml`，找到 `models:` 部分，取消注释并修改：

```yaml
models:
  - name: gpt-4
    display_name: GPT-4
    use: langchain_openai:ChatOpenAI
    model: gpt-4
    api_key: $OPENAI_API_KEY
    max_tokens: 4096
    temperature: 0.7
```

然后在 `.env` 文件添加：
```bash
OPENAI_API_KEY=sk-xxx
```

#### 方案 B：用 OpenRouter (访问更多模型)
```yaml
models:
  - name: openrouter-gemini-2.5-flash
    display_name: Gemini 2.5 Flash (OpenRouter)
    use: langchain_openai:ChatOpenAI
    model: google/gemini-2.5-flash-preview
    api_key: $OPENROUTER_API_KEY
    base_url: https://openrouter.ai/api/v1
```

```bash
OPENROUTER_API_KEY=sk-or-xxx
```

#### 方案 C：用字节火山引擎 (官方推荐)
```yaml
models:
  - name: doubao-seed-1.8
    display_name: Doubao-Seed-1.8
    use: deerflow.models.patched_deepseek:PatchedChatDeepSeek
    model: doubao-seed-1-8-251228
    api_base: https://ark.cn-beijing.volces.com/api/v3
    api_key: $VOLCENGINE_API_KEY
    supports_thinking: true
    supports_vision: true
```

```bash
VOLCENGINE_API_KEY=your-volcengine-key
```

---

## 启动方式

### 方案 1：本地开发模式 (推荐首次使用)
```bash
cd tools/deer-flow
make dev PYTHON=python3
```

访问：http://localhost:2026

### 方案 2：Docker 模式 (生产环境)
```bash
cd tools/deer-flow
make docker-init    # 首次需要拉取沙箱镜像
make docker-start   # 启动服务
```

访问：http://localhost:2026

### 方案 3：后台守护进程
```bash
cd tools/deer-flow
make dev-daemon PYTHON=python3
```

---

## 核心概念理解

### DeerFlow 是什么
DeerFlow 是一个 **Super Agent Harness**，定位是：
- 编排多个子 agent 完成复杂任务
- 支持长时间运行 (分钟到小时级)
- 有记忆、沙箱、技能、工具系统
- 适合深度研究、编码、自动化任务

### 与 OpenCLI / CLI-Anything 的区别

| 项目 | 定位 | 适合场景 |
|------|------|----------|
| **OpenCLI** | 现成 CLI Hub | 直接调用已有网站/工具能力 |
| **CLI-Anything** | CLI 生成器 | 把 GUI 软件变成 CLI |
| **DeerFlow** | Super Agent 编排平台 | 复杂多步骤任务、长时间运行、需要记忆/沙箱 |

### 三者配合方式
- **OpenCLI** → 提供"原子能力"(调用网站/API)
- **CLI-Anything** → 把内部工具包装成 CLI
- **DeerFlow** → 编排这些能力，完成复杂任务

---

## 推荐的首次使用流程

### 第 1 步：配置模型 Key
1. 编辑 `.env` 文件
2. 填入至少一个模型 API Key

### 第 2 步：启动服务
```bash
cd tools/deer-flow
make dev PYTHON=python3
```

### 第 3 步：访问 UI
打开浏览器：http://localhost:2026

### 第 4 步：测试一个简单任务
在 UI 里输入：
- "帮我搜索最新的 AI 新闻"
- "分析这个 GitHub 仓库的结构"

---

## 沙箱模式说明

DeerFlow 支持多种沙箱：

### 本地模式 (最简单)
- 代码直接在本地运行
- 无需 Docker
- 适合测试和简单任务

### Docker 模式 (推荐生产)
- 任务在隔离容器里跑
- 更安全
- 需要 `make setup-sandbox` 预拉镜像

### Kubernetes 模式 (企业级)
- 通过 provisioner 服务管理
- 适合大规模部署

---

## 常用命令速查

```bash
# 检查依赖
make check PYTHON=python3

# 安装依赖
make install PYTHON=python3

# 启动开发模式
make dev PYTHON=python3

# 启动后台模式
make dev-daemon PYTHON=python3

# 停止服务
make stop

# 拉取沙箱镜像
make setup-sandbox

# Docker 模式启动
make docker-start

# 查看配置版本
grep config_version config.yaml

# 升级配置 (官方更新后)
make config-upgrade
```

---

## 当前待办事项

### 必须做
1. **编辑 `.env` 文件** → 填入至少一个模型 API Key
2. **编辑 `config.yaml`** → 启用至少一个模型配置

### 可选做
1. 预拉沙箱镜像：`make setup-sandbox`
2. 测试启动：`make dev PYTHON=python3`
3. 访问 UI 验证：http://localhost:2026

---

## 官方资源

- **官网**: https://deerflow.tech
- **GitHub**: https://github.com/bytedance/deer-flow
- **中文文档**: `README_zh.md`
- **贡献指南**: `CONTRIBUTING.md`
- **字节Coding Plan**: 可用免费额度跑 Doubao/DeepSeek/Kimi

---

## 我的建议

### 如果你想快速体验
1. 用 OpenRouter + Gemini 2.5 Flash (便宜、快)
2. 本地模式启动 (`make dev`)
3. 先在 UI 里跑几个简单任务

### 如果你想认真用
1. 申请字节火山引擎 Coding Plan (有免费额度)
2. 配置 Doubao-Seed-2.0-Code
3. 用 Docker 沙箱模式
4. 把常用技能配置好

### 如果和 OpenCLI/CLI-Anything 配合
- DeerFlow 作为"大脑"编排复杂任务
- OpenCLI 作为"手"调用外部能力
- CLI-Anything 把内部工具包装成 CLI 供 DeerFlow 调用

---

**下一步你告诉我**：
1. 想用哪个模型 provider (OpenAI / OpenRouter / 火山引擎 / 其他)
2. 想现在启动试试，还是先配置完再说

我可以直接帮你改配置文件。
