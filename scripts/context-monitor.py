#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context 监控与自动记忆整理

功能：
1. 监控 Session Context 使用率
2. 超过 70% 时自动触发记忆整理
3. 将重要信息写入 MEMORY.md
4. 清理冗余上下文
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 配置
CONTEXT_WARNING_THRESHOLD = 0.70  # 70% 警告阈值
CONTEXT_CRITICAL_THRESHOLD = 0.85  # 85% 紧急阈值
MEMORY_FILE = Path.home() / '.openclaw' / 'workspace' / 'MEMORY.md'
CONTEXT_STATE_FILE = Path.home() / '.openclaw' / 'workspace' / '.context-state.json'


def get_session_status():
    """获取当前 Session 状态"""
    try:
        # 尝试从环境变量或配置文件获取 Session 信息
        # 这里简化处理，实际应该调用 OpenClaw API
        return {
            'token_used': 0,
            'token_limit': 0,
            'usage_percent': 0.0,
            'message_count': 0
        }
    except Exception as e:
        print(f"⚠️ 无法获取 Session 状态：{e}")
        return None


def load_context_state():
    """加载 Context 状态"""
    if CONTEXT_STATE_FILE.exists():
        with open(CONTEXT_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'last_cleanup': None,
        'cleanup_count': 0,
        'total_tokens_saved': 0
    }


def save_context_state(state):
    """保存 Context 状态"""
    with open(CONTEXT_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def estimate_context_usage():
    """估算当前 Context 使用率"""
    # 简化版本：检查最近的会话记录
    session_dir = Path.home() / '.openclaw' / 'agents' / 'main' / 'sessions'
    
    if not session_dir.exists():
        return {'estimated': True, 'usage_percent': 0.0, 'message_count': 0}
    
    # 找到最新的会话文件
    session_files = list(session_dir.glob('*.jsonl'))
    if not session_files:
        return {'estimated': True, 'usage_percent': 0.0, 'message_count': 0}
    
    latest_session = max(session_files, key=lambda f: f.stat().st_mtime)
    
    # 计算消息数量
    message_count = 0
    total_chars = 0
    
    with open(latest_session, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                msg = json.loads(line)
                if msg.get('type') == 'message':
                    message_count += 1
                    content = msg.get('message', {}).get('content', [])
                    for item in content:
                        if isinstance(item, dict) and 'text' in item:
                            total_chars += len(item['text'])
            except:
                continue
    
    # 粗略估算：每个中文字符≈1.5 token，每个英文字符≈0.25 token
    estimated_tokens = total_chars * 0.5
    token_limit = 128000  # 假设限制
    
    usage_percent = estimated_tokens / token_limit
    
    return {
        'estimated': True,
        'usage_percent': usage_percent,
        'message_count': message_count,
        'total_chars': total_chars,
        'session_file': str(latest_session)
    }


def should_cleanup(usage_percent):
    """判断是否需要清理"""
    return usage_percent >= CONTEXT_WARNING_THRESHOLD


def extract_key_points_from_session():
    """从当前会话中提取关键点"""
    session_dir = Path.home() / '.openclaw' / 'agents' / 'main' / 'sessions'
    
    if not session_dir.exists():
        return []
    
    session_files = list(session_dir.glob('*.jsonl'))
    if not session_files:
        return []
    
    latest_session = max(session_files, key=lambda f: f.stat().st_mtime)
    
    key_points = []
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    with open(latest_session, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                msg = json.loads(line)
                if msg.get('type') == 'message':
                    role = msg.get('message', {}).get('role', '')
                    content = msg.get('message', {}).get('content', [])
                    
                    text_content = ''
                    for item in content:
                        if isinstance(item, dict) and 'text' in item:
                            text_content += item['text']
                    
                    # 提取关键信息（简化版）
                    if len(text_content) > 100:
                        # 检查是否包含重要关键词
                        keywords = ['配置', '修复', '优化', '完成', '创建', '部署', '技能', '邮箱', '邮件']
                        if any(kw in text_content for kw in keywords):
                            # 截取前 200 字符作为关键点
                            summary = text_content[:200].replace('\n', ' ').strip()
                            if len(text_content) > 200:
                                summary += '...'
                            key_points.append({
                                'role': role,
                                'summary': summary,
                                'length': len(text_content)
                            })
            except:
                continue
    
    return key_points[:10]  # 最多返回 10 个关键点


def append_to_memory(key_points):
    """将关键点添加到 MEMORY.md"""
    if not MEMORY_FILE.exists():
        # 创建基础 MEMORY.md
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            f.write("# MEMORY.md - 长期记忆\n\n")
            f.write(f"_最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}_\n\n")
    
    # 读取现有内容
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 添加新的关键点
    today = datetime.now().strftime('%Y-%m-%d')
    new_section = f"\n## {today} - 自动整理\n\n"
    
    for i, point in enumerate(key_points, 1):
        if point['role'] == 'assistant':
            new_section += f"### {i}. 完成的工作\n"
        else:
            new_section += f"### {i}. 用户需求\n"
        new_section += f"{point['summary']}\n\n"
    
    # 检查是否已存在今日章节
    if f"## {today}" in content:
        print(f"⚠️ 今日 ({today}) 已有记录，跳过写入")
        return False
    
    # 追加到文件
    with open(MEMORY_FILE, 'a', encoding='utf-8') as f:
        f.write(new_section)
    
    print(f"✅ 已添加 {len(key_points)} 个关键点到 MEMORY.md")
    return True


def cleanup_context():
    """执行 Context 清理"""
    print(f"🔍 检查 Context 使用情况...")
    
    # 获取使用率
    status = estimate_context_usage()
    usage_percent = status.get('usage_percent', 0.0)
    
    print(f"📊 当前 Context 使用率：{usage_percent:.1%}")
    print(f"   消息数：{status.get('message_count', 0)}")
    print(f"   字符数：{status.get('total_chars', 0):,}")
    
    # 加载状态
    state = load_context_state()
    
    # 判断是否需要清理
    if not should_cleanup(usage_percent):
        print(f"✅ Context 使用率正常 (<{CONTEXT_WARNING_THRESHOLD:.0%})")
        return
    
    # 需要清理
    print(f"\n⚠️  Context 使用率超过阈值 ({CONTEXT_WARNING_THRESHOLD:.0%})")
    print(f"📝 开始提取关键点...")
    
    # 提取关键点
    key_points = extract_key_points_from_session()
    
    if not key_points:
        print("⚠️  未提取到关键点")
        return
    
    print(f"✅ 提取到 {len(key_points)} 个关键点")
    
    # 写入 MEMORY.md
    print(f"\n💾 写入 MEMORY.md...")
    if append_to_memory(key_points):
        # 更新状态
        state['last_cleanup'] = datetime.now().isoformat()
        state['cleanup_count'] += 1
        save_context_state(state)
        
        print(f"\n✅ Context 整理完成！")
        print(f"   清理次数：{state['cleanup_count']}")
        print(f"   最后清理：{state['last_cleanup']}")
    else:
        print(f"\n⚠️  跳过写入（今日已记录）")


def main():
    """主函数"""
    print("="*60)
    print("🔍 Context 监控与自动记忆整理")
    print(f"   时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    try:
        cleanup_context()
    except Exception as e:
        print(f"\n❌ 执行失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ 检查完成")
    print("="*60)


if __name__ == '__main__':
    main()
