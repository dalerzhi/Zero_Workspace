# 语音识别 (STT) 和语音合成 (TTS) 优化方案

**研究日期**: 2026-03-06  
**目的**: 优化 Whisper 转录效果和 TTS 质量

---

## 📊 语音识别 (STT) 方案对比

### 1. Whisper 模型家族 (OpenAI)

| 模型 | 大小 | 中文效果 | 速度 | 推荐场景 |
|------|------|----------|------|----------|
| `tiny` | 39M | ⭐⭐ | 最快 | 快速测试，资源受限 |
| `base` | 74M | ⭐⭐ | 快 | 日常使用 |
| `small` | 244M | ⭐⭐⭐ | 中等 | 平衡选择 |
| `medium` | 769M | ⭐⭐⭐⭐ | 慢 | 高质量需求 |
| `large-v3` | 1550M | ⭐⭐⭐⭐⭐ | 最慢 | 生产环境 |
| `large-v3-turbo` | 1550M | ⭐⭐⭐⭐⭐ | 中等 | **推荐** |

**关键发现**:
- `large-v3` 比 `large-v2` 错误率降低 10-20%
- `turbo` 版本使用优化解码，速度快 2-3 倍，精度几乎相同
- 中文识别：`large-v3` > `medium` > `small`

### 2. Whisper 改进版本

#### WhisperX ⭐⭐⭐⭐⭐ (强烈推荐)
- **GitHub**: https://github.com/m-bain/whisperX
- **优势**:
  - 70 倍实时速度 (large-v2)
  - 单词级时间戳
  - 说话人分离 (Diarization)
  - VAD 预处理减少幻觉
  - 支持批量处理
- **安装**: `pip install whisperx`
- **使用**:
  ```bash
  whisperx audio.wav --model large-v3 --language zh
  ```

#### Faster-Whisper
- **GitHub**: https://github.com/guillaumekln/faster-whisper
- **优势**: CTranslate2 加速，内存占用低
- **速度**: 比原版快 4-5 倍

### 3. 云端 API 对比

| 服务商 | 中文准确率 | 价格 | 延迟 | 特色 |
|--------|------------|------|------|------|
| **Azure Speech** | ⭐⭐⭐⭐⭐ | $1/小时 | 低 | 支持方言，实时流式 |
| **Google Cloud STT** | ⭐⭐⭐⭐⭐ | $1.44/小时 | 低 | Chirp 3 模型，100+ 语言 |
| **OpenAI Whisper API** | ⭐⭐⭐⭐ | $0.006/分钟 | 中 | 简单，统一 API |
| **讯飞听见** | ⭐⭐⭐⭐⭐ | ¥0.8/小时 | 低 | 中文优化，方言支持 |
| **阿里云语音识别** | ⭐⭐⭐⭐ | ¥0.8/小时 | 低 | 中文场景优化 |

**推荐**: 
- 追求质量：Azure Speech / Google Chirp 3
- 性价比：讯飞听见 / 阿里云
- 简单集成：OpenAI API

---

## 🎤 TTS 方案对比

### 1. macOS 自带 `say` 命令

**优点**:
- 免费，离线，无需 API key
- 简单易用
- 隐私好

**缺点**:
- 声音机械感强
- 表现力有限
- 只有几种中文声音

**可用声音**:
```bash
say -v '?'  # 查看所有声音
```
- `Ting-Ting` - 女声，普通话 (默认)
- `Sin-Ji` - 女声，粤语
- `Mei-Jia` - 女声，普通话 (较新)

**评分**: ⭐⭐ (仅适合测试)

### 2. 云端 TTS API

| 服务商 | 自然度 | 中文支持 | 价格 | 特色 |
|--------|--------|----------|------|------|
| **Azure TTS** | ⭐⭐⭐⭐⭐ | 优秀 | $15/百万字符 | 神经语音，情感控制 |
| **Google TTS** | ⭐⭐⭐⭐ | 好 | $16/百万字符 | WaveNet 音质 |
| **Amazon Polly** | ⭐⭐⭐⭐ | 好 | $16/百万字符 | 新闻播报风格 |
| **ElevenLabs** | ⭐⭐⭐⭐⭐ | 良好 | $5-330/月 | 最自然，声音克隆 |
| **讯飞 TTS** | ⭐⭐⭐⭐⭐ | 优秀 | ¥15/百万字符 | 中文最优，方言 |
| **阿里云 TTS** | ⭐⭐⭐⭐ | 优秀 | ¥12/百万字符 | 中文场景 |

### 3. 开源 TTS

| 项目 | 质量 | 速度 | 难度 |
|------|------|------|------|
| **Coqui TTS** | ⭐⭐⭐⭐ | 快 | 中等 |
| **Piper** | ⭐⭐⭐ | 很快 | 简单 |
| **StyleTTS 2** | ⭐⭐⭐⭐⭐ | 中等 | 困难 |

---

## 🎯 推荐方案

### 方案 A: 本地优先 (隐私好，免费)

```bash
# STT: 使用 Whisper large-v3-turbo
whisper audio.ogg --model large-v3-turbo --language zh --output_format txt

# 或者用 WhisperX (更快更准)
whisperx audio.ogg --model large-v3 --language zh
```

**优点**: 免费，离线，隐私好  
**缺点**: 需要 GPU 才快，中文略逊于云端

### 方案 B: 云端高质量 (推荐)

```bash
# STT: Azure Speech / Google Cloud
# TTS: Azure TTS / ElevenLabs
```

**优点**: 最佳质量，支持方言，情感丰富  
**缺点**: 需要 API key，有成本

### 方案 C: 混合方案 (平衡)

```bash
# 日常用本地 Whisper
whisper audio.ogg --model medium --language zh

# 重要内容用云端 API
# 如会议记录、正式文档
```

---

## 📝 实施建议

### 立即可以做的优化

1. **升级 Whisper 模型**:
   ```bash
   # 当前用的是 tiny，升级到 large-v3-turbo
   whisper audio.ogg --model large-v3-turbo --language zh
   ```

2. **安装 WhisperX**:
   ```bash
   pip install whisperx
   # 使用
   whisperx audio.ogg --model large-v3 --language zh
   ```

3. **指定语言**:
   ```bash
   # 总是指定 --language zh 避免自动检测错误
   whisper audio.ogg --model medium --language zh
   ```

### 中期优化 (需要配置)

1. **配置 Azure Speech API**:
   ```bash
   # 需要 Azure 账号和 API key
   # 中文识别率提升 10-15%
   ```

2. **配置 Azure TTS / ElevenLabs**:
   ```bash
   # 替代 macOS say 命令
   # 声音自然度提升巨大
   ```

### 长期优化

1. **微调模型**: 针对特定场景 (如会议、访谈) 微调 Whisper
2. **自建服务**: 部署 WhisperX + Azure TTS 的本地服务

---

## 💰 成本估算

### 本地方案
- Whisper: 免费 (电费 + 硬件)
- macOS say: 免费
- **总计**: ¥0

### 云端方案 (按使用量)
- Azure Speech: ¥7/小时
- Azure TTS: ¥10/百万字符
- **月使用 10 小时**: 约 ¥100-200

---

## 🔧 下一步行动

1. [ ] 安装 WhisperX 测试效果
2. [ ] 申请 Azure / Google Cloud 免费额度测试
3. [ ] 对比 Whisper large-v3-turbo vs tiny 的效果
4. [ ] 测试 Azure TTS vs macOS say 的差异
5. [ ] 根据测试结果选择最终方案

---

## 📚 参考资料

- [Whisper 官方](https://github.com/openai/whisper)
- [WhisperX](https://github.com/m-bain/whisperX)
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper)
- [Azure Speech](https://azure.microsoft.com/services/cognitive-services/speech-services/)
- [Google Cloud STT](https://cloud.google.com/speech-to-text)
- [ElevenLabs](https://elevenlabs.io)
