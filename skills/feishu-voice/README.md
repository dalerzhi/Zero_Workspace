# Feishu Voice Message Skill

发送飞书**原生语音消息**（不是音频文件）的完整解决方案。

## 安装

这个 skill 已经在你的 workspace 中：
```
/Users/a123456/.openclaw/workspace/skills/feishu-voice/
```

**依赖**：
- `ffmpeg` - 用于音频转换
- `say` - macOS 自带 TTS

如果 ffmpeg 未安装：
```bash
brew install ffmpeg
```

## 使用方法

### 方式 1：使用脚本（推荐）

```bash
# 基本用法
./skills/feishu-voice/feishu-voice.sh "你好，这是测试语音"

# 指定接收人
./skills/feishu-voice/feishu-voice.sh "你好" ou_7c6c3cdce8475c7a8de63811592c37f9

# 指定声音
./skills/feishu-voice/feishu-voice.sh "Hello" ou_xxx Mei-Jia
```

### 方式 2：手动命令

```bash
# 1. 生成 TTS
say -v Ting-Ting "你好" -o /Users/a123456/.openclaw/workspace/voice.m4a

# 2. 转成 opus
ffmpeg -i voice.m4a -c libopus voice.opus -y

# 3. 发送
openclaw message send --channel feishu --target <user_id> --media voice.opus
```

## 为什么需要这个 Skill？

飞书区分两种音频：
- **音频文件** (`.m4a`, `.mp3`) - 显示为文件附件
- **语音消息** (`.opus`, `.ogg`) - 显示为原生语音气泡 ✅

这个 skill 确保你发送的是**原生语音消息**。

## 可用声音

查看可用声音：
```bash
say -v '?'
```

常用中文声音：
- `Ting-Ting` - 女声，普通话（默认）
- `Sin-Ji` - 女声，粤语
- `Mei-Jia` - 女声，普通话（较新）

## 文件结构

```
feishu-voice/
├── SKILL.md          # 完整文档
├── feishu-voice.sh   # 快捷脚本
└── README.md         # 本文件
```

## 故障排除

**问题**："Local media path is not under an allowed directory"
- **解决**：文件必须放在 workspace 目录，不能用 `/tmp/`

**问题**：发送后显示为文件，不是语音消息
- **解决**：确保文件扩展名是 `.opus` 或 `.ogg`

## 相关文档

- [完整 Skill 文档](SKILL.md)
- [飞书消息 API](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create)
