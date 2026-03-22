import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_news_email(to_email, news_dict):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise EnvironmentError("❌ EMAIL_ADDRESS or EMAIL_PASSWORD not set in .env")

    subject = "PromptPress News Update"
    body = """
    <html>
    <head>
      <style>
        body { font-family: Inter,Arial,sans-serif; }
        .news-topic { margin-bottom: 32px; }
        .news-article { border-bottom: 1px solid #eaeaea; padding-bottom: 12px; margin-bottom: 18px; display: flex; align-items: flex-start; }
        .news-content { flex: 1; }
        .news-image { width: 100px; height: 65px; object-fit: cover; border-radius: 8px; margin-right: 20px; }
        .title { font-weight: 600; margin-bottom: 2px; color: #1641bc; }
        .desc { color: #222; font-size: 0.97em; }
        .link { font-size: 0.93em; color: #2967e0; text-decoration: none; word-break:break-all; }
      </style>
    </head>
    <body>
      <h2>🧠 Your AI News Digest</h2>
    """

    for topic, news in news_dict.items():
        body += f'<div class="news-topic"><h3>{topic}</h3>'
        if isinstance(news, str):
            body += f"<p>{news}</p>"   # e.g., API error message
        elif isinstance(news, list) and news:
            for article in news:
                img_html = f'<img src="{article.get("image")}" class="news-image" alt="Image">' if article.get("image") else ''
                body += f'''
                    <div class="news-article">
                      {img_html}
                      <div class="news-content">
                        <div class="title">{article.get("title", "No title")}</div>
                        <div class="desc">{article.get("description","")}</div>
                        <a class="link" href="{article.get("link","#")}">Read more</a>
                      </div>
                    </div>
                '''
        else:
            body += "<p>No news found for this topic.</p>"
        body += '</div>'

    body += "</body></html>"

    # Construct email
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Error sending email to {to_email}: {e}")
        raise