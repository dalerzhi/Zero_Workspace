# 🔄 Session 配置持久化指南

_如何让新 Session 自动记住你的偏好设置_

---

## 📋 问题

每次新 Session 启动时，Agent 会"失忆"，忘记：
- 默认 TTS 音色
- 飞书默认接收者
- 摄像头设备
- 邮箱配置
- 其他偏好设置

---

## ✅ 解决方案

### 三层记忆系统

```
┌─────────────────────────────────────────┐
│  1. preferences.json (全局配置)          │
│     ~/.openclaw/preferences.json        │
│     → 每次启动自动加载                   │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  2. TOOLS.md (工作区配置)                │
│     ~/.openclaw/workspace/TOOLS.md      │
│     → 每次 Session 加载                  │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  3. MEMORY.md (长期记忆)                 │
│     ~/.openclaw/workspace/MEMORY.md     │
│     → 仅主 Session 加载                  │
└─────────────────────────────────────────┘
```

---

## 🔧 配置文件详解

### 1. preferences.json（关键！）

**位置**: `~/.openclaw/preferences.json`

**作用**: 
- 存储所有用户偏好
- 每次 Session 启动时自动加载
- 设置环境变量供脚本使用

**内容示例**:
```json
{
  "tts": {
    "default_voice_id": "dde1b9b5",
    "default_voice_name": "故事讲述者（子轩）",
    "provider": "noiz"
  },
  "feishu": {
    "default_chat_id": "ou_7c6c3cdce8475c7a8de63811592c37f9",
    "voice_method": "python_script"
  },
  "camera": {
    "default_device": "Insta360 Link 2"
  }
}
```

**自动设置的环境变量**:
```bash
TTS_DEFAULT_VOICE=dde1b9b5
TTS_PROVIDER=noiz
FEISHU_DEFAULT_CHAT_ID=ou_xxxxx
FEISHU_VOICE_METHOD=python_script
CAMERA_DEFAULT_DEVICE="Insta360 Link 2"
```

---

### 2. init-session.py（自动加载脚本）

**位置**: `~/.openclaw/workspace/scripts/init-session.py`

**作用**:
- 读取 `preferences.json`
- 设置环境变量
- 打印配置摘要

**运行方式**:
```bash
# 手动运行
python3 scripts/init-session.py

# 自动运行（推荐）
# 在 HEARTBEAT.md 中添加自动运行指令
```

**输出示例**:
```
🚀 Session 初始化...
✅ 环境变量已设置

============================================================
📋 用户偏好配置摘要
============================================================
🎤 TTS 默认音色：故事讲述者（子轩）- 磁性舒缓 (dde1b9b5)
📨 飞书默认接收者：ou_7c6c3cdce8475c7a8de63811592c37f9
   语音发送方式：python_script
📷 默认摄像头：Insta360 Link 2
📧 邮箱账户：main
   日报时间：08:00
============================================================
✅ Session 初始化完成！
```

---

### 3. TOOLS.md（快速参考）

**位置**: `~/.openclaw/workspace/TOOLS.md`

**作用**:
- 记录关键配置
- 快速查阅
- 每次 Session 都会加载

**内容**:
- TTS 音色配置
- 飞书语音发送方法
- 摄像头设备
- 其他工具配置

---

### 4. MEMORY.md（长期记忆）

**位置**: `~/.openclaw/workspace/MEMORY.md`

**作用**:
- 存储重要决策和历史
- 仅在主 Session 加载（安全考虑）
- 不自动设置环境变量

**内容**:
- 技能集成记录
- 重要经验教训
- 历史配置变更

---

## 🚀 使用流程

### 新 Session 启动时

**自动执行**：
```bash
# 1. 读取 preferences.json
# 2. 设置环境变量
# 3. 加载 TOOLS.md
# 4. （主 Session）加载 MEMORY.md
```

**结果**：
- ✅ TTS 默认音色已设置
- ✅ 飞书默认接收者已设置
- ✅ 摄像头设备已配置
- ✅ 可以直接使用 `python3 scripts/feishu-voice.py "文本"`

---

## 📝 修改配置

### 方法 1：编辑 preferences.json

```bash
vi ~/.openclaw/preferences.json

# 修改后重启 Session 或运行：
python3 scripts/init-session.py
```

### 方法 2：使用命令更新

```bash
# 更新默认音色
jq '.tts.default_voice_id = "8316cdf1"' \
  ~/.openclaw/preferences.json > /tmp/pref.json && \
  mv /tmp/pref.json ~/.openclaw/preferences.json

# 重新加载
python3 scripts/init-session.py
```

### 方法 3：直接设置环境变量（临时）

```bash
export TTS_DEFAULT_VOICE="8316cdf1"
export FEISHU_DEFAULT_CHAT_ID="ou_xxxxx"
```

---

## 🔍 验证配置

### 检查配置文件
```bash
cat ~/.openclaw/preferences.json | jq '.tts'
```

### 检查环境变量
```bash
echo $TTS_DEFAULT_VOICE
echo $FEISHU_DEFAULT_CHAT_ID
```

### 运行初始化脚本
```bash
python3 scripts/init-session.py
```

### 测试语音发送
```bash
python3 scripts/feishu-voice.py "测试语音"
```

---

## ⚠️ 注意事项

### 安全
- `preferences.json` 权限设置为 600
- 不包含敏感信息（密码、API Key 等）
- API Key 存储在独立文件（`~/.noiz_api_key`）

### 备份
```bash
# 备份配置
cp ~/.openclaw/preferences.json ~/.openclaw/preferences.json.backup

# 恢复配置
cp ~/.openclaw/preferences.json.backup ~/.openclaw/preferences.json
```

### 同步
```bash
# Git 忽略 preferences.json（包含个人配置）
echo "preferences.json" >> ~/.openclaw/.gitignore

# 但提交 preferences.json.template（示例配置）
cp ~/.openclaw/preferences.json ~/.openclaw/preferences.json.template
# 删除敏感信息后提交
```

---

## 📚 文件清单

| 文件 | 位置 | 作用 | 加载时机 |
|------|------|------|----------|
| `preferences.json` | `~/.openclaw/` | 用户偏好配置 | 每次启动 |
| `init-session.py` | `workspace/scripts/` | 初始化脚本 | 手动/自动 |
| `TOOLS.md` | `workspace/` | 工具配置 | 每次 Session |
| `MEMORY.md` | `workspace/` | 长期记忆 | 仅主 Session |
| `HEARTBEAT.md` | `workspace/` | 启动指令 | 每次 Session |

---

## 🎯 最佳实践

1. **使用 preferences.json 存储所有偏好**
   - 集中管理
   - 自动加载
   - 跨 Session 持久化

2. **在 HEARTBEAT.md 中添加自动运行指令**
   - 确保每次启动都加载

3. **定期更新 TOOLS.md**
   - 保持文档与配置同步

4. **MEMORY.md 只存储重要决策**
   - 不包含具体配置值

---

**最后更新**: 2026-03-09  
**状态**: ✅ 已配置并测试
