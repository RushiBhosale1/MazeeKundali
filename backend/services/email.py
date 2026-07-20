import logging
import base64
from typing import Optional
from api.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

def send_pdf_email_sync(to_email: str, subject: str, html_body: str, pdf_bytes: bytes, filename: str) -> bool:
    """
    Sends an email with a PDF attachment using the Resend API.
    Runs synchronously (can be called from ThreadPoolExecutor).
    """
    if not settings.resend_api_key:
        logger.warning(f"Resend API key not configured. Skipping email to {to_email}")
        return False

    try:
        import resend
        resend.api_key = settings.resend_api_key

        # Convert PDF bytes to base64 for attachment
        pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')

        params = {
            "from": f"Mazeekundali <{settings.resend_from_email}>",
            "to": to_email,
            "subject": subject,
            "html": html_body,
            "attachments": [
                {
                    "filename": filename,
                    "content": pdf_b64,
                }
            ]
        }

        email = resend.Emails.send(params)
        logger.info(f"Email sent successfully to {to_email} via Resend. ID: {email.get('id')}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

async def send_pdf_email(to_email: str, subject: str, html_body: str, pdf_bytes: bytes, filename: str) -> bool:
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=1) as pool:
        return await loop.run_in_executor(pool, send_pdf_email_sync, to_email, subject, html_body, pdf_bytes, filename)
