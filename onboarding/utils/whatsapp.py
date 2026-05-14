from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_invitation_whatsapp(employee_phone, employee_name, invitation_token, portal_url=None):
    """
    Send invitation via WhatsApp to new joiner using Twilio

    Args:
        employee_phone: Phone number with country code (e.g., +91XXXXXXXXXX)
        employee_name: Name of the employee
        invitation_token: Unique token for onboarding portal
        portal_url: Base URL for onboarding portal (e.g., http://example.com)

    Returns:
        bool: True if WhatsApp sent successfully, False otherwise
    """
    try:
        if not portal_url:
            portal_url = "http://65.2.31.152"  # Default to live URL

        # Initialize Twilio client
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        whatsapp_from = settings.TWILIO_WHATSAPP_FROM

        if not all([account_sid, auth_token, whatsapp_from]):
            logger.warning("Twilio credentials not configured in settings")
            return False

        client = Client(account_sid, auth_token)

        onboarding_link = f"{portal_url}/onboarding/join/{invitation_token}/"

        message_body = f"""
Hello {employee_name}! 👋

Welcome to our organization! We're excited to have you join our team.

Please complete your onboarding by clicking the link below:

{onboarding_link}

This link will expire in 30 days.

If you have any questions, please contact our HR team.

Best regards,
HR Team
        """.strip()

        message = client.messages.create(
            from_=whatsapp_from,
            body=message_body,
            to=f"whatsapp:{employee_phone}"
        )

        logger.info(f"WhatsApp invitation sent to {employee_phone} with message SID: {message.sid}")
        return True

    except Exception as e:
        logger.error(f"Error sending WhatsApp invitation to {employee_phone}: {str(e)}")
        return False


def send_status_update_whatsapp(employee_phone, employee_name, status_message):
    """
    Send status update via WhatsApp to employee

    Args:
        employee_phone: Phone number with country code
        employee_name: Name of the employee
        status_message: The status message to send (e.g., "Documents received", "Offer signed")

    Returns:
        bool: True if WhatsApp sent successfully, False otherwise
    """
    try:
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        whatsapp_from = settings.TWILIO_WHATSAPP_FROM

        if not all([account_sid, auth_token, whatsapp_from]):
            logger.warning("Twilio credentials not configured in settings")
            return False

        client = Client(account_sid, auth_token)

        message_body = f"""
Hi {employee_name},

{status_message}

If you have any questions, please don't hesitate to reach out to our HR team.

Best regards,
HR Team
        """.strip()

        message = client.messages.create(
            from_=whatsapp_from,
            body=message_body,
            to=f"whatsapp:{employee_phone}"
        )

        logger.info(f"WhatsApp status update sent to {employee_phone} with message SID: {message.sid}")
        return True

    except Exception as e:
        logger.error(f"Error sending WhatsApp status update to {employee_phone}: {str(e)}")
        return False


def send_document_reminder_whatsapp(employee_phone, employee_name, portal_url=None):
    """
    Send document upload reminder via WhatsApp

    Args:
        employee_phone: Phone number with country code
        employee_name: Name of the employee
        portal_url: Base URL for onboarding portal

    Returns:
        bool: True if WhatsApp sent successfully, False otherwise
    """
    try:
        if not portal_url:
            portal_url = "http://65.2.31.152"

        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        whatsapp_from = settings.TWILIO_WHATSAPP_FROM

        if not all([account_sid, auth_token, whatsapp_from]):
            logger.warning("Twilio credentials not configured in settings")
            return False

        client = Client(account_sid, auth_token)

        message_body = f"""
Hi {employee_name},

This is a reminder to upload your required documents for onboarding. Please visit the portal to upload:

📄 Resume/CV
🆔 ID Proof (Aadhar/Passport)
📍 Address Proof
🏦 Bank Details Form

Documents must be in PDF, JPG, or PNG format and under 5MB each.

Portal: {portal_url}

Thank you!
HR Team
        """.strip()

        message = client.messages.create(
            from_=whatsapp_from,
            body=message_body,
            to=f"whatsapp:{employee_phone}"
        )

        logger.info(f"WhatsApp document reminder sent to {employee_phone} with message SID: {message.sid}")
        return True

    except Exception as e:
        logger.error(f"Error sending WhatsApp document reminder to {employee_phone}: {str(e)}")
        return False
