#!/usr/bin/env python3
"""
Insta360 Link Controller 云台控制 - 鼠标拖动方式
"""
import subprocess
import time

def drag_mouse(from_x, from_y, to_x, to_y, duration=0.5):
    """鼠标拖动"""
    # 移动到起点
    subprocess.run(['cliclick', f'm:{from_x},{from_y}'])
    time.sleep(0.2)
    # 按下鼠标
    subprocess.run(['cliclick', 'dd:.'])
    time.sleep(0.1)
    # 拖动到终点
    subprocess.run(['cliclick', f'dm:{to_x},{to_y}'])
    time.sleep(duration)
    # 松开鼠标
    subprocess.run(['cliclick', 'du:.'])
    time.sleep(0.1)

def ptz_up(steps=3):
    """云台向上 - 鼠标向下拖动"""
    print("云台向上")
    for _ in range(steps):
        drag_mouse(600, 400, 600, 300, 0.3)
        time.sleep(0.2)

def ptz_down(steps=3):
    """云台向下 - 鼠标向上拖动"""
    print("云台向下")
    for _ in range(steps):
        drag_mouse(600, 300, 600, 400, 0.3)
        time.sleep(0.2)

def ptz_left(steps=3):
    """云台向左 - 鼠标向右拖动"""
    print("云台向左")
    for _ in range(steps):
        drag_mouse(300, 400, 400, 400, 0.3)
        time.sleep(0.2)

def ptz_right(steps=3):
    """云台向右 - 鼠标向左拖动"""
    print("云台向右")
    for _ in range(steps):
        drag_mouse(400, 400, 300, 400, 0.3)
        time.sleep(0.2)

if __name__ == '__main__':
    print("Insta360 Link 鼠标拖动控制测试")
    print("请确保 Insta360 Link Controller 窗口在前台！")
    time.sleep(2)
    
    # 测试向上
    ptz_up(2)
    time.sleep(1)
    subprocess.run(['imagesnap', '-d', 'Insta360 Link 2', '/Users/a123456/.openclaw/workspace/mouse_up.jpg'])
    print("拍照完成")
