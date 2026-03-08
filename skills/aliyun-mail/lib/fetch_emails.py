#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云邮箱 - 邮件收取与总结
"""

import argparse
import os
import re
import sys
from datetime import datetime, timedelta
from email.header import decode_header
from pathlib import Path

# 邮件处理
try:
    from imap_tools import MailBox
except ImportError:
    print("❌ 缺少 imap-tools，运行：pip3 install imap-tools")
    sys.exit(1)

# 附件处理
try:
    from docx import Document as DocxDocument
    import openpyxl
    from pptx import Presentation
    from pypdf import PdfReader
except ImportError:
    print("❌ 缺少附件处理库，运行：pip3 install python-docx openpyxl python-pptx pypdf2")
    sys.exit(1)


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
                key = key.strip().lower().replace('-', '_')
                value = value.strip()
                current_account[key] = value
        
        if current_account:
            accounts.append(current_account)
    
    return accounts


def decode_mime(header):
    """解码 MIME 编码的邮件头"""
    if not header:
        return ''
    
    decoded = decode_header(header)
    result = ''
    for text, encoding in decoded:
        if isinstance(text, bytes):
            result += text.decode(encoding or 'utf-8', errors='replace')
        else:
            result += text
    return result


def extract_text_from_docx(file_path):
    """从 Word 文档提取文本"""
    try:
        doc = DocxDocument(file_path)
        return '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
    except Exception as e:
        return f"[Word 读取失败：{e}]"


def extract_text_from_xlsx(file_path):
    """从 Excel 提取文本（前 5 行）"""
    try:
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        texts = []
        for sheet_name in wb.sheetnames[:2]:  # 只读前 2 个工作表
            sheet = wb[sheet_name]
            for row_idx, row in enumerate(sheet.iter_rows(max_row=5, values_only=True)):
                if row_idx >= 5:
                    break
                cells = [str(cell) if cell is not None else '' for cell in row]
                if any(cells):
                    texts.append(' | '.join(cells))
        return '\n'.join(texts)
    except Exception as e:
        return f"[Excel 读取失败：{e}]"


def extract_text_from_pptx(file_path):
    """从 PPT 提取文本"""
    try:
        prs = Presentation(file_path)
        texts = []
        for slide_idx, slide in enumerate(prs.slides):
            if slide_idx >= 5:  # 只读前 5 页
                break
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    texts.append(shape.text.strip())
        return '\n'.join(texts)
    except Exception as e:
        return f"[PPT 读取失败：{e}]"


def extract_text_from_pdf(file_path):
    """从 PDF 提取文本"""
    try:
        reader = PdfReader(file_path)
        texts = []
        for page_idx, page in enumerate(reader.pages):
            if page_idx >= 5:  # 只读前 5 页
                break
            text = page.extract_text()
            if text:
                texts.append(text.strip())
        return '\n'.join(texts)
    except Exception as e:
        return f"[PDF 读取失败：{e}]"


def process_attachment(attach, output_dir):
    """处理附件，返回内容和保存路径"""
    if not attach.payload:
        return None, None
    
    filename = attach.filename
    if not filename:
        return None, None
    
    # 保存附件
    output_path = os.path.join(output_dir, filename)
    with open(output_path, 'wb') as f:
        f.write(attach.payload)
    
    # 根据类型提取文本
    content = None
    lower_name = filename.lower()
    
    if lower_name.endswith('.docx'):
        content = extract_text_from_docx(output_path)
    elif lower_name.endswith(('.xlsx', '.xls')):
        content = extract_text_from_xlsx(output_path)
    elif lower_name.endswith(('.pptx', '.ppt')):
        content = extract_text_from_pptx(output_path)
    elif lower_name.endswith('.pdf'):
        content = extract_text_from_pdf(output_path)
    
    return content, output_path


def fetch_emails(account, days=1, since=None, until=None):
    """收取邮件"""
    emails = []
    
    # 计算日期范围
    if since and until:
        date_from = datetime.strptime(since, '%Y-%m-%d')
        date_to = datetime.strptime(until, '%Y-%m-%d')
    else:
        date_to = datetime.now()
        date_from = date_to - timedelta(days=days)
    
    try:
        with MailBox(account['imap_server'], port=int(account.get('imap_port', 993)), 
                     ssl=True).login(account['email'], account['auth_code']) as mailbox:
            
            # 搜索日期范围内的邮件
            criteria = f'SINCE "{date_from.strftime("%d-%b-%Y")}"'
            
            for msg in mailbox.fetch(criteria, reverse=True):
                # 跳过自己发送的邮件
                if msg.from_ == account['email']:
                    continue
                
                email_data = {
                    'from': decode_mime(msg.from_),
                    'to': decode_mime(msg.to),
                    'subject': decode_mime(msg.subject),
                    'date': msg.date,
                    'text': msg.text or '',
                    'html': msg.html or '',
                    'attachments': [],
                    'account': account['email']
                }
                
                # 处理附件
                for attach in msg.attachments:
                    email_data['attachments'].append({
                        'filename': attach.filename,
                        'content_type': attach.content_type,
                        'size': len(attach.payload) if attach.payload else 0
                    })
                
                emails.append(email_data)
    
    except Exception as e:
        print(f"❌ 邮箱 {account['email']} 连接失败：{e}")
        return []
    
    return emails


def generate_summary(emails, include_attachments=True, output_dir=None):
    """生成邮件总结"""
    if not emails:
        return "📭 没有新邮件"
    
    summary = []
    summary.append(f"# 📧 邮件日报 ({datetime.now().strftime('%Y-%m-%d')})\n")
    
    # 概览
    total = len(emails)
    with_attachments = sum(1 for e in emails if e['attachments'])
    
    summary.append("## 概览")
    summary.append(f"- 总邮件数：{total}")
    summary.append(f"- 含附件：{with_attachments}\n")
    
    # 重点邮件（带附件的优先）
    summary.append("## 重点邮件\n")
    
    for idx, email in enumerate(emails[:10], 1):  # 最多显示 10 封
        summary.append(f"### {idx}. {email['subject'] or '(无主题)'}")
        summary.append(f"**发件人**: {email['from']}")
        summary.append(f"**时间**: {email['date'].strftime('%Y-%m-%d %H:%M')}")
        
        # 附件信息
        if email['attachments']:
            attach_list = ', '.join([a['filename'] for a in email['attachments']])
            summary.append(f"**附件**: {attach_list}")
            
            # 如果有输出目录，处理附件内容
            if output_dir and include_attachments:
                os.makedirs(output_dir, exist_ok=True)
                account = {'email': email['account'], 'imap_server': '', 'auth_code': ''}
                # 这里需要重新获取附件内容，简化处理
                summary.append("\n_附件内容需在完整模式下读取_")
        
        # 邮件正文摘要（前 200 字）
        text = email['text'][:500].strip() if email['text'] else ''
        if text:
            # 清理 HTML 标签
            text = re.sub(r'<[^>]+>', '', text)
            text = text[:200] + '...' if len(text) > 200 else text
            summary.append(f"\n**摘要**: {text}\n")
        
        summary.append("---\n")
    
    # 其他邮件
    if len(emails) > 10:
        summary.append(f"\n## 其他邮件 ({len(emails) - 10} 封)\n")
        for email in emails[10:]:
            summary.append(f"- {email['subject'] or '(无主题)'} - {email['from']}")
    
    return '\n'.join(summary)


def main():
    parser = argparse.ArgumentParser(description='阿里云邮箱工具')
    parser.add_argument('--action', required=True, choices=['summary', 'list', 'attachments', 'test'])
    parser.add_argument('--days', type=int, default=1, help='收取最近 N 天的邮件')
    parser.add_argument('--since', help='开始日期 YYYY-MM-DD')
    parser.add_argument('--until', help='结束日期 YYYY-MM-DD')
    parser.add_argument('--output-dir', default='./email-attachments', help='附件保存目录')
    parser.add_argument('--include-attachments', action='store_true', default=True)
    parser.add_argument('--send-feishu', action='store_true')
    parser.add_argument('--chat-id', help='飞书聊天 ID')
    
    args = parser.parse_args()
    
    # 加载凭证
    workspace_dir = Path(__file__).parent.parent.parent
    cred_file = workspace_dir / '.credentials' / 'aliyun-mail.md'
    
    if not cred_file.exists():
        print(f"❌ 凭证文件不存在：{cred_file}")
        print("请先创建凭证文件，参考：skills/aliyun-mail/README-授权码.md")
        sys.exit(1)
    
    accounts = parse_credentials(cred_file)
    
    if not accounts:
        print("❌ 凭证文件中没有有效的邮箱配置")
        sys.exit(1)
    
    print(f"📬 找到 {len(accounts)} 个邮箱账户")
    
    # 收取所有邮箱的邮件
    all_emails = []
    for account in accounts:
        print(f"\n正在收取 {account['email']} 的邮件...")
        emails = fetch_emails(
            account,
            days=args.days,
            since=args.since,
            until=args.until
        )
        print(f"  ✓ 收取 {len(emails)} 封邮件")
        all_emails.extend(emails)
    
    print(f"\n总计：{len(all_emails)} 封邮件")
    
    # 根据动作处理
    if args.action == 'test':
        print("\n✅ 邮箱连接测试成功")
        return
    
    if args.action == 'list':
        for email in all_emails:
            print(f"\n{email['date'].strftime('%Y-%m-%d %H:%M')} | {email['from']} | {email['subject']}")
            if email['attachments']:
                print(f"  附件：{', '.join([a['filename'] for a in email['attachments']])}")
        return
    
    if args.action == 'attachments':
        os.makedirs(args.output_dir, exist_ok=True)
        print(f"\n保存附件到：{args.output_dir}")
        # 简化处理，实际需要重新获取
        print("附件提取功能开发中...")
        return
    
    if args.action == 'summary':
        summary = generate_summary(
            all_emails,
            include_attachments=args.include_attachments,
            output_dir=args.output_dir if args.include_attachments else None
        )
        print("\n" + "="*60)
        print(summary)
        print("="*60)
        
        # 保存到文件
        output_file = workspace_dir / 'memory' / f"{datetime.now().strftime('%Y-%m-%d')}-email-summary.md"
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"\n💾 总结已保存：{output_file}")
        
        # 发送到飞书（待实现）
        if args.send_feishu and args.chat_id:
            print(f"\n📤 发送到飞书：{args.chat_id}")
            # 这里调用飞书 API
            print("飞书发送功能开发中...")


if __name__ == '__main__':
    main()
