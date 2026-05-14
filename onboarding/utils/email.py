from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_invitation_email(employee, invitation_token, portal_url=None):
    """
    Send invitation email to new joiner

    Args:
        employee: Employee object
        invitation_token: Unique token for onboarding portal
        portal_url: Base URL for onboarding portal (e.g., http://example.com)

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        if not portal_url:
            portal_url = "http://65.2.31.152"  # Default to live URL

        onboarding_link = f"{portal_url}/onboarding/join/{invitation_token}/"

        # Email content
        subject = f"Welcome to {settings.DEFAULT_FROM_EMAIL.split('@')[1].upper()}! Complete Your Onboarding"

        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2>Welcome, {employee.name}!</h2>
                <p>We're excited to have you join our team!</p>
                <p>To complete your onboarding and get started, please click the link below:</p>
                <p><a href="{onboarding_link}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Complete Your Onboarding
                </a></p>
                <p>Or copy and paste this link in your browser:</p>
                <p><code>{onboarding_link}</code></p>
                <p>This link will expire in 30 days.</p>
                <hr>
                <p><strong>Your Details:</strong></p>
                <ul>
                    <li>Name: {employee.name}</li>
                    <li>Employee ID: {employee.employee_id}</li>
                    <li>Department: {employee.department.name if employee.department else 'N/A'}</li>
                    <li>Position: {employee.position}</li>
                    <li>Start Date: {employee.date_joined.strftime('%d %b %Y')}</li>
                </ul>
                <p>If you have any questions, please contact HR.</p>
                <p>Best regards,<br>HR Team</p>
            </body>
        </html>
        """

        text_message = strip_tags(html_message)

        # Send email
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[employee.email],
            html_message=html_message,
            fail_silently=False,
        )

        return True

    except Exception as e:
        print(f"Error sending invitation email to {employee.email}: {str(e)}")
        return False


def send_offer_letter_email(offer_letter):
    """
    Send offer letter via email

    Args:
        offer_letter: OfferLetter object

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        employee = offer_letter.employee
        subject = f"Offer Letter - {employee.name}"

        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2>Offer Letter</h2>
                <p>Dear {employee.name},</p>
                <p>We are pleased to extend an offer of employment to you!</p>
                <p><strong>Offer Details:</strong></p>
                <ul>
                    <li>Position: {offer_letter.department}</li>
                    <li>Annual Salary: ₹{offer_letter.salary_amount:,.2f}</li>
                    <li>Start Date: {offer_letter.start_date.strftime('%d %b %Y')}</li>
                </ul>
                <p>Please find the complete offer letter attached or in the onboarding portal.</p>
                <p>Please review the offer and confirm your acceptance in the onboarding portal.</p>
                <p>Best regards,<br>HR Team</p>
            </body>
        </html>
        """

        text_message = strip_tags(html_message)

        # Create email with attachment
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[employee.email]
        )
        email.attach_alternative(html_message, "text/html")

        # Attach PDF if available
        if offer_letter.pdf_file:
            with offer_letter.pdf_file.open('rb') as pdf:
                email.attach('offer_letter.pdf', pdf.read(), 'application/pdf')

        email.send(fail_silently=False)
        return True

    except Exception as e:
        print(f"Error sending offer letter email to {employee.email}: {str(e)}")
        return False


def send_document_request_email(employee, invitation_token, portal_url=None):
    """
    Send document request email to new joiner

    Args:
        employee: Employee object
        invitation_token: Unique token for onboarding portal
        portal_url: Base URL for onboarding portal

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        if not portal_url:
            portal_url = "http://65.2.31.152"

        documents_link = f"{portal_url}/onboarding/documents/{invitation_token}/"

        subject = f"Please Upload Required Documents - {employee.name}"

        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2>Document Submission Required</h2>
                <p>Dear {employee.name},</p>
                <p>To complete your onboarding, we need you to upload the following documents:</p>
                <ul>
                    <li>Resume/CV</li>
                    <li>ID Proof (Aadhar/Passport)</li>
                    <li>Address Proof</li>
                    <li>Bank Details Form</li>
                </ul>
                <p><a href="{documents_link}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Upload Documents
                </a></p>
                <p>Please ensure all documents are in PDF, JPG, or PNG format and under 5MB each.</p>
                <p>Best regards,<br>HR Team</p>
            </body>
        </html>
        """

        text_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[employee.email],
            html_message=html_message,
            fail_silently=False,
        )

        return True

    except Exception as e:
        print(f"Error sending document request email to {employee.email}: {str(e)}")
        return False


def send_onboarding_complete_email(employee):
    """
    Send completion confirmation email

    Args:
        employee: Employee object

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = "Onboarding Complete - Welcome Aboard!"

        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2>Welcome Aboard, {employee.name}!</h2>
                <p>Congratulations! You have successfully completed your onboarding.</p>
                <p>You will receive your login credentials shortly.</p>
                <p><strong>Your First Day Details:</strong></p>
                <ul>
                    <li>Start Date: {employee.date_joined.strftime('%d %b %Y')}</li>
                    <li>Department: {employee.department.name if employee.department else 'N/A'}</li>
                    <li>Position: {employee.position}</li>
                </ul>
                <p>The HR team will contact you to confirm onboarding arrangements.</p>
                <p>If you have any questions, please don't hesitate to reach out.</p>
                <p>Best regards,<br>HR Team</p>
            </body>
        </html>
        """

        text_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[employee.email],
            html_message=html_message,
            fail_silently=False,
        )

        return True

    except Exception as e:
        print(f"Error sending completion email to {employee.email}: {str(e)}")
        return False
