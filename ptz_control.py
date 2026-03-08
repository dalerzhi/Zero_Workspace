#!/usr/bin/env python3
"""
Insta360 Link Controller 云台控制脚本
通过模拟键盘快捷键控制摄像头云台

Insta360 Link Controller 快捷键：
- Option + ↑ 云台向上
- Option + ↓ 云台向下
- Option + ← 云台向左
- Option + → 云台向右
- Command + ↑ 变焦放大
- Command + ↓ 变焦缩小
"""
import subprocess
import time
import sys

def send_key_combo(modifier, key):
    """发送组合键"""
    subprocess.run(['cliclick', f'kd:{modifier}'])
    time.sleep(0.1)
    subprocess.run(['cliclick', f'kp:{key}'])
    time.sleep(0.1)
    subprocess.run(['cliclick', f'ku:{modifier}'])

def move_ptz(direction, steps=5):
    """
    控制云台移动
    direction: up, down, left, right, zoom_in, zoom_out
    """
    key_map = {
        'up': 'arrow-up',
        'down': 'arrow-down', 
        'left': 'arrow-left',
        'right': 'arrow-right',
        'zoom_in': 'arrow-up',
        'zoom_out': 'arrow-down'
    }
    
    modifier_map = {
        'up': 'alt',
        'down': 'alt',
        'left': 'alt',
        'right': 'alt',
        'zoom_in': 'cmd',
        'zoom_out': 'cmd'
    }
    
    if direction in key_map:
        modifier = modifier_map[direction]
        key = key_map[direction]
        print(f"Moving {direction} ({steps} steps)")
        for i in range(steps):
            send_key_combo(modifier, key)
            time.sleep(0.15)
            print(f"  Step {i+1}/{steps}")

def take_photo(filename):
    """拍照"""
    subprocess.run(['imagesnap', '-d', 'Insta360 Link 2', filename])
    print(f"Photo saved: {filename}")

if __name__ == '__main__':
    command = sys.argv[1] if len(sys.argv) > 1 else 'test'
    
    if command == 'up':
        move_ptz('up', 5)
    elif command == 'down':
        move_ptz('down', 5)
    elif command == 'left':
        move_ptz('left', 5)
    elif command == 'right':
        move_ptz('right', 5)
    elif command == 'zoom_in':
        move_ptz('zoom_in', 3)
    elif command == 'zoom_out':
        move_ptz('zoom_out', 3)
    elif command == 'test':
        print("=== Insta360 Link 云台控制测试 ===")
        print("测试流程：上 → 拍照 → 下 → 拍照 → 左 → 拍照 → 右 → 拍照")
        
        # 先拍一张基准照片
        take_photo('/Users/a123456/.openclaw/workspace/ptz_center.jpg')
        
        # 向上
        print("\n1. 云台向上")
        move_ptz('up', 5)
        time.sleep(1)
        take_photo('/Users/a123456/.openclaw/workspace/ptz_up.jpg')
        
        # 向下（回到中间）
        print("\n2. 云台向下（回中）")
        move_ptz('down', 5)
        time.sleep(1)
        take_photo('/Users/a123456/.openclaw/workspace/ptz_center2.jpg')
        
        # 向左
        print("\n3. 云台向左")
        move_ptz('left', 5)
        time.sleep(1)
        take_photo('/Users/a123456/.openclaw/workspace/ptz_left.jpg')
        
        # 向右（回到中间）
        print("\n4. 云台向右（回中）")
        move_ptz('right', 5)
        time.sleep(1)
        take_photo('/Users/a123456/.openclaw/workspace/ptz_center3.jpg')
        
        print("\n✅ 测试完成！")
    else:
        print(f"未知命令：{command}")
        print("可用命令：up, down, left, right, zoom_in, zoom_out, test")
