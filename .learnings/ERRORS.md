# Errors Log

记录命令失败、异常和集成问题。

---

## [ERR-20260306-001] nano_banana_pro

**Logged**: 2026-03-06T18:47:00+08:00
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Nano Banana 2 依赖的 inference.sh CLI 无法安装（域名被墙）

### Error
```
curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL in connection to cli.inference.sh:443
curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL in connection to dist.inference.sh:443
```

### Context
- 尝试安装 Nano Banana 2 skill
- 需要 infsh CLI 工具
- 域名 cli.inference.sh 和 dist.inference.sh 无法连接

### Suggested Fix
1. 使用代理
2. 手动下载二进制文件
3. 或者直接使用 Gemini API 调用图片生成

### Metadata
- Reproducible: yes
- Related Files: `/Users/a123456/.openclaw/workspace/skills/nano-banana-2/SKILL.md`
- See Also: LRN-20260306-004

---

## [ERR-20260306-002] izwi_tts

**Logged**: 2026-03-06T18:47:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
Izwi TTS `--speaker` 参数对 0.6B Base 模型无效

---

## [ERR-20260306-003] memory_loss

**Logged**: 2026-03-06T19:26:00+08:00
**Priority**: high
**Status**: pending
**Area**: config

### Summary
写报告时忘记已完成的进度，显示"等待 API key 配置"

### Error
报告中写道："生成头像图片（等待 API key 配置）"
但实际上 API key 早已获取，头像已生成完成

### Context
- 19:17 已成功生成 `zero-avatar.png` (2K, 5.3MB)
- 19:26 写报告时却写成"等待 API key"
- 原因：写报告时没有检查实际完成状态

### Suggested Fix
1. 写报告前先检查 `.learnings/` 中的状态
2. 或者用任务清单跟踪进度
3. 建立"完成即更新"的习惯

### Metadata
- Reproducible: yes
- Related Files: `/Users/a123456/.openclaw/workspace/self-improvement-report.md`
- See Also: LRN-20260306-006 (用户配置偏好必须记录)

---

## [ERR-20260306-004] performance

**Logged**: 2026-03-06T19:47:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: infra

### Summary
VoiceDesign 1.7B 模型 TTS 生成速度慢

### Error
男声语音生成花了太长时间（>10 分钟未完成）

### Context
- VoiceDesign-4bit 模型 2.15 GiB
- 5 秒语音需要 40 秒生成（8 倍速）
- 长文本（30 秒）需要 4-5 分钟

### Resolution
- **Resolved**: 2026-03-06T19:47:00+08:00
- **Notes**: 改用短文本测试（10 秒），生成成功。建议日常用 0.6B 模型，重要场合用 VoiceDesign

### Metadata
- Reproducible: yes
- Related Files: `/Users/a123456/.local/bin/izwi`
- See Also: LRN-20260306-003 (Izwi 音色模型选择)

### Error
```
izwi tts --model Qwen3-TTS-12Hz-0.6B-Base --speaker "male-deep" ...
# 生成的语音仍然是女声
```

### Context
- 尝试用 `--speaker "male-deep"` 生成男声
- Qwen3-TTS-12Hz-0.6B-Base 模型不支持音色切换
- 只有 VoiceDesign 模型支持

### Resolution
- **Resolved**: 2026-03-06T18:47:00+08:00
- **Notes**: 下载了 VoiceDesign-4bit 模型 (2.15 GiB)，支持男声音色

### Metadata
- Reproducible: yes
- Related Files: `/Users/a123456/.local/bin/izwi`
- See Also: LRN-20260306-003

---
