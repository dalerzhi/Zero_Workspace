#!/usr/bin/env python3
"""
Test script to check Insta360 Link 2 PTZ controls via OpenCV
"""
import cv2

# 打开摄像头
cap = cv2.VideoCapture(0)  # 尝试默认摄像头

# 检查是否打开成功
if not cap.isOpened():
    print("无法打开摄像头")
    exit(1)

# 列出所有可能的控制参数
controls = {
    'CAP_PROP_PAN': cv2.CAP_PROP_PAN,
    'CAP_PROP_TILT': cv2.CAP_PROP_TILT,
    'CAP_PROP_ZOOM': cv2.CAP_PROP_ZOOM,
    'CAP_PROP_FOCUS': cv2.CAP_PROP_FOCUS,
    'CAP_PROP_EXPOSURE': cv2.CAP_PROP_EXPOSURE,
    'CAP_PROP_GAIN': cv2.CAP_PROP_GAIN,
}

print("检查摄像头控制参数支持情况：")
print("-" * 50)

for name, prop_id in controls.items():
    value = cap.get(prop_id)
    print(f"{name}: {value} (0 或不支持 = 无此功能)")

# 尝试获取摄像头信息
print("\n当前摄像头参数：")
print(f"分辨率：{cap.get(cv2.CAP_PROP_FRAME_WIDTH)} x {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
print(f"FPS: {cap.get(cv2.CAP_PROP_FPS)}")

cap.release()
print("\n测试完成")
