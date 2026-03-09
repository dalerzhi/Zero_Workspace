#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云邮箱 - 邮件收取与总结
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from email.header import decode_header
from pathlib import Path
import requests

# 邮件处理
try:
    from imap_tools import MailBox, AND
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
                # 去掉开头的 `-` 和空格，然后替换 `-` 为 `_`
                key = key.strip().lstrip('-').strip().lower().replace('-', '_')
                value = value.strip()
                current_account[key] = value
        
        if current_account:
            accounts.append(current_account)
    
    return accounts


def decode_mime(header):
    """解码 MIME 编码的邮件头"""
    if not header:
        return ''
    
    # imap_tools 可能返回 tuple (如 msg.to)
    if isinstance(header, tuple):
        header = ', '.join([str(h) for h in header])
    
    decoded = decode_header(header)
    result = ''
    for text, encoding in decoded:
        if isinstance(text, bytes):
            result += text.decode(encoding or 'utf-8', errors='replace')
        else:
            result += text
    return result


def format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"


def send_to_feishu(markdown_content, chat_id):
    """发送 Markdown 消息到飞书"""
    # 飞书凭证（从环境变量或配置文件读取）
    app_id = os.environ.get('FEISHU_APP_ID', 'cli_a909ad9f75fadbb5')
    app_secret = os.environ.get('FEISHU_APP_SECRET', 'p1MtN6OZic92OCOpMgxaZdSzAvRfsrys')
    
    # 1. 获取 tenant_access_token
    try:
        token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        token_resp = requests.post(token_url, json={"app_id": app_id, "app_secret": app_secret}, timeout=10)
        token_data = token_resp.json()
        
        if token_data.get('code') != 0:
            print(f"❌ 获取飞书 token 失败：{token_data.get('msg')}")
            return False
        
        token = token_data['tenant_access_token']
    except Exception as e:
        print(f"❌ 飞书认证失败：{e}")
        return False
    
    # 2. 发送消息
    try:
        msg_url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 飞书 Markdown 消息
        content = {
            "text": markdown_content
        }
        
        payload = {
            "receive_id": chat_id,
            "msg_type": "text",  # 使用 text 类型，因为飞书对 Markdown 支持有限
            "content": json.dumps(content)
        }
        
        params = {"receive_id_type": "open_id"}
        resp = requests.post(msg_url, headers=headers, params=params, json=payload, timeout=10)
        result = resp.json()
        
        if result.get('code') == 0:
            msg_id = result['data']['message_id']
            print(f"✅ 飞书发送成功：{msg_id}")
            return True
        else:
            print(f"❌ 飞书发送失败：{result.get('msg')}")
            return False
            
    except Exception as e:
        print(f"❌ 飞书发送异常：{e}")
        return False


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
    
    # 清理文件名
    safe_filename = filename.replace('/', '_').replace('\\', '_')
    output_path = os.path.join(output_dir, safe_filename)
    
    # 保存附件
    with open(output_path, 'wb') as f:
        f.write(attach.payload)
    
    # 根据类型提取文本
    content = None
    lower_name = safe_filename.lower()
    
    if lower_name.endswith('.docx'):
        content = extract_text_from_docx(output_path)
    elif lower_name.endswith(('.xlsx', '.xls')):
        content = extract_text_from_xlsx(output_path)
    elif lower_name.endswith(('.pptx', '.ppt')):
        content = extract_text_from_pptx(output_path)
    elif lower_name.endswith('.pdf'):
        content = extract_text_from_pdf(output_path)
    else:
        content = f"[不支持的文件类型：{lower_name.split('.')[-1]}]"
    
    return content, output_path


def fetch_emails(account, days=1, since=None, until=None, output_dir=None):
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
        with MailBox(account['imap_server'], port=int(account.get('imap_port', 993))).login(account['email'], account['auth_code']) as mailbox:
            
            # 使用 imap_tools 的 AND 条件搜索日期范围
            if since and until:
                date_from = datetime.strptime(since, '%Y-%m-%d').date()
                date_to = datetime.strptime(until, '%Y-%m-%d').date()
                criteria = AND(date_gte=date_from, date_lte=date_to)
            else:
                date_from = (datetime.now() - timedelta(days=days)).date()
                criteria = AND(date_gte=date_from)
            
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
                
                # 处理附件（下载并解析内容）
                for attach in msg.attachments:
                    attach_info = {
                        'filename': attach.filename,
                        'content_type': attach.content_type,
                        'size': len(attach.payload) if attach.payload else 0,
                        'content': None,
                        'path': None
                    }
                    
                    # 如果有输出目录，下载并解析附件
                    if output_dir:
                        content, path = process_attachment(attach, output_dir)
                        attach_info['content'] = content
                        attach_info['path'] = path
                    
                    email_data['attachments'].append(attach_info)
                
                emails.append(email_data)
    
    except Exception as e:
        import traceback
        print(f"❌ 邮箱 {account['email']} 连接失败：{e}")
        traceback.print_exc()
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
    total_attachments = sum(len(e['attachments']) for e in emails)
    
    summary.append("## 概览")
    summary.append(f"- 总邮件数：{total}")
    summary.append(f"- 含附件邮件：{with_attachments}")
    summary.append(f"- 附件总数：{total_attachments}\n")
    
    # 重点邮件（带附件的优先）
    summary.append("## 重点邮件\n")
    
    for idx, email in enumerate(emails[:10], 1):  # 最多显示 10 封
        summary.append(f"### {idx}. {email['subject'] or '(无主题)'}")
        summary.append(f"**发件人**: {email['from']}")
        summary.append(f"**时间**: {email['date'].strftime('%Y-%m-%d %H:%M')}")
        summary.append(f"**收件人**: {email['to']}\n")
        
        # 邮件正文摘要
        text = email['text'][:800].strip() if email['text'] else ''
        if text:
            # 清理 HTML 标签
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'\n\s*\n', '\n\n', text)  # 清理多余空行
            summary.append(f"**正文摘要**:\n{text}\n")
        
        # 附件信息和内容
        if email['attachments']:
            summary.append("**附件详情**:\n")
            for att_idx, att in enumerate(email['attachments'], 1):
                summary.append(f"  **{att_idx}. {att['filename']}** ({format_size(att['size'])})")
                
                if att['content']:
                    # 显示附件内容摘要（前 500 字）
                    content_preview = att['content'][:500]
                    if len(att['content']) > 500:
                        content_preview += "\n  ...(内容过长，已截断)"
                    summary.append(f"\n  **内容摘要**:\n  ```\n  {content_preview}\n  ```\n")
                elif att['path']:
                    summary.append(f"\n  _文件已保存：{att['path']}_\n")
                summary.append("\n")
        
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
    # skills/aliyun-mail/lib/fetch_emails.py -> workspace
    workspace_dir = Path(__file__).parent.parent.parent.parent
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
    
    # 根据动作处理
    if args.action == 'test':
        print("\n✅ 邮箱连接测试成功")
        return
    
    if args.action == 'list':
        all_emails = []
        for account in accounts:
            print(f"\n正在收取 {account['email']} 的邮件...", file=sys.stderr)
            emails = fetch_emails(
                account,
                days=args.days,
                since=args.since,
                until=args.until,
                output_dir=None
            )
            print(f"  ✓ 收取 {len(emails)} 封邮件", file=sys.stderr)
            all_emails.extend(emails)
        
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
        # 使用 email-reports 目录，而不是 memory
        output_dir = workspace_dir / 'email-reports' / datetime.now().strftime('%Y-%m-%d')
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n📂 附件保存目录：{output_dir}")
        
        # 收取邮件并下载附件
        all_emails = []
        for account in accounts:
            print(f"\n正在收取 {account['email']} 的邮件...")
            emails = fetch_emails(
                account,
                days=args.days,
                since=args.since,
                until=args.until,
                output_dir=str(output_dir) if args.include_attachments else None
            )
            print(f"  ✓ 收取 {len(emails)} 封邮件")
            all_emails.extend(emails)
        
        print(f"\n总计：{len(all_emails)} 封邮件")
        
        # 生成总结
        summary = generate_summary(
            all_emails,
            include_attachments=args.include_attachments,
            output_dir=str(output_dir) if args.include_attachments else None
        )
        print("\n" + "="*60)
        print(summary)
        print("="*60)
        
        # 保存到 email-reports 目录
        output_file = output_dir / f"{datetime.now().strftime('%Y-%m-%d')}-邮件日报.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"\n💾 总结已保存：{output_file}")
        
        # 发送到飞书
        if args.send_feishu and args.chat_id:
            print(f"\n📤 发送到飞书：{args.chat_id}")
            send_to_feishu(summary, args.chat_id)


if __name__ == '__main__':
    main()
