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
        author = repo.get("author") or ""
        repo_name = repo.get("name") or ""
        full_name = repo.get("fullName")
        if full_name and "/" in full_name:
            name = full_name
        elif author and repo_name:
            name = f"{author}/{repo_name}"
        else:
            name = full_name or repo_name or "unknown"

        description = repo.get("description", "") or ""
        language = repo.get("language", "") or ""
        stars = int(repo.get("stars", 0) or 0)
        stars_today = int(repo.get("currentPeriodStars", 0) or 0)
        url = repo.get("url", f"https://github.com/{name}")
        forks = int(repo.get("forks", 0) or 0)

        stars_str = f"{stars:,}"
        stars_today_str = f"{stars_today:,}"
        forks_str = f"{forks:,}"

        lang_badge = ""
        if language:
            lang_badge = f'<span style="display:inline-flex;align-items:center;gap:4px;margin-left:12px;padding:2px 8px;background:rgba(110,118,129,0.15);border-radius:9999px;font-size:11px;color:#8b949e;"><span style="width:8px;height:8px;border-radius:50%;background:#58a6ff;display:inline-block;"></span>{language}</span>'

        items_html += f"""
        <tr>
            <td style="padding:20px;border-bottom:1px solid #21262d;vertical-align:top;">
                <div style="display:flex;align-items:flex-start;gap:16px;">
                    <div style="flex-shrink:0;width:32px;height:32px;background:linear-gradient(135deg,#1f6feb,#58a6ff);border-radius:8px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:14px;font-weight:700;">{i}</div>
                    <div style="flex:1;min-width:0;">
                        <div style="font-size:16px;font-weight:600;margin-bottom:6px;">
                            <a href="{url}" style="color:#58a6ff;text-decoration:none;">{name}</a>
                        </div>
                        <div style="color:#8b949e;margin-bottom:12px;font-size:14px;line-height:1.6;">{description}</div>
                        <div style="display:flex;align-items:center;flex-wrap:wrap;gap:12px;font-size:13px;color:#6e7681;">
                            <span style="display:inline-flex;align-items:center;gap:4px;">
                                <svg width="14" height="14" viewBox="0 0 16 16" fill="#e3b341" style="vertical-align:middle;"><path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.75.75 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"/></svg>
                                {stars_str}
                            </span>
                            <span style="display:inline-flex;align-items:center;gap:4px;color:#3fb950;">
                                <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor" style="vertical-align:middle;"><path d="M4.22 4.22a.75.75 0 0 1 1.06 0l2.69 2.689V1.75a.75.75 0 0 1 1.5 0v5.159l2.69-2.689a.75.75 0 1 1 1.06 1.061l-3.889 3.89a.75.75 0 0 1-1.06 0L4.22 5.28a.75.75 0 0 1 0-1.06Z"/><path d="M8.75 14.5a.75.75 0 0 1-.75-.75v-5.5H6.274l-1.966 1.967a.75.75 0 0 1-1.06-1.06l3.889-3.89a.75.75 0 0 1 1.06 0l3.889 3.89a.75.75 0 0 1-1.06 1.06L9.5 8.25H8.75v5.5a.75.75 0 0 1-.75.75Z"/></svg>
                                {stars_today_str} today
                            </span>
                            <span style="display:inline-flex;align-items:center;gap:4px;">
                                <svg width="14" height="14" viewBox="0 0 16 16" fill="#8b949e" style="vertical-align:middle;"><path d="M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z"/></svg>
                                {forks_str}
                            </span>
                            {lang_badge}
                        </div>
                    </div>
                </div>
            </td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Trending</title>
</head>
<body style="margin:0;padding:0;background:#0d1117;color:#c9d1d9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;line-height:1.5;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background:#0d1117;">
        <tr>
            <td align="center" style="padding:40px 16px;">
                <table role="presentation" width="100%" max-width="720" cellspacing="0" cellpadding="0" border="0" style="max-width:720px;width:100%;background:#161b22;border-radius:16px;border:1px solid #30363d;overflow:hidden;">
                    <tr>
                        <td style="padding:32px 32px 24px;border-bottom:1px solid #21262d;background:linear-gradient(135deg,#161b22 0%,#1c2128 100%);">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td>
                                        <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
                                            <div style="width:40px;height:40px;background:linear-gradient(135deg,#f78166,#ff7b72);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;">🔥</div>
                                            <h1 style="margin:0;font-size:28px;font-weight:700;color:#f0f6fc;letter-spacing:-0.5px;">GitHub Trending</h1>
                                        </div>
                                        <p style="margin:0;color:#8b949e;font-size:15px;">{period}热门仓库精选 · {datetime.now().strftime('%Y-%m-%d')}</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">{items_html}</table>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:24px 32px;border-top:1px solid #21262d;background:#0d1117;text-align:center;">
                            <p style="margin:0 0 8px;color:#484f58;font-size:13px;">Powered by GitHub Actions</p>
                            <a href="https://githubtrending.lessx.xyz" style="color:#58a6ff;text-decoration:none;font-size:13px;">数据来源：githubtrending.lessx.xyz</a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
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
    since = os.environ.get("SINCE", "weekly")
    to_email = os.environ.get("TO_EMAIL")

    print(f"正在抓取 {since} 的 GitHub Trending...")
    repos = fetch_trending(since)
    print(f"获取到 {len(repos)} 个仓库")

    html = build_email_html(repos, since)
    send_email(html, to_email)
