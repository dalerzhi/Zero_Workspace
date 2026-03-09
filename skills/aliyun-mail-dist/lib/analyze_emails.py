#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件智能分析 - 生成重要事项摘要
"""

import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

try:
    from imap_tools import MailBox, AND
except ImportError:
    print("❌ 缺少 imap-tools，运行：pip3 install imap-tools")
    sys.exit(1)

# 关键词权重（判断邮件重要性）
IMPORTANT_KEYWORDS = {
    '紧急': 5, '重要': 5, '审批': 5, '合同': 5, '账单': 4, '付款': 4,
    '故障': 5, '漏洞': 5, '安全': 4, '事故': 5, '告警': 4,
    '报价': 3, '订单': 4, '交付': 3, '上线': 4, '发布': 3,
    '会议': 2, '评审': 3, '汇报': 3, '总结': 2, '计划': 2,
    '人事': 3, '招聘': 2, '离职': 4, '入职': 3,
}

# 忽略的发件人/主题模式
IGNORE_PATTERNS = [
    r'no-reply@', r'noreply@', r'系统通知', r'自动发送',
    r'订阅', r'unsubscribe', r'广告', r'推广',
    r' Kickstarter', r'折扣', r'优惠',
]


def parse_credentials(cred_file):
    """解析凭证文件"""
    accounts = []
    current_account = {}
    
    with open(cred_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line.startswith('###'):
                if current_account:
                    accounts.append(current_account)
                current_account = {}
                continue
            
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lstrip('-').strip().lower().replace('-', '_')
                value = value.strip()
                current_account[key] = value
        
        if current_account:
            accounts.append(current_account)
    
    return accounts


def should_ignore(email):
    """判断是否应该忽略的邮件"""
    subject = email.subject or ''
    from_ = email.from_ or ''
    
    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, subject, re.IGNORECASE) or re.search(pattern, from_, re.IGNORECASE):
            return True
    return False


def calculate_importance(email):
    """计算邮件重要性分数"""
    score = 0
    text = (email.subject or '') + ' ' + (email.text or '')[:500]
    
    for keyword, weight in IMPORTANT_KEYWORDS.items():
        if keyword in text:
            score += weight
    
    # 有附件加分
    if email.attachments:
        score += 2
    
    # 多人收件加分
    if len(email.to) > 3:
        score += 1
    
    return score


def categorize_email(email):
    """分类邮件"""
    subject = (email.subject or '').lower()
    text = (email.text or '').lower()
    content = subject + ' ' + text
    
    categories = {
        '财务': ['账单', '付款', '发票', '结算', '报价', '合同', '采购'],
        '项目': ['项目', '交付', '上线', '发布', '进度', '计划', '评审'],
        '系统': ['系统', '服务器', '网络', '故障', '漏洞', '安全', '告警', '维护'],
        '人事': ['人事', '招聘', '入职', '离职', '面试', 'offer'],
        '会议': ['会议', '会议室', '预约', '邀请'],
        '客户': ['客户', '订单', '需求', 'RFP', '投标'],
    }
    
    for category, keywords in categories.items():
        for kw in keywords:
            if kw.lower() in content:
                return category
    
    return '其他'


def extract_key_points(text, max_length=300):
    """提取关键要点"""
    if not text:
        return ''
    
    # 清理 HTML
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    
    # 提取前几行（通常是重点）
    lines = text.strip().split('\n')
    key_lines = []
    
    for line in lines[:10]:  # 最多前 10 行
        line = line.strip()
        if line and len(line) > 5:  # 忽略太短的行
            key_lines.append(line)
        if len('\n'.join(key_lines)) > max_length:
            break
    
    result = '\n'.join(key_lines)
    if len(result) > max_length:
        result = result[:max_length] + '...'
    
    return result


def analyze_emails(account, days=4, output_file=None):
    """分析邮件并生成摘要"""
    
    date_from = (datetime.now() - timedelta(days=days)).date()
    print(f'📬 正在分析 {account["email"]} 的邮件...')
    print(f'   日期范围：{date_from} 至今\n')
    
    try:
        with MailBox(account['imap_server'], port=int(account.get('imap_port', 993))).login(
            account['email'], account['auth_code']
        ) as mailbox:
            criteria = AND(date_gte=date_from)
            emails = list(mailbox.fetch(criteria, reverse=True))
            
    except Exception as e:
        print(f'❌ 连接失败：{e}')
        return
    
    # 过滤和分类
    important_emails = []
    normal_emails = defaultdict(list)
    ignored_count = 0
    
    for email in emails:
        # 跳过自己发送的
        if email.from_ == account['email']:
            continue
        
        # 跳过忽略的
        if should_ignore(email):
            ignored_count += 1
            continue
        
        # 计算重要性
        score = calculate_importance(email)
        
        email_data = {
            'from': email.from_,
            'to': email.to,
            'subject': email.subject or '(无主题)',
            'date': email.date,
            'score': score,
            'category': categorize_email(email),
            'key_points': extract_key_points(email.text),
            'has_attachments': len(email.attachments) > 0,
            'attachment_count': len(email.attachments),
        }
        
        if score >= 5:
            important_emails.append(email_data)
        else:
            normal_emails[email_data['category']].append(email_data)
    
    # 排序
    important_emails.sort(key=lambda x: (-x['score'], x['date']))
    for category in normal_emails:
        normal_emails[category].sort(key=lambda x: x['date'], reverse=True)
    
    # 生成报告
    report = generate_report(
        important_emails, 
        dict(normal_emails), 
        len(emails), 
        ignored_count,
        date_from
    )
    
    # 输出
    print(report)
    
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f'\n💾 报告已保存：{output_file}')


def generate_report(important, normal, total, ignored, date_from):
    """生成摘要报告"""
    
    lines = []
    lines.append(f"# 📧 重要事项摘要 ({date_from} 至今)")
    lines.append(f"\n_生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}_\n")
    
    # 概览
    lines.append("## 📊 概览")
    lines.append(f"- 总邮件数：{total}")
    lines.append(f"- 已忽略（系统/广告）：{ignored}")
    lines.append(f"- **重要事项：{len(important)}**")
    lines.append(f"- 一般事项：{sum(len(v) for v in normal.values())}\n")
    
    # 高优先级
    if important:
        lines.append("\n## 🔴 高优先级事项\n")
        for i, email in enumerate(important[:10], 1):  # 最多显示 10 个
            lines.append(f"### {i}. {email['subject']}")
            lines.append(f"**发件人**: {email['from']}")
            lines.append(f"**时间**: {email['date'].strftime('%m-%d %H:%M')}")
            lines.append(f"**分类**: {email['category']} | **重要性**: {email['score']}分")
            
            if email['has_attachments']:
                lines.append(f"**附件**: {email['attachment_count']} 个")
            
            if email['key_points']:
                lines.append(f"\n**要点**:\n{email['key_points']}\n")
            
            lines.append("---\n")
    
    # 一般事项（按类别）
    lines.append("\n## 📋 一般事项（按类别）\n")
    
    for category, emails in sorted(normal.items(), key=lambda x: -len(x[1])):
        if not emails:
            continue
        
        lines.append(f"### {category} ({len(emails)} 封)\n")
        for email in emails[:5]:  # 每类最多显示 5 个
            lines.append(f"- [{email['date'].strftime('%m-%d %H:%M')}] {email['subject']} — {email['from'].split('<')[-1].strip('>') if '<' in email['from'] else email['from']}")
        
        if len(emails) > 5:
            lines.append(f"- ... 还有 {len(emails) - 5} 封")
        lines.append("")
    
    # 提醒
    lines.append("\n---\n")
    lines.append("\n💡 **提醒**: 请优先处理高优先级事项，特别是标红的内容。")
    
    return '\n'.join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='邮件智能分析')
    parser.add_argument('--days', type=int, default=4, help='分析最近 N 天')
    parser.add_argument('--output', help='输出文件路径')
    args = parser.parse_args()
    
    # 加载凭证
    workspace_dir = Path(__file__).parent.parent.parent.parent
    cred_file = workspace_dir / '.credentials' / 'aliyun-mail.md'
    
    if not cred_file.exists():
        print(f"❌ 凭证文件不存在：{cred_file}")
        sys.exit(1)
    
    accounts = parse_credentials(cred_file)
    if not accounts:
        print("❌ 凭证文件中没有有效的邮箱配置")
        sys.exit(1)
    
    # 输出文件
    output_file = args.output
    if not output_file:
        output_dir = workspace_dir / 'email-reports'
        os.makedirs(output_dir, exist_ok=True)
        output_file = output_dir / f"{datetime.now().strftime('%Y%m%d')}-重要事项摘要.md"
    
    # 分析
    for account in accounts:
        analyze_emails(account, days=args.days, output_file=str(output_file))


if __name__ == '__main__':
    main()
