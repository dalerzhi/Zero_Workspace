#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件分析脚本 - 收取并分析重要邮件
"""

import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
import os
import re

# 邮箱配置
EMAIL_CONFIG = {
    'email': 'zhibin@cheersucloud.com',
    'imap_server': 'imap.qiye.aliyun.com',
    'imap_port': 993,
    'auth_code': 'Nf8JracDzQP4u4uu'
}

# 重要性关键词
IMPORTANT_KEYWORDS = [
    '紧急', '重要', '审批', '合同', '账单', '故障', '漏洞',
    'urgent', 'important', 'approval', 'contract', 'invoice',
    'error', 'critical', 'alert', 'warning', 'payment'
]

# 忽略的发件人/主题关键词
IGNORE_PATTERNS = [
    'noreply', 'no-reply', 'notification', 'system', '自动',
    '订阅', '广告', 'promo', 'marketing', 'newsletter',
    '验证码', '登录', 'security alert'
]

def decode_mime_words(s):
    """解码 MIME 编码的字符串"""
    if not s:
        return ''
    decoded = []
    for part, encoding in decode_header(s):
        if isinstance(part, bytes):
            try:
                decoded.append(part.decode(encoding or 'utf-8', errors='ignore'))
            except:
                decoded.append(part.decode('utf-8', errors='ignore'))
        else:
            decoded.append(part)
    return ''.join(decoded)

def get_email_body(msg):
    """获取邮件正文"""
    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition', ''))
            
            # 跳过附件
            if 'attachment' in content_disposition:
                continue
            
            if content_type == 'text/plain':
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    body += part.get_payload(decode=True).decode(charset, errors='ignore')
                except:
                    pass
                break  # 只取第一个 text/plain
    else:
        try:
            charset = msg.get_content_charset() or 'utf-8'
            body = msg.get_payload(decode=True).decode(charset, errors='ignore')
        except:
            pass
    
    return body[:500]  # 只取前 500 字

def get_attachments(msg):
    """获取附件信息"""
    attachments = []
    for part in msg.walk():
        content_disposition = str(part.get('Content-Disposition', ''))
        if 'attachment' in content_disposition:
            filename = part.get_filename()
            if filename:
                filename = decode_mime_words(filename)
                content_type = part.get_content_type()
                attachments.append({
                    'filename': filename,
                    'content_type': content_type
                })
    return attachments

def is_important(subject, body, from_addr):
    """判断邮件是否重要"""
    text = (subject + ' ' + body + ' ' + from_addr).lower()
    
    # 检查是否应该忽略
    for pattern in IGNORE_PATTERNS:
        if pattern.lower() in text:
            return False
    
    # 检查重要性关键词
    for keyword in IMPORTANT_KEYWORDS:
        if keyword.lower() in text:
            return True
    
    return False

def categorize_email(subject, body):
    """对邮件进行分类"""
    text = (subject + ' ' + body).lower()
    
    categories = {
        '财务': ['发票', '账单', '付款', '收款', '财务', 'invoice', 'payment', 'billing'],
        '项目': ['项目', '进度', '交付', 'milestone', 'project', 'deadline'],
        '系统': ['系统', '服务器', '部署', 'bug', 'error', 'server', 'deploy'],
        '人事': ['人事', '招聘', '面试', 'hr', 'employee', 'hire'],
        '合同': ['合同', '协议', '签署', 'contract', 'agreement', 'sign'],
        '审批': ['审批', '审核', '批准', 'approval', 'review', 'authorize']
    }
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in text:
                return category
    
    return '其他'

def fetch_emails():
    """收取邮件并分析"""
    print("正在连接邮箱服务器...")
    
    # 连接 IMAP 服务器
    mail = imaplib.IMAP4_SSL(EMAIL_CONFIG['imap_server'], EMAIL_CONFIG['imap_port'])
    mail.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['auth_code'])
    mail.select('INBOX')
    
    # 计算日期范围（从 2026-03-05 到今天）
    start_date = datetime(2026, 3, 5)
    end_date = datetime.now()
    
    print(f"收取邮件范围：{start_date.date()} 至 {end_date.date()}")
    
    # 搜索邮件
    search_date = start_date.strftime('%d-%b-%Y')
    status, messages = mail.search(None, f'(SINCE {search_date})')
    
    if status != 'OK':
        print("搜索邮件失败")
        return []
    
    email_ids = messages[0].split()
    total_emails = len(email_ids)
    print(f"找到 {total_emails} 封邮件")
    
    emails_data = []
    processed = 0
    
    # 分批处理邮件
    for email_id in email_ids:
        processed += 1
        if processed % 10 == 0:
            print(f"已处理 {processed}/{total_emails} 封邮件...")
        
        status, msg_data = mail.fetch(email_id, '(RFC822)')
        if status != 'OK':
            continue
        
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                
                # 提取基本信息
                subject = decode_mime_words(msg.get('Subject', ''))
                from_addr = decode_mime_words(msg.get('From', ''))
                date_str = msg.get('Date', '')
                
                # 解析日期
                try:
                    date_obj = email.utils.parsedate_to_datetime(date_str)
                    formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_date = date_str
                
                # 获取正文和附件
                body = get_email_body(msg)
                attachments = get_attachments(msg)
                
                # 判断重要性
                importance = is_important(subject, body, from_addr)
                category = categorize_email(subject, body) if importance else None
                
                emails_data.append({
                    'id': email_id.decode(),
                    'from': from_addr,
                    'date': formatted_date,
                    'subject': subject,
                    'body': body,
                    'attachments': attachments,
                    'important': importance,
                    'category': category
                })
    
    mail.close()
    mail.logout()
    
    print(f"邮件分析完成，共处理 {len(emails_data)} 封邮件")
    return emails_data

def generate_report(emails_data):
    """生成摘要报告"""
    
    # 筛选重要邮件
    important_emails = [e for e in emails_data if e['important']]
    total_count = len(emails_data)
    important_count = len(important_emails)
    
    # 按类别分组
    categories = {}
    for email in important_emails:
        cat = email['category'] or '其他'
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(email)
    
    # 收集有附件的邮件
    emails_with_attachments = [e for e in important_emails if e['attachments']]
    
    # 生成报告
    report = []
    report.append("# 📧 邮件摘要报告")
    report.append(f"**时间范围**: 2026-03-05 至 {datetime.now().strftime('%Y-%m-%d')}")
    report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # 今日概览
    report.append("## 📊 今日概览")
    report.append(f"- 总邮件数：**{total_count}**")
    report.append(f"- 重要邮件数：**{important_count}**")
    report.append(f"- 带附件的重要邮件：**{len(emails_with_attachments)}**")
    report.append("")
    
    # 高优先级事项
    report.append("## 🔴 高优先级事项")
    if important_emails:
        for i, email in enumerate(important_emails[:10], 1):  # 最多显示 10 封
            report.append(f"### {i}. {email['subject']}")
            report.append(f"- **发件人**: {email['from']}")
            report.append(f"- **时间**: {email['date']}")
            report.append(f"- **类别**: {email['category'] or '其他'}")
            if email['body']:
                # 清理正文，只显示关键内容
                body_preview = email['body'].replace('\n', ' ').strip()[:200]
                if len(email['body']) > 200:
                    body_preview += '...'
                report.append(f"- **内容摘要**: {body_preview}")
            if email['attachments']:
                att_names = ', '.join([a['filename'] for a in email['attachments']])
                report.append(f"- **附件**: {att_names}")
            report.append("")
    else:
        report.append("暂无高优先级事项。")
        report.append("")
    
    # 一般事项（按类别）
    report.append("## 📋 一般事项（按类别）")
    if categories:
        for category, emails in sorted(categories.items()):
            report.append(f"### {category} ({len(emails)}封)")
            for email in emails[:5]:  # 每类最多显示 5 封
                report.append(f"- {email['date']} | {email['from']} | {email['subject'][:50]}")
            if len(emails) > 5:
                report.append(f"- ... 还有 {len(emails) - 5} 封")
            report.append("")
    else:
        report.append("无分类事项。")
        report.append("")
    
    # 重要附件列表
    report.append("## 📎 重要附件列表")
    if emails_with_attachments:
        for email in emails_with_attachments:
            report.append(f"### {email['subject']}")
            for att in email['attachments']:
                report.append(f"- `{att['filename']}` ({att['content_type']})")
            report.append("")
    else:
        report.append("无重要附件。")
        report.append("")
    
    # 备注
    report.append("---")
    report.append("**备注**: 本报告已过滤系统通知、订阅邮件、广告等非重要邮件。")
    
    return '\n'.join(report)

def main():
    """主函数"""
    print("=" * 50)
    print("邮件分析助手启动")
    print("=" * 50)
    
    # 收取并分析邮件
    emails_data = fetch_emails()
    
    if not emails_data:
        print("未找到邮件")
        return
    
    # 生成报告
    report = generate_report(emails_data)
    
    # 保存报告
    report_dir = '/Users/a123456/.openclaw/workspace/email-reports'
    os.makedirs(report_dir, exist_ok=True)
    
    report_filename = f"{report_dir}/上周五至今 - 重要事项摘要.md"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("=" * 50)
    print(f"✅ 报告已保存至：{report_filename}")
    print(f"📊 总邮件数：{len(emails_data)}")
    print(f"🔴 重要邮件数：{len([e for e in emails_data if e['important']])}")
    print("=" * 50)

if __name__ == '__main__':
    main()
