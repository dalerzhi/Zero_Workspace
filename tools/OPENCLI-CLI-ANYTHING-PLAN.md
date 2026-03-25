# OpenCLI + CLI-Anything 安装与使用规划

更新时间：2026-03-26

## 已完成安装

### 1. OpenCLI
- 仓库：`tools/opencli`
- 全局命令：`opencli`
- 版本：`1.4.1`
- 安装方式：`npm install -g @jackwener/opencli`

### 2. CLI-Anything
- 仓库：`tools/CLI-Anything`
- OpenClaw skill：`~/.openclaw/skills/cli-anything/SKILL.md`
- 安装方式：从仓库复制 `openclaw-skill/SKILL.md`

### 3. OpenCLI 浏览器扩展
- 已下载并解压到：`tools/opencli-extension/unpacked`
- zip 包：`tools/opencli-extension/opencli-extension.zip`

## 当前状态

### OpenCLI
- `opencli list`：正常
- `opencli doctor`：Daemon 正常，Chrome 扩展未连接
- 结论：
  - **Public / 外部 CLI Hub 命令可用**
  - **依赖浏览器登录态的网站命令暂不可用，需手动装扩展并启用**

### CLI-Anything
- 作为 OpenClaw skill 已可调用
- 适合用于：
  - 给 GUI 软件生成 CLI harness
  - 给源代码仓库生成 agent-native CLI
  - 迭代 refine / validate / test 某个现有 harness

## 两个项目的定位

### OpenCLI 是什么
OpenCLI 更像一个“现成工具运行层 / 统一 CLI Hub”：
- 直接调用现成站点适配器（如 HackerNews、Bilibili、Boss 等）
- 统一调用已有本地 CLI（如 gh、docker 等）
- 可复用 Chrome 登录态抓取站点数据
- 偏“拿来即用”

### CLI-Anything 是什么
CLI-Anything 更像一个“CLI 生成器 / Harness Builder”：
- 面向某个 GUI 软件或代码仓库
- 通过方法论生成一套新的 Python CLI
- 带命令结构、JSON 输出、REPL、测试、README
- 偏“把原本没有 CLI 的东西变成 CLI”

## 推荐分工

### 场景 A：要直接用现成网站/桌面应用能力
优先用 **OpenCLI**

示例：
- `opencli hackernews top --limit 10`
- `opencli gh pr list --limit 5`
- 未来扩展连通后：`opencli boss recommend`、`opencli xiaohongshu search ...`

### 场景 B：要把某个软件/仓库长期改造成 agent-native CLI
优先用 **CLI-Anything**

示例：
- 为某个 GUI 工具生成命令行控制层
- 为某个桌面软件做 REPL + JSON 输出 + 自动化测试
- 为内部项目做 harness，方便 OpenClaw/Codex/Claude Code 调用

## 下一步建议

### OpenCLI
1. 在 Chrome 里安装扩展
   - 打开 `chrome://extensions`
   - 开启开发者模式
   - 选择“加载已解压的扩展程序”
   - 目录选：`/Users/a123456/.openclaw/workspace/tools/opencli-extension/unpacked`
2. 安装完成后执行：
   - `opencli doctor`
3. 验证一个 public 命令 + 一个 browser 命令：
   - `opencli hackernews top --limit 3`
   - `opencli xiaohongshu search 充电宝`（需登录态）

### CLI-Anything
1. 选一个真实目标做首个 harness
2. 用 OpenClaw skill 发起生成
3. 产出目录放到 workspace 的独立子目录
4. 之后按 refine / validate / test 迭代

## 我建议的实际落地路线

### 第一阶段：把 OpenCLI 跑通
- 目的：把“外部网站/CLI 能力”先接起来
- 重点：扩展连接 + 登录态验证

### 第二阶段：选一个适合 CLI-Anything 的目标
优先选以下类型：
- 有 GUI、但没有好 CLI 的软件
- 有现成源代码仓库、适合包一层 agent harness
- Bill 日常高频会重复调用的内部工具

### 第三阶段：形成组合打法
- OpenCLI：负责“直接调用现成能力”
- CLI-Anything：负责“把没有 CLI 的东西变成 CLI”
- OpenClaw：负责调度、编排、长期使用

## 候选试点

### 候选 1：内部常用 GUI 工具
如果有重复操作的软件，可以用 CLI-Anything 包装

### 候选 2：某个开源桌面工具
拿一个 GUI 重、脚本化弱的项目做样板 harness

### 候选 3：招聘/内容/平台类站点自动化
如果主要目的是“直接取数和调用”，优先 OpenCLI，不必先造新 harness

## 常用命令

### OpenCLI
```bash
opencli --version
opencli list
opencli doctor
opencli hackernews top --limit 5
opencli gh pr list --limit 5
```

### CLI-Anything（在 OpenClaw 中）
```text
@cli-anything build a CLI for ./path/to/software
@cli-anything refine ./path/to/software
@cli-anything validate ./path/to/software
```

## 结论
- **OpenCLI：已经装好，差 Chrome 扩展最后一步。**
- **CLI-Anything：已经以 OpenClaw skill 形式装好。**
- **最佳策略不是二选一，而是配合使用。**
