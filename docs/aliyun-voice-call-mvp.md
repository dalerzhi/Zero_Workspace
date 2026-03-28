# 阿里云电话外呼 MVP 记录

## 目标
让 OpenClaw 能通过阿里云语音服务，主动呼叫中国手机号。

## 当前选型
优先用 **公共模式 + SingleCallByTts**：
- 无需先买固定外显号码
- 只需要模板审核通过即可开始
- 最适合先打通第一通电话

备用：
- `SingleCallByVoice`：播报已审核的语音文件
- 专属模式：需要购买真实号码或服务实例

## 已完成
- 调研确认：Twilio 不适合中国大陆手机号外呼
- 调研确认：阿里云语音服务支持语音通知/验证码，并提供 `SingleCallByTts` / `SingleCallByVoice`
- 本地已创建 Python venv：`.venv-aliyun-vms`
- 已安装 SDK：`alibabacloud_dyvmsapi20170525`, `alibabacloud_tea_openapi`
- 已创建调用脚本：`scripts/aliyun_voice_call.py`

## 阿里云最小前置条件
1. 注册/登录阿里云
2. 完成企业实名认证
3. 开通语音服务
4. 申请企业资质并审核通过
5. 申请话术并审核通过
6. 创建 **公共模式** 的文本转语音模板并审核通过
7. 购买/开通语音通知公共号池套餐（分钟包）
8. 创建 AK/SK（建议 RAM 子账号）

## 最小调用方式
```bash
. .venv-aliyun-vms/bin/activate
export ALIYUN_ACCESS_KEY_ID=xxx
export ALIYUN_ACCESS_KEY_SECRET=xxx
export ALIYUN_VMS_TTS_CODE=TTS_xxx
python scripts/aliyun_voice_call.py tts \
  --called-number 13901241378 \
  --tts-param '{"name":"Bill"}'
```

如果模板不带变量：
```bash
python scripts/aliyun_voice_call.py tts \
  --called-number 13901241378 \
  --tts-code TTS_xxx \
  --tts-param '{}'
```

## 关键文档（官方）
- 产品页：`https://www.aliyun.com/product/vms`
- 快速入门：`https://help.aliyun.com/zh/vms/getting-started/through-the-api-or-sdk-using-voice-notification-or-audio-captcha`
- TTS 单呼：`https://help.aliyun.com/zh/vms/developer-reference/api-dyvmsapi-2017-05-25-singlecallbytts`
- 语音文件单呼：`https://help.aliyun.com/zh/vms/developer-reference/api-dyvmsapi-2017-05-25-singlecallbyvoice`
- FAQ：`https://help.aliyun.com/zh/vms/support/voice-notification-or-voice-verification-code-faq`

## 关键限制（官方）
- 同一“资质信息 + 号码用途”下，对同一被叫：**1 次/分钟、5 次/小时、20 次/24 小时**
- 模板/语音文件必须审核通过才能呼叫
- 公共模式与专属模式的模板/语音文件不通用

## 下一步
等用户提供：
- 阿里云账号登录能力（或让用户自行完成控制台开通）
- AK / SK
- 审核通过的 `TTS_CODE`

拿到这三个后，直接执行真实外呼测试。
