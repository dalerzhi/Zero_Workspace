#!/usr/bin/env python3
import argparse
import json
import os
import sys
from typing import Any

try:
    from alibabacloud_dyvmsapi20170525.client import Client
    from alibabacloud_dyvmsapi20170525 import models as vms_models
    from alibabacloud_tea_openapi.models import Config
except Exception as e:  # pragma: no cover
    print(
        "Missing Aliyun Voice SDK. Activate .venv-aliyun-vms or install: "
        "pip install alibabacloud_dyvmsapi20170525 alibabacloud_tea_openapi",
        file=sys.stderr,
    )
    raise


def env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    return value if value not in ("", None) else default


def make_client() -> Client:
    access_key_id = env("ALIYUN_ACCESS_KEY_ID")
    access_key_secret = env("ALIYUN_ACCESS_KEY_SECRET")
    if not access_key_id or not access_key_secret:
        raise SystemExit("Need ALIYUN_ACCESS_KEY_ID and ALIYUN_ACCESS_KEY_SECRET")

    config = Config(access_key_id=access_key_id, access_key_secret=access_key_secret)
    config.endpoint = env("ALIYUN_VMS_ENDPOINT", "dyvmsapi.aliyuncs.com")
    return Client(config)


def obj_to_dict(obj: Any) -> Any:
    if hasattr(obj, "to_map"):
        return obj.to_map()
    if isinstance(obj, dict):
        return {k: obj_to_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [obj_to_dict(v) for v in obj]
    return obj


def single_call_by_tts(args: argparse.Namespace) -> dict:
    client = make_client()
    request = vms_models.SingleCallByTtsRequest(
        called_number=args.called_number,
        called_show_number=args.called_show_number,
        tts_code=args.tts_code,
        tts_param=args.tts_param,
        play_times=args.play_times,
        volume=args.volume,
        speed=args.speed,
        out_id=args.out_id,
    )
    response = client.single_call_by_tts(request)
    return obj_to_dict(response)


def single_call_by_voice(args: argparse.Namespace) -> dict:
    client = make_client()
    request = vms_models.SingleCallByVoiceRequest(
        called_number=args.called_number,
        called_show_number=args.called_show_number,
        voice_code=args.voice_code,
        play_times=args.play_times,
        volume=args.volume,
        speed=args.speed,
        out_id=args.out_id,
    )
    response = client.single_call_by_voice(request)
    return obj_to_dict(response)


def query_call_detail(args: argparse.Namespace) -> dict:
    client = make_client()
    request = vms_models.QueryCallDetailByCallIdRequest(call_id=args.call_id)
    response = client.query_call_detail_by_call_id(request)
    return obj_to_dict(response)


def main() -> int:
    parser = argparse.ArgumentParser(description="Aliyun Voice Service call helper")
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--called-number", required=True, help="Target phone number")
    common.add_argument(
        "--called-show-number",
        default=env("ALIYUN_VMS_CALLED_SHOW_NUMBER"),
        help="Leave empty for public mode; set purchased real number/service instance for exclusive mode",
    )
    common.add_argument("--play-times", type=int, default=int(env("ALIYUN_VMS_PLAY_TIMES", "2")))
    common.add_argument("--volume", type=int, default=int(env("ALIYUN_VMS_VOLUME", "100")))
    common.add_argument("--speed", type=int, default=int(env("ALIYUN_VMS_SPEED", "0")))
    common.add_argument("--out-id", default=env("ALIYUN_VMS_OUT_ID", "openclaw"))

    p_tts = sub.add_parser("tts", parents=[common], help="Call via SingleCallByTts")
    p_tts.add_argument("--tts-code", default=env("ALIYUN_VMS_TTS_CODE"), required=env("ALIYUN_VMS_TTS_CODE") is None)
    p_tts.add_argument(
        "--tts-param",
        default=env("ALIYUN_VMS_TTS_PARAM", "{}"),
        help='JSON string like {"name":"Bill"}',
    )
    p_tts.set_defaults(func=single_call_by_tts)

    p_voice = sub.add_parser("voice", parents=[common], help="Call via SingleCallByVoice")
    p_voice.add_argument("--voice-code", default=env("ALIYUN_VMS_VOICE_CODE"), required=env("ALIYUN_VMS_VOICE_CODE") is None)
    p_voice.set_defaults(func=single_call_by_voice)

    p_query = sub.add_parser("query", help="Query call detail by CallId")
    p_query.add_argument("--call-id", required=True)
    p_query.set_defaults(func=query_call_detail)

    args = parser.parse_args()

    if getattr(args, "tts_param", None):
        try:
            json.loads(args.tts_param)
        except Exception as e:
            raise SystemExit(f"Invalid --tts-param JSON: {e}")

    result = args.func(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
