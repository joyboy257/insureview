import smtplib
import asyncio
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


def _build_email(from_addr: str, to_addr: str, subject: str, html_body: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["List-Unsubscribe"] = f"<mailto:unsubscribe@insureview.sg?subject=unsubscribe:{to_addr}>"
    part = MIMEText(html_body, "html")
    msg.attach(part)
    return msg


def _smtp_send(msg: MIMEMultipart) -> None:
    with smtplib.SMTP(settings.email_server_host, settings.email_server_port) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        if settings.email_server_user and settings.email_server_pass:
            server.login(settings.email_server_user, settings.email_server_pass)
        server.sendmail(msg["From"], msg["To"], msg.as_bytes())


async def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    from_email: Optional[str] = None,
) -> bool:
    """
    Send an HTML email asynchronously using asyncio.to_thread for the blocking SMTP call.
    Returns True on success, False on failure.
    """
    from_addr = from_email or settings.email_from
    try:
        msg = _build_email(from_addr, to_email, subject, html_body)
        await asyncio.to_thread(_smtp_send, msg)
        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as exc:
        logger.exception(f"Failed to send email to {to_email}: {exc}")
        return False


# ── Email templates ─────────────────────────────────────────────────────────────

PARSE_COMPLETE_TEMPLATE = """
<html>
<body style="font-family: Inter, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px;">
  <div style="background: hsl(174,52%,32%); padding: 24px; border-radius: 8px 8px 0 0;">
    <h1 style="color: white; margin: 0; font-size: 20px;">Insureview</h1>
  </div>
  <div style="border: 1px solid hsl(214.3,31.8%,91.4%); border-top: none; padding: 24px; border-radius: 0 0 8px 8px;">
    <h2 style="color: hsl(222.2,84%,4.9%); margin-top: 0;">Your policy has been parsed</h2>
    <p style="color: hsl(215.4,16.3%,46.9%);">Great news — <strong>{filename}</strong> has been successfully analyzed.</p>
    <p style="color: hsl(215.4,16.3%,46.9%);">You can now view your full portfolio analysis on Insureview.</p>
    <a href="{dashboard_url}" style="display: inline-block; background: hsl(174,52%,32%); color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 600; margin-top: 16px;">View My Portfolio</a>
    <hr style="border: none; border-top: 1px solid hsl(214.3,31.8%,91.4%); margin: 24px 0;">
    <p style="font-size: 12px; color: hsl(215.4,16.3%,46.9%);">
      You received this because you uploaded a policy to Insureview.<br>
      <a href="{unsubscribe_url}">Unsubscribe</a>
    </p>
  </div>
</body>
</html>
"""

GAP_DETECTED_TEMPLATE = """
<html>
<body style="font-family: Inter, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px;">
  <div style="background: hsl(174,52%,32%); padding: 24px; border-radius: 8px 8px 0 0;">
    <h1 style="color: white; margin: 0; font-size: 20px;">Insureview</h1>
  </div>
  <div style="border: 1px solid hsl(214.3,31.8%,91.4%); border-top: none; padding: 24px; border-radius: 0 0 8px 8px;">
    <h2 style="color: hsl(222.2,84%,4.9%); margin-top: 0;">New gap detected in your portfolio</h2>
    <p style="color: hsl(215.4,16.3%,46.9%);">We found <strong>{gap_count} new coverage gap{gap_plural}</strong> in your portfolio after analyzing {policy_count} policy{policy_plural}.</p>
    <ul style="color: hsl(215.4,16.3%,46.9%);">
      {gap_items}
    </ul>
    <a href="{dashboard_url}" style="display: inline-block; background: hsl(174,52%,32%); color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 600; margin-top: 16px;">View Gap Analysis</a>
    <hr style="border: none; border-top: 1px solid hsl(214.3,31.8%,91.4%); margin: 24px 0;">
    <p style="font-size: 12px; color: hsl(215.4,16.3%,46.9%);">
      Insureview monitors your portfolio and alerts you when gaps are found.<br>
      <a href="{unsubscribe_url}">Unsubscribe from gap alerts</a>
    </p>
  </div>
</body>
</html>
"""


async def send_parse_complete_email(
    to_email: str,
    filename: str,
    dashboard_url: str,
) -> bool:
    subject = f"Your policy '{filename}' is ready"
    html = PARSE_COMPLETE_TEMPLATE.format(
        filename=filename,
        dashboard_url=dashboard_url,
        unsubscribe_url=f"{dashboard_url}#unsubscribe",
    )
    return await send_email(to_email, subject, html)


async def send_gap_detected_email(
    to_email: str,
    gap_count: int,
    policy_count: int,
    gap_names: list[str],
    dashboard_url: str,
) -> bool:
    subject = f"New: {gap_count} coverage gap{gap_count != 1 and 's' or ''} found"
    gap_items_html = "".join(f"<li>{name}</li>" for name in gap_names[:5])
    if gap_count > 5:
        gap_items_html += f"<li>...and {gap_count - 5} more</li>"
    html = GAP_DETECTED_TEMPLATE.format(
        gap_count=gap_count,
        gap_plural=gap_count != 1 and "s" or "",
        policy_count=policy_count,
        policy_plural=policy_count != 1 and "s" or "",
        gap_items=gap_items_html,
        dashboard_url=dashboard_url,
        unsubscribe_url=f"{dashboard_url}#unsubscribe",
    )
    return await send_email(to_email, subject, html)
