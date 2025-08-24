import os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.utils.logging import logger
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pathlib

def send_invoice_email(to_email: str, subject: str, html_body: str):
    host = os.getenv("SMTP_HOST"); port = int(os.getenv("SMTP_PORT","587"))
    user = os.getenv("SMTP_USER"); pwd = os.getenv("SMTP_PASS")
    if not (host and user and pwd):
        logger.warning("SMTP not configured; skipping email send")
        return False
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject; msg["From"] = user; msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))
    with smtplib.SMTP(host, port) as server:
        server.starttls(); server.login(user, pwd); server.sendmail(user, [to_email], msg.as_string())
    return True

def render_invoice_html(**ctx):
    templates_dir = pathlib.Path(__file__).resolve().parents[1] / "templates"
    env = Environment(loader=FileSystemLoader(str(templates_dir)), autoescape=select_autoescape())
    tpl = env.get_template("invoice_email.html")
    return tpl.render(**ctx)
