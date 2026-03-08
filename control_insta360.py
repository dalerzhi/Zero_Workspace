#!/usr/bin/env python3
"""
Insta360 Link Controller 云台控制脚本
通过模拟键盘快捷键控制摄像头
"""
import subprocess
import time

def send_keys(keys):
    """发送键盘按键组合"""
    subprocess.run(['cliclick', 't:' + keys])

def move_camera(direction, duration=1):
    """
    控制摄像头移动
    direction: up, down, left, right
    Insta360 Link Controller 快捷键：
    - Option + ↑ 云台向上
    - Option + ↓ 云台向下
    - Option + ← 云台向左
    - Option + → 云台向右
    """
    key_map = {
        'up': 'up',
        'down': 'down', 
        'left': 'left',
        'right': 'right'
    }
    
    if direction in key_map:
        print(f"Moving camera {direction}")
        # 用 cliclick 的 press 命令
        for _ in range(int(duration * 5)):
            subprocess.run(['cliclick', f'press:{key_map[direction]}'])
            time.sleep(0.2)

if __name__ == '__main__':
    print("Insta360 Link 云台控制测试")
    print("尝试控制摄像头...")
    
    # 测试：先向上移动
    move_camera('up', 1)
    time.sleep(1)
    
    # 测试：拍一张照片
    subprocess.run(['imagesnap', '-d', 'Insta360 Link 2', '/Users/a123456/.openclaw/workspace/camera_after_move.jpg'])
    print("完成！")
