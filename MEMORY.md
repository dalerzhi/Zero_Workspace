# MEMORY.md - 长期记忆

_最后更新：2026-03-08 06:00_

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
- 状态：🔧 技能已创建，待配置凭证
- 位置：`workspace/skills/aliyun-mail/`
- 功能：多邮箱 IMAP 收取、附件解析 (Word/Excel/PPT/PDF)、每日总结
- 依赖：`pip3 install imap-tools python-docx openpyxl python-pptx pypdf2`
- 配置：`.credentials/aliyun-mail.md` (参考模板：`.credentials/aliyun-mail.md.template`)
- 授权码指南：`skills/aliyun-mail/README-授权码.md`
- 用法：
  ```bash
  # 安装依赖
  bash skills/aliyun-mail/aliyun-mail.sh install
  
  # 测试连接
  bash skills/aliyun-mail/aliyun-mail.sh test
  
  # 收取昨日邮件并总结
  bash skills/aliyun-mail/aliyun-mail.sh summary --days 1
  
  # 配置每日 8 点自动任务
  openclaw cron create email-daily-summary \
    --schedule "0 8 * * *" \
    --command "cd /Users/a123456/.openclaw/workspace && bash skills/aliyun-mail/aliyun-mail.sh summary --days 1"
  ```

## 重要经验
1. 每天早上先检查 `memory/` 目录和 `MEMORY.md`
2. 飞书语音技能已经就绪，可以直接用
3. TTS 测试用 `tts` 工具，音频会自动交付
4. ⚠️ 用户配置偏好必须记录到 MEMORY.md
5. ⭐ **网络搜索优先用 Agent Reach**
6. ⚠️ OpenClaw 配置的环境变量不会传递到 exec，需要从 `~/.zshrc` 读取
7. ⚠️ clawhub 安装常限流，用浏览器手动下载 zip
8. ⚠️ inference.sh 域名被墙，需要代理或手动下载
