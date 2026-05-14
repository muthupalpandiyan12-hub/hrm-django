from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from io import BytesIO
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def generate_offer_letter_pdf(offer_letter):
    """
    Generate professional offer letter PDF for new joiner

    Args:
        offer_letter: OfferLetter object with employee and offer details

    Returns:
        BytesIO: PDF file object in memory, None if generation failed
    """
    try:
        # Create BytesIO buffer for PDF
        buffer = BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )

        # Container for PDF elements
        elements = []

        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=1,  # Center alignment
            fontName='Helvetica-Bold'
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            spaceAfter=12,
            leading=14,
            alignment=4,  # Justified alignment
        )

        # Company header
        company_name = settings.DEFAULT_FROM_EMAIL.split('@')[1].upper()
        elements.append(Paragraph(company_name, title_style))
        elements.append(Spacer(1, 0.2*inch))

        # Offer letter title
        elements.append(Paragraph("OFFER OF EMPLOYMENT", heading_style))
        elements.append(Spacer(1, 0.2*inch))

        # Date and reference
        today = datetime.now().strftime('%d %B %Y')
        date_text = f"<b>Date:</b> {today}<br/><b>To:</b> {offer_letter.employee.name}"
        elements.append(Paragraph(date_text, body_style))
        elements.append(Spacer(1, 0.3*inch))

        # Opening paragraph
        opening = f"Dear {offer_letter.employee.name},"
        elements.append(Paragraph(opening, body_style))
        elements.append(Spacer(1, 0.15*inch))

        # Main offer content
        offer_intro = "We are pleased to extend an offer of employment to you for the position of <b>{}</b> in our esteemed organization.".format(
            offer_letter.department
        )
        elements.append(Paragraph(offer_intro, body_style))
        elements.append(Spacer(1, 0.15*inch))

        # Offer details table
        elements.append(Paragraph("<b>Offer Details:</b>", heading_style))

        offer_data = [
            ['Position', offer_letter.department],
            ['Annual Salary', '₹{:,.2f}'.format(offer_letter.salary_amount)],
            ['Start Date', offer_letter.start_date.strftime('%d %B %Y')],
            ['Employment Type', 'Full-Time'],
        ]

        offer_table = Table(offer_data, colWidths=[2*inch, 3*inch])
        offer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8EEF7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(offer_table)
        elements.append(Spacer(1, 0.2*inch))

        # Offer content (HTML content if available, or standard terms)
        if offer_letter.offer_content:
            elements.append(Paragraph(offer_letter.offer_content, body_style))
        else:
            # Standard offer terms
            standard_terms = """
            <b>Terms of Employment:</b><br/>
            <br/>
            This offer is contingent upon the following:
            <br/>
            • Successful completion of background verification
            <br/>
            • Verification of educational qualifications
            <br/>
            • Satisfactory health check-up
            <br/>
            • Submission of required documents
            <br/>
            <br/>
            Your employment will be governed by the terms and conditions outlined in the employee handbook,
            company policies, and applicable laws of India. You will be required to sign a formal employment
            agreement before your start date.
            <br/>
            <br/>
            Please note that this offer is valid for 15 days from the date mentioned above. Your acceptance
            of this offer should be communicated in writing before the validity period expires.
            """
            elements.append(Paragraph(standard_terms, body_style))

        elements.append(Spacer(1, 0.2*inch))

        # Closing
        closing = """
        We look forward to welcoming you to our team. Should you have any questions or require any clarification
        regarding this offer, please do not hesitate to contact our Human Resources department.
        <br/>
        <br/>
        <b>Yours sincerely,</b>
        <br/>
        <br/>
        <br/>
        Human Resources Department
        """
        elements.append(Paragraph(closing, body_style))

        # Build PDF
        doc.build(elements)

        # Get PDF data
        buffer.seek(0)
        logger.info(f"Successfully generated offer letter PDF for {offer_letter.employee.name}")
        return buffer

    except Exception as e:
        logger.error(f"Error generating offer letter PDF for {offer_letter.employee.name}: {str(e)}")
        return None


def generate_welcome_document_pdf(employee):
    """
    Generate welcome/onboarding guide PDF for new joiner

    Args:
        employee: Employee object

    Returns:
        BytesIO: PDF file object in memory, None if generation failed
    """
    try:
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )

        elements = []

        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=20,
            alignment=1,
            fontName='Helvetica-Bold'
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            spaceAfter=12,
            leading=14,
        )

        # Welcome header
        elements.append(Paragraph("WELCOME TO OUR ORGANIZATION", title_style))
        elements.append(Spacer(1, 0.2*inch))

        # Personalized welcome
        welcome_text = f"<b>Welcome, {employee.name}!</b><br/><br/>We are delighted to have you join our team. This document contains important information to help you get started."
        elements.append(Paragraph(welcome_text, body_style))
        elements.append(Spacer(1, 0.2*inch))

        # Your details section
        elements.append(Paragraph("Your Details:", heading_style))
        details_data = [
            ['Name', employee.name],
            ['Employee ID', employee.employee_id],
            ['Department', employee.department.name if employee.department else 'N/A'],
            ['Position', employee.position],
            ['Start Date', employee.date_joined.strftime('%d %B %Y')],
        ]

        details_table = Table(details_data, colWidths=[2*inch, 3*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8EEF7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(details_table)
        elements.append(Spacer(1, 0.3*inch))

        # Next steps
        elements.append(Paragraph("Your Onboarding Checklist:", heading_style))
        checklist = """
        <b>Before Your First Day:</b><br/>
        ☐ Review and accept the offer letter<br/>
        ☐ Upload required documents (Resume, ID Proof, Address Proof, Bank Details)<br/>
        ☐ Complete the onboarding form<br/>
        ☐ Sign the employment agreement digitally<br/>
        <br/>
        <b>On Your First Day:</b><br/>
        ☐ Complete IT setup and system access<br/>
        ☐ Receive office access card and keys<br/>
        ☐ Meet your manager and team members<br/>
        ☐ Attend orientation session<br/>
        ☐ Review company policies and procedures<br/>
        """
        elements.append(Paragraph(checklist, body_style))
        elements.append(Spacer(1, 0.2*inch))

        # Contact information
        elements.append(Paragraph("Important Contact Information:", heading_style))
        contact_text = """
        <b>Human Resources Department:</b><br/>
        Email: hr@company.com<br/>
        Phone: Available in the HR Portal<br/>
        <br/>
        If you have any questions during your onboarding process, please feel free to reach out to our HR team.
        We are here to help make your transition smooth and successful.
        """
        elements.append(Paragraph(contact_text, body_style))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)

        logger.info(f"Successfully generated welcome document PDF for {employee.name}")
        return buffer

    except Exception as e:
        logger.error(f"Error generating welcome document PDF for {employee.name}: {str(e)}")
        return None


def generate_document_checklist_pdf(employee, documents):
    """
    Generate document checklist PDF for new joiner

    Args:
        employee: Employee object
        documents: List of DocumentRequirement objects

    Returns:
        BytesIO: PDF file object in memory, None if generation failed
    """
    try:
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )

        elements = []

        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=20,
            alignment=1,
            fontName='Helvetica-Bold'
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            spaceAfter=10,
            leading=14,
        )

        # Title
        elements.append(Paragraph("DOCUMENT UPLOAD CHECKLIST", title_style))
        elements.append(Spacer(1, 0.2*inch))

        # Employee info
        emp_info = f"<b>Employee:</b> {employee.name} | <b>ID:</b> {employee.employee_id}"
        elements.append(Paragraph(emp_info, body_style))
        elements.append(Spacer(1, 0.2*inch))

        # Documents table
        doc_data = [['Document Type', 'Required', 'Format', 'Max Size']]
        for doc in documents:
            required = "Yes" if doc.is_required else "Optional"
            doc_data.append([
                doc.name,
                required,
                doc.file_type_allowed.upper(),
                "5 MB"
            ])

        doc_table = Table(doc_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch])
        doc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')]),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        elements.append(doc_table)
        elements.append(Spacer(1, 0.3*inch))

        # Instructions
        instructions = """
        <b>Upload Instructions:</b><br/>
        1. All documents must be in the specified format (PDF, JPG, or PNG)<br/>
        2. Each file must not exceed 5 MB in size<br/>
        3. Documents should be clear and readable<br/>
        4. Use your full name when saving files for identification<br/>
        5. Upload all required documents to complete onboarding<br/>
        <br/>
        <b>Important:</b> Incomplete document submission may delay your onboarding process.
        Please ensure all required documents are uploaded before your start date.
        """
        elements.append(Paragraph(instructions, body_style))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)

        logger.info(f"Successfully generated document checklist PDF for {employee.name}")
        return buffer

    except Exception as e:
        logger.error(f"Error generating document checklist PDF for {employee.name}: {str(e)}")
        return None
