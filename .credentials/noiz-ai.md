# Noiz AI 账号凭证

_创建时间：2026-03-07 13:38_
_用途：Noiz AI TTS 服务 API 访问_

---

## 📧 账号信息

| 字段 | 值 |
|------|-----|
| **邮箱** | `6875447@qq.com` |
| **密码** | `Noiz12345678` |

---

## ✅ 注册状态

**注册时间**: 2026-03-07 13:45  
**状态**: ✅ 已验证，API Key 已配置  
**测试**: ✅ TTS 生成成功（4.92 秒音频）

---

## 🧪 测试结果

**测试时间**: 2026-03-07 13:55  
**测试文本**: "你好，这是 NoizAI TTS 测试，我的声音好听吗？"  
**生成时长**: 4.92 秒  
**输出文件**: `/tmp/noiz-test.wav`  
**音质**: ⭐⭐⭐⭐⭐ 非常好，自然流畅  
| **手机** | `13901241378` (备用) |

---

## 🔑 API Key

**Key**: `NjU2MDVjYjQtOGMzZC00OTc5LWE0YjgtODM4ZWY3NzYzYWQ1JDY4NzU0NDdAcXEuY29t`

**额度**: 100,000 字符免费 TTS

**创建时间**: 2026-03-07

---

## 📝 使用说明

### 配置 API Key

```bash
bash skills/tts/scripts/tts.sh config --set-api-key YOUR_KEY
```

API Key 会保存到 `~/.noiz_api_key`

### 测试 TTS

```bash
# 简单模式
bash skills/tts/scripts/tts.sh speak \
  -t "你好，这是 NoizAI TTS 测试" \
  -o /tmp/test.wav

# 飞书发送
bash skills/tts/scripts/tts.sh speak_and_send_feishu \
  -t "你好" \
  --chat-id ou_xxx
```

---

## 🔗 相关链接

- 官网：https://noiz.ai
- API Keys：https://developers.noiz.ai/api-keys
- 文档：https://docs.noiz.ai

---

**安全提示**：
- 此文件包含敏感凭证，请勿上传到公开仓库
- 建议启用两步验证（如果支持）
- 定期更换密码
