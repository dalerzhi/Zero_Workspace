# MEMORY.md - 长期记忆

_最后更新：2026-03-10 06:46_

## 技能与工具

### Noiz Cloud TTS (云端语音 AI) ⭐
- **状态**: ✅ 已集成并投入使用
- **API Key**: `~/.noiz_api_key` (Base64 编码)
- **免费额度**: 100,000 字符
- **默认音色**: `dde1b9b5` - 故事讲述者（子轩）- 中文男声
- **推荐音色**:
  - 男声：`dde1b9b5` (子轩), `96270d87` (子轩), `8316cdf1` (亦辰)
  - 女声：`4f71a876` (小雨), `e47a10c4` (活泼小雨)
- **情感参数**: 小写格式 `{"happiness":0.7}`, `{"tenderness":0.6}`, `{"calm":0.8}`
- **文档**: `workspace/tts-output/DEBUG-SUMMARY.md`, `workspace/tts-output/FIX-RECORD.md`

### 飞书语音发送 (修复版) ✅
- **技能位置**: `skills/feishu-voice/SKILL.md`
- **依赖**: `ffmpeg` (brew), `ffprobe` (时长检测)
- **流程**: Noiz API → WAV → ffmpeg 转 OPUS → 自动检测时长 → 飞书 upload (带 duration) → 发送
- **关键修复**: 
  - OPUS 参数：16kHz, 单声道，24kbps (飞书优化)
  - 必须传递 `duration` 参数 (毫秒) 才能显示正确时长
  - 插件已修复：`extensions/feishu/src/media.ts` (自动检测时长)
- **备份文件**: `media.ts.backup.20260307_180813`

### STT (语音识别)
- Whisper CLI 已安装：`brew install openai-whisper`
- 用法：`whisper audio.ogg --model base --language zh --output_dir .`
- 模型位置：`~/.cache/whisper`

### Izwi (本地语音 AI)
- 状态：✅ 已安装 (v0.1.0-beta-5)
- 位置：`/Applications/Izwi.app` + CLI `/Users/a123456/.local/bin/izwi`
- 服务：`izwi serve` (运行在 http://127.0.0.1:8080)
- **TTS 音色**：
  - `Qwen3-TTS-12Hz-0.6B-Base` - 只有女声 ⚠️
  - `Qwen3-TTS-12Hz-1.7B-VoiceDesign-4bit` - 支持男声 ✅ (已下载)
  - 男声选项：`male-deep` (深沉), `male-narrator` (旁白), `male-calm` (平静), `male-warm` (温暖)
- **默认音色**：`male-deep` (深沉男声)

### Agent Reach (网络搜索第一优先) ⭐
- **重要**：网络搜索时优先使用 Agent Reach，而不是 web_search
- 状态：✅ 已安装 (v1.3.0)
- 位置：`~/.agent-reach/` + Python 包 `agent-reach`
- 诊断：`agent-reach doctor`
- 支持平台：
  - ✅ GitHub - 完整可用
  - ✅ YouTube - 字幕提取
  - ✅ RSS - 订阅源读取
  - ✅ 网页 - Jina Reader
  - ⬜ Twitter/X - 需配置 xreach
  - ⬜ 小红书 - 需配置 MCP
  - ⬜ 抖音 - 需配置 MCP
  - ⬜ LinkedIn - 需配置 MCP
  - ⬜ Boss 直聘 - 需配置 MCP
  - ⬜ 微信公众号 - 需配置工具

### Nano Banana Pro (图片生成)
- 状态：✅ 已安装
- 位置：`workspace/skills/nano-banana-pro/`
- 依赖：`uv` (已安装), Gemini API Key
- 用法：
  ```bash
  uv run skills/nano-banana-pro/scripts/generate_image.py \
    --prompt "描述" \
    --filename "输出.png" \
    --resolution 1K|2K|4K \
    --api-key "KEY"
  ```
- **API Key**：从 `~/.zshrc` 中的 `GEMINI_API_KEY` 读取

### Self-Improving Agent (自我改进)
- 状态：✅ 已安装
- 位置：`workspace/skills/self-improving-agent/`
- 日志目录：`workspace/.learnings/`
  - `LEARNINGS.md` - 纠正、知识缺口、最佳实践
  - `ERRORS.md` - 命令失败、异常
  - `FEATURE_REQUESTS.md` - 功能请求

### Aliyun Mail (阿里云邮箱) 📧
- 状态：✅ 已配置并投入使用
- 位置：`workspace/skills/aliyun-mail/`
- 功能：多邮箱 IMAP 收取、附件解析 (Word/Excel/PPT/PDF)、每日总结
- 依赖：`pip3 install --break-system-packages imap-tools python-docx openpyxl python-pptx pypdf`
- 配置邮箱：`zhibin@cheersucloud.com` (企业邮箱)
- 凭证：`.credentials/aliyun-mail.md` (chmod 600)
- 定时任务：每日 8:00 AM 自动运行 (`openclaw cron list` 查看)
- 用法：
  ```bash
  # 手动收取昨日邮件
  python3 skills/aliyun-mail/lib/fetch_emails.py --action summary --days 1
  
  # 收取指定日期范围
  python3 skills/aliyun-mail/lib/fetch_emails.py --action summary --since 2026-03-07 --until 2026-03-08
  
  # 测试连接
  python3 skills/aliyun-mail/lib/fetch_emails.py --action test
  ```
- 输出：`memory/YYYY-MM-DD-email-summary.md`
- 待完善：附件内容读取、飞书自动发送

### Insta360 Link 2 (USB 摄像头) 📷 ⭐
- **状态**: ✅ USB 直连，macOS 原生支持
- **调用方式**: `imagesnap` CLI (已安装 `/opt/homebrew/bin/imagesnap`)
- **查看设备**: `imagesnap -l`
- **可用设备**:
  - `Insta360 Link 2` ← 主用摄像头
  - `Insta360 Virtual Camera`
  - `"Daler's iPhone"的相机` (备选)
- **拍摄命令**:
  ```bash
  # 使用 Insta360 Link 2 拍摄
  imagesnap -d "Insta360 Link 2" -q high [输出文件.jpg]
  
  # 使用默认摄像头
  imagesnap -q high [输出文件.jpg]
  ```
- **重要**: 
  - `nodes camera_snap` 需要配对的节点设备（手机等），当前**无配对设备**
  - USB 摄像头直接用 `imagesnap` 命令，无需节点配对
  - 拍摄文件默认保存在 workspace 目录
- **配置位置**: `workspace/TOOLS.md` (详细配置)

## 重要经验
1. 每天早上先检查 `memory/` 目录和 `MEMORY.md`
2. 飞书语音技能已经就绪，可以直接用
3. TTS 测试用 `tts` 工具，音频会自动交付
4. ⚠️ 用户配置偏好必须记录到 MEMORY.md
5. ⭐ **网络搜索优先用 Agent Reach**
6. ⚠️ OpenClaw 配置的环境变量不会传递到 exec，需要从 `~/.zshrc` 读取
7. ⚠️ clawhub 安装常限流，用浏览器手动下载 zip
8. ⚠️ inference.sh 域名被墙，需要代理或手动下载
9. ⭐ **摄像头调用**: 用 `imagesnap` 命令 (USB 直连)，不是 `nodes camera_snap` (需要配对设备)

## 2026-03-09 - 自动整理

### 1. 用户需求
Conversation info (untrusted metadata): ```json {   "message_id": "om_x100b55d526ad4ca8b3443f73aceab8e",   "sender_id": "ou_7c6c3cdce8475c7a8de63811592c37f9",   "sender": "ou_7c6c3cdce8475c7a8de638115...

### 2. 完成的工作
目前无法读取邮件，原因是：  **Gmail 未配置认证** - `gog` 工具需要 OAuth 认证才能访问 Gmail - 当前没有存储任何 token (`gog auth list` 显示 "No tokens stored")  **需要配置才能读取邮件：**  ```bash # 配置 Gmail 访问 gog auth gmail ```  这会打开浏览器让你授权访问 Gmail。...

### 3. 用户需求
# 📧 邮件日报 (2026-03-09)  ## 概览 - 总邮件数：3 - 含附件：3  ## 重点邮件  ### 1. 回复：关于导入新防火墙品牌说明 **发件人**: junyi.cheng@cheersucloud.com **时间**: 2026-03-08 17:03 **附件**: 17553_InsertPic_FF70(03-02-15-32-35).png, InsertPi...

### 4. 用户需求
# 2026-03-08 - 周日  ## 📝 日志  _暂无手动记录_  ## 🔄 自动备份  - Git 提交：`1baf63a Auto backup: 2026-03-08 00:00:10`  --- **创建时间**: 2026-03-08 06:00 **状态**: 待填充

### 5. 用户需求
# 每日总结 - 2026-03-08  _自动生成于 2026-03-08 06:00:00_  ## 📈 今日统计  | 指标 | 数量 | |------|------| | Git 提交 | 1 | | 修改文件 | - | | 学习记录 | 0 | | 错误记录 | 0 | | 功能请求 | 0 | | MEMORY.md 更新 | true | | 待办事项 | 0 |  ## 📝 G...

### 6. 用户需求
{"type":"session","version":3,"id":"5aae7da1-9fc3-426c-bd8b-29f2e37f978d","timestamp":"2026-03-07T05:20:40.839Z","cwd":"/Users/a123456/.openclaw/workspace"} {"type":"model_change","id":"6aac5331","par...

### 7. 用户需求
{"type":"message","id":"286949dc","parentId":"512aef84","timestamp":"2026-03-07T09:07:24.509Z","message":{"role":"assistant","content":[{"type":"thinking","thinking":"需要查看飞书 outbound.ts 中 sendMediaFei...

### 8. 完成的工作
找到了！昨晚（3 月 7 日）的工作记录已经完整保存：  ## 📋 昨晚工作摘要（2026-03-07）  ### 主要任务：修复飞书语音时长显示问题  **问题**：飞书语音消息显示时长 `0:00`  **根因**：OpenClaw 飞书插件上传音频时没有传递 `duration` 参数  **解决方案**： 1. ✅ 备份原文件：`media.ts.backup.20260307_18081...

### 9. 用户需求
# 2026-03-08 - 周日  ## 📝 日志  _暂无手动记录_  ## 🔄 自动备份  - Git 提交：`1baf63a Auto backup: 2026-03-08 00:00:10`  --- **创建时间**: 2026-03-08 06:00 **状态**: 待填充

### 10. 用户需求
{"type":"session","version":3,"id":"5aae7da1-9fc3-426c-bd8b-29f2e37f978d","timestamp":"2026-03-07T05:20:40.839Z","cwd":"/Users/a123456/.openclaw/workspace"} {"type":"model_change","id":"6aac5331","par...

