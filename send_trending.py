import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def fetch_trending(since="weekly"):
    """抓取 GitHub Trending 数据"""
    url = f"https://githubtrending.lessx.xyz/trending?since={since}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()

def build_email_html(repos, since):
    """构建邮件 HTML 内容"""
    period_map = {"daily": "今日", "weekly": "本周", "monthly": "本月"}
    period = period_map.get(since, since)
    
    items_html = ""
   for i, repo in enumerate(repos[:20], 1):
    name = repo.get("fullName") or f"{repo.get('author')}/{repo.get('name')}"
    description = repo.get("description", "") or ""
    language = repo.get("language", "") or ""
    stars = repo.get("stars", 0)
    stars_today = repo.get("currentPeriodStars", 0)
    url = repo.get("url", f"https://github.com/{name}")
    forks = repo.get("forks", 0)
    
    # 提前格式化好数字，避免 f-string 中的语法冲突
    stars_str = f"{stars:,}"
    stars_today_str = f"{stars_today:,}"
    forks_str = f"{forks:,}"
    
    lang_badge = f'<span style="color:#6e7681;margin-left:8px;">● {language}</span>' if language else ""
    
    items_html += f"""
    <tr>
        <td style="padding:16px;border-bottom:1px solid #30363d;">
            <div style="font-size:16px;font-weight:600;">
                <a href="{url}" style="color:#58a6ff;text-decoration:none;">{name}</a>
            </div>
            <div style="color:#8b949e;margin:6px 0;font-size:14px;">{description}</div>
            <div style="font-size:12px;color:#6e7681;margin-top:8px;">
                ⭐ {stars_str} · 📈 {stars_today_str} stars today · 🍴 {forks_str}{lang_badge}
            </div>
        </td>
    </tr>"""
    
    html = f"""
    <html>
    <body style="background:#0d1117;color:#c9d1d9;font-family:-apple-system,BlinkMacSystemFont,sans-serif;">
        <div style="max-width:700px;margin:0 auto;padding:20px;">
            <h1 style="color:#58a6ff;border-bottom:2px solid #30363d;padding-bottom:12px;">
                🔥 GitHub Trending · {period}
            </h1>
            <p style="color:#8b949e;">更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <table style="width:100%;border-collapse:collapse;">{items_html}</table>
            <div style="text-align:center;margin-top:30px;color:#484f58;font-size:12px;">
                Powered by GitHub Actions · <a href="https://githubtrending.lessx.xyz" style="color:#484f58;">数据来源</a>
            </div>
        </div>
    </body>
    </html>"""
    return html

def send_email(html_content, to_email):
    """通过 QQ 邮箱 SMTP 发送邮件"""
    smtp_host = os.environ["SMTP_HOST"]
    smtp_port = int(os.environ["SMTP_PORT"])
    sender = os.environ["SENDER_EMAIL"]
    password = os.environ["SENDER_PASSWORD"]
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🔥 GitHub Trending 周报 - {datetime.now().strftime('%Y-%m-%d')}"
    msg["From"] = sender
    msg["To"] = to_email
    msg.attach(MIMEText(html_content, "html", "utf-8"))
    
    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(sender, password)
        server.sendmail(sender, to_email, msg.as_string())
    print("邮件发送成功！")

if __name__ == "__main__":
    since = os.environ.get("SINCE", "weekly")  # weekly / daily / monthly
    to_email = os.environ["TO_EMAIL"]
    
    print(f"正在抓取 {since} 的 GitHub Trending...")
    repos = fetch_trending(since)
    print(f"获取到 {len(repos)} 个仓库")
    
    html = build_email_html(repos, since)
    send_email(html, to_email)
