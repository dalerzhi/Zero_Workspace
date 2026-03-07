# MEMORY.md - 长期记忆

_最后更新：2026-03-06 18:47_

## 技能与工具

### 飞书语音发送
- 技能位置：`skills/feishu-voice/SKILL.md`
- 依赖：`ffmpeg` (brew), `say` (macOS 内置)
- 流程：TTS → `.m4a` → ffmpeg 转 `.opus` → 飞书 message 发送
- 关键：必须用 `.opus` 格式才能显示为原生语音消息
- 中文语音：`Ting-Ting`, `Mei-Jia`, `Sin-Ji`

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

## 重要经验
1. 每天早上先检查 `memory/` 目录和 `MEMORY.md`
2. 飞书语音技能已经就绪，可以直接用
3. TTS 测试用 `tts` 工具，音频会自动交付
4. ⚠️ 用户配置偏好必须记录到 MEMORY.md
5. ⭐ **网络搜索优先用 Agent Reach**
6. ⚠️ OpenClaw 配置的环境变量不会传递到 exec，需要从 `~/.zshrc` 读取
7. ⚠️ clawhub 安装常限流，用浏览器手动下载 zip
8. ⚠️ inference.sh 域名被墙，需要代理或手动下载
