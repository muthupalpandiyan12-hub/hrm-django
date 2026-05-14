from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db import transaction
from django.urls import reverse
from django.conf import settings

from employees.models import Employee
from .models import (
    OnboardingInvitation, OfferLetter, EmployeeDocument,
    DocumentRequirement, OnboardingChecklist, DigitalSignature
)
from .forms import (
    OfferLetterForm, DocumentUploadForm, OnboardingChecklistForm,
    AdminChecklistManagementForm, DocumentVerificationForm,
    InvitationResendForm, SignatureForm
)
from .utils.email import (
    send_invitation_email, send_offer_letter_email,
    send_document_request_email, send_onboarding_complete_email
)
from .utils.whatsapp import (
    send_invitation_whatsapp, send_status_update_whatsapp,
    send_document_reminder_whatsapp
)
from .utils.pdf import (
    generate_offer_letter_pdf, generate_welcome_document_pdf,
    generate_document_checklist_pdf
)
from .utils.tokens import verify_token, is_token_valid, regenerate_token

import logging

logger = logging.getLogger(__name__)


# ==================== ADMIN VIEWS ====================

@login_required
@require_http_methods(["GET"])
def onboarding_dashboard(request):
    """
    Admin dashboard showing pending onboardings and their status
    """
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page")
        return redirect('home')

    # Get all onboarding invitations grouped by status
    pending_invitations = OnboardingInvitation.objects.filter(
        status='pending'
    ).select_related('employee').order_by('-created_at')

    sent_invitations = OnboardingInvitation.objects.filter(
        status='sent'
    ).select_related('employee').order_by('-created_at')

    accepted_invitations = OnboardingInvitation.objects.filter(
        status='accepted'
    ).select_related('employee').order_by('-created_at')

    # Statistics
    total_pending = pending_invitations.count()
    total_sent = sent_invitations.count()
    total_accepted = accepted_invitations.count()

    context = {
        'pending_invitations': pending_invitations[:10],
        'sent_invitations': sent_invitations[:10],
        'accepted_invitations': accepted_invitations[:10],
        'total_pending': total_pending,
        'total_sent': total_sent,
        'total_accepted': total_accepted,
    }

    return render(request, 'onboarding/admin/dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def send_invitation(request, employee_id):
    """
    Admin view to send invitation to new joiner via email and/or WhatsApp
    """
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page")
        return redirect('home')

    employee = get_object_or_404(Employee, pk=employee_id)

    # Check if invitation already exists
    existing_invitation = OnboardingInvitation.objects.filter(
        employee=employee
    ).first()

    if request.method == 'POST':
        send_email = request.POST.get('send_email') == 'on'
        send_whatsapp = request.POST.get('send_whatsapp') == 'on'

        if not send_email and not send_whatsapp:
            messages.error(request, "Please select at least one contact method")
            return redirect('send_invitation', employee_id=employee_id)

        try:
            # Create or update invitation
            invitation, created = OnboardingInvitation.objects.get_or_create(
                employee=employee
            )

            invitation.status = 'sent'

            # Send email
            if send_email:
                portal_url = request.POST.get('portal_url', settings.PORTAL_URL if hasattr(settings, 'PORTAL_URL') else None)
                email_sent = send_invitation_email(employee, invitation.invitation_token, portal_url)
                if email_sent:
                    invitation.email_sent_at = timezone.now()
                    messages.success(request, f"Invitation email sent to {employee.email}")
                else:
                    messages.warning(request, f"Failed to send email to {employee.email}")

            # Send WhatsApp
            if send_whatsapp:
                if employee.phone_number:
                    whatsapp_sent = send_invitation_whatsapp(
                        employee.phone_number,
                        employee.name,
                        invitation.invitation_token,
                        portal_url if send_email else None
                    )
                    if whatsapp_sent:
                        invitation.whatsapp_sent_at = timezone.now()
                        messages.success(request, f"Invitation WhatsApp sent to {employee.phone_number}")
                    else:
                        messages.warning(request, f"Failed to send WhatsApp to {employee.phone_number}")
                else:
                    messages.warning(request, "Employee phone number not available")

            invitation.save()

            return redirect('onboarding_dashboard')

        except Exception as e:
            logger.error(f"Error sending invitation to {employee.name}: {str(e)}")
            messages.error(request, f"Error sending invitation: {str(e)}")

    context = {
        'employee': employee,
        'existing_invitation': existing_invitation,
    }

    return render(request, 'onboarding/admin/invite_form.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def create_offer_letter(request, employee_id):
    """
    Admin view to create offer letter for employee
    """
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page")
        return redirect('home')

    employee = get_object_or_404(Employee, pk=employee_id)
    offer_letter = OfferLetter.objects.filter(employee=employee).first()

    if request.method == 'POST':
        form = OfferLetterForm(request.POST, instance=offer_letter)
        if form.is_valid():
            offer_letter = form.save(commit=False)
            offer_letter.employee = employee
            offer_letter.created_by = request.user
            offer_letter.status = 'draft'
            offer_letter.save()

            # Generate PDF
            pdf_buffer = generate_offer_letter_pdf(offer_letter)
            if pdf_buffer:
                offer_letter.pdf_file.save(
                    f'offer_letter_{employee.id}.pdf',
                    pdf_buffer
                )
                offer_letter.save()
                messages.success(request, "Offer letter created successfully")
            else:
                messages.warning(request, "Offer letter created but PDF generation failed")

            # Send if requested
            if form.cleaned_data.get('send_immediately'):
                email_sent = send_offer_letter_email(offer_letter)
                if email_sent:
                    offer_letter.status = 'sent'
                    offer_letter.sent_at = timezone.now()
                    offer_letter.save()
                    messages.success(request, f"Offer letter sent to {employee.email}")
                else:
                    messages.error(request, "Failed to send offer letter")

            return redirect('onboarding_dashboard')
    else:
        form = OfferLetterForm(instance=offer_letter)

    context = {
        'form': form,
        'employee': employee,
        'offer_letter': offer_letter,
    }

    return render(request, 'onboarding/admin/offer_letter_form.html', context)


@login_required
@require_http_methods(["GET"])
def document_verification(request, employee_id):
    """
    Admin view to verify documents uploaded by employee
    """
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page")
        return redirect('home')

    employee = get_object_or_404(Employee, pk=employee_id)
    documents = EmployeeDocument.objects.filter(employee=employee).select_related('document_type')

    # Get document requirements
    all_requirements = DocumentRequirement.objects.all()
    uploaded_docs = documents.values_list('document_type_id', flat=True)
    pending_docs = all_requirements.exclude(id__in=uploaded_docs).filter(is_required=True)

    context = {
        'employee': employee,
        'documents': documents,
        'pending_documents': pending_docs,
    }

    return render(request, 'onboarding/admin/document_verification.html', context)


@login_required
@require_http_methods(["POST"])
def verify_document(request, document_id):
    """
    Admin action to verify/reject a document
    """
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Permission denied'})

    document = get_object_or_404(EmployeeDocument, pk=document_id)
    form = DocumentVerificationForm(request.POST)

    if form.is_valid():
        status = form.cleaned_data['verification_status']
        notes = form.cleaned_data.get('admin_notes', '')

        if status == 'verified':
            document.mark_verified(request.user, notes)
            messages.success(request, f"{document.document_type.name} verified successfully")
        elif status == 'rejected':
            document.admin_verified = False
            document.admin_notes = notes
            document.verified_by = request.user
            document.verified_at = timezone.now()
            document.save()

            # Send notification to employee
            send_status_update_whatsapp(
                document.employee.phone_number,
                document.employee.name,
                f"Your {document.document_type.name} was not accepted. Please resubmit: {notes}"
            )
            messages.warning(request, "Document rejected and employee notified")

        return redirect('document_verification', employee_id=document.employee_id)

    return render(request, 'onboarding/admin/document_verification.html', {'form': form})


@login_required
@require_http_methods(["GET", "POST"])
def manage_onboarding_checklist(request, employee_id):
    """
    Admin view to create and manage onboarding checklist for employee
    """
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page")
        return redirect('home')

    employee = get_object_or_404(Employee, pk=employee_id)
    checklists = OnboardingChecklist.objects.filter(employee=employee).order_by('due_date')

    if request.method == 'POST':
        form = AdminChecklistManagementForm(request.POST)
        if form.is_valid():
            checklist = form.save(commit=False)
            checklist.employee = employee
            checklist.save()

            messages.success(request, "Checklist item added successfully")
            return redirect('manage_onboarding_checklist', employee_id=employee_id)
    else:
        form = AdminChecklistManagementForm()

    context = {
        'form': form,
        'employee': employee,
        'checklists': checklists,
    }

    return render(request, 'onboarding/admin/checklist.html', context)


# ==================== PORTAL VIEWS (New Joiner) ====================

@require_http_methods(["GET", "POST"])
def accept_invitation(request, token):
    """
    New joiner accepts invitation and enters onboarding portal
    """
    # Clean token - remove any whitespace
    token = str(token).strip()

    # Debug: Log the token being searched
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"DEBUG: Searching for invitation with token: {token}")
    logger.info(f"DEBUG: Token type: {type(token)}, Token length: {len(token)}")

    # First, check if token exists in database
    try:
        all_invitations = OnboardingInvitation.objects.all()
        logger.info(f"DEBUG: Total invitations in database: {all_invitations.count()}")

        for inv in all_invitations[:5]:
            logger.info(f"DEBUG: Invitation found - Token: {inv.invitation_token}, Status: {inv.status}")

        invitation = OnboardingInvitation.objects.get(invitation_token=token)
        logger.info(f"DEBUG: Invitation found successfully for token: {token}")
    except OnboardingInvitation.DoesNotExist:
        logger.error(f"DEBUG: No invitation found for token: {token}")
        logger.error(f"DEBUG: Token value: '{token}', length: {len(token)}")

        # Check if invitation exists with similar token
        similar = OnboardingInvitation.objects.filter(invitation_token__icontains=token[:8]).first()
        if similar:
            logger.error(f"DEBUG: Found similar invitation with token starting with: {similar.invitation_token[:8]}")

        raise Http404("Invitation not found. The link may have expired or is invalid.")
    except Exception as e:
        logger.exception(f"DEBUG: Exception during invitation lookup: {str(e)}")
        raise

    # Verify token
    token_check = verify_token(token, invitation)
    if not token_check['valid']:
        messages.error(request, f"Invalid or expired invitation link: {token_check['error']}")
        return render(request, 'onboarding/portal/invalid_token.html')

    employee = invitation.employee

    if request.method == 'POST':
        # Mark invitation as accepted
        invitation.status = 'accepted'
        invitation.accepted_at = timezone.now()
        invitation.save()

        messages.success(request, f"Welcome {employee.name}! You have accepted the invitation.")
        return redirect('onboarding_portal', token=token)

    context = {
        'employee': employee,
        'invitation': invitation,
    }

    return render(request, 'onboarding/portal/accept_invitation.html', context)


@require_http_methods(["GET"])
def onboarding_portal(request, token):
    """
    Main onboarding portal for new joiner - shows next steps and progress
    """
    invitation = get_object_or_404(OnboardingInvitation, invitation_token=token)

    # Verify token
    token_check = verify_token(token, invitation)
    if not token_check['valid']:
        messages.error(request, "Invalid or expired invitation link")
        return render(request, 'onboarding/portal/invalid_token.html')

    employee = invitation.employee

    # Get progress data
    offer_letter = OfferLetter.objects.filter(employee=employee).first()
    documents = EmployeeDocument.objects.filter(employee=employee)
    checklists = OnboardingChecklist.objects.filter(employee=employee)
    signature = DigitalSignature.objects.filter(invitation=invitation).first()

    # Calculate progress
    progress = 0
    if invitation.status == 'accepted':
        progress += 10
    if documents.filter(admin_verified=True).exists():
        progress += 30
    if offer_letter and offer_letter.status == 'signed':
        progress += 30
    if checklists.filter(is_completed=True).count() == checklists.count() and checklists.exists():
        progress += 30

    context = {
        'employee': employee,
        'invitation': invitation,
        'token': token,
        'offer_letter': offer_letter,
        'documents_count': documents.count(),
        'verified_documents': documents.filter(admin_verified=True).count(),
        'total_documents': DocumentRequirement.objects.filter(is_required=True).count(),
        'checklist_count': checklists.count(),
        'completed_checklist': checklists.filter(is_completed=True).count(),
        'signature': signature,
        'progress': progress,
    }

    return render(request, 'onboarding/portal/onboarding_portal.html', context)


@require_http_methods(["GET", "POST"])
def upload_documents(request, token):
    """
    New joiner uploads required documents
    """
    invitation = get_object_or_404(OnboardingInvitation, invitation_token=token)

    # Verify token
    token_check = verify_token(token, invitation)
    if not token_check['valid']:
        return render(request, 'onboarding/portal/invalid_token.html')

    employee = invitation.employee
    uploaded_docs = EmployeeDocument.objects.filter(employee=employee)
    required_docs = DocumentRequirement.objects.filter(is_required=True)

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES, employee=employee)
        if form.is_valid():
            document = form.save(commit=False)
            document.employee = employee
            document.save()

            messages.success(request, f"{document.document_type.name} uploaded successfully!")

            # Check if all documents uploaded
            if uploaded_docs.count() >= required_docs.count():
                send_status_update_whatsapp(
                    employee.phone_number,
                    employee.name,
                    "All your documents have been received. Our HR team will review and verify them soon."
                )

            return redirect('upload_documents', token=token)
    else:
        form = DocumentUploadForm(employee=employee)

    context = {
        'form': form,
        'employee': employee,
        'token': token,
        'uploaded_documents': uploaded_docs,
        'required_documents': required_docs,
    }

    return render(request, 'onboarding/portal/document_upload.html', context)


@require_http_methods(["GET", "POST"])
def view_and_sign_offer(request, token):
    """
    New joiner views and digitally signs offer letter
    """
    invitation = get_object_or_404(OnboardingInvitation, invitation_token=token)

    # Verify token
    token_check = verify_token(token, invitation)
    if not token_check['valid']:
        return render(request, 'onboarding/portal/invalid_token.html')

    employee = invitation.employee
    offer_letter = get_object_or_404(OfferLetter, employee=employee)

    if request.method == 'POST':
        form = SignatureForm(request.POST, request.FILES)
        if form.is_valid():
            # Create or update signature record
            signature, created = DigitalSignature.objects.get_or_create(
                invitation=invitation
            )

            signature.employee_signature = form.cleaned_data['signature_image']
            signature.signed_on = timezone.now()
            signature.status = 'signed'
            signature.save()

            # Update offer letter status
            offer_letter.status = 'signed'
            offer_letter.signed_at = timezone.now()
            offer_letter.save()

            messages.success(request, "Offer letter signed successfully!")

            # Send notification
            send_status_update_whatsapp(
                employee.phone_number,
                employee.name,
                "Thank you for signing the offer letter. Please complete your day-1 checklist now."
            )

            return redirect('onboarding_portal', token=token)
    else:
        form = SignatureForm()

    context = {
        'form': form,
        'employee': employee,
        'token': token,
        'offer_letter': offer_letter,
    }

    return render(request, 'onboarding/portal/sign_offer.html', context)


@require_http_methods(["GET", "POST"])
def day1_checklist(request, token):
    """
    New joiner completes day-1 onboarding checklist
    """
    invitation = get_object_or_404(OnboardingInvitation, invitation_token=token)

    # Verify token
    token_check = verify_token(token, invitation)
    if not token_check['valid']:
        return render(request, 'onboarding/portal/invalid_token.html')

    employee = invitation.employee
    checklist_items = OnboardingChecklist.objects.filter(employee=employee).order_by('due_date')

    if request.method == 'POST':
        form = OnboardingChecklistForm(request.POST, checklist_items=checklist_items)
        if form.is_valid():
            # Mark checked items as complete
            for item in checklist_items:
                field_name = f'task_{item.id}'
                if form.cleaned_data.get(field_name):
                    item.mark_completed()

            messages.success(request, "Checklist items marked successfully!")

            # Check if all completed
            completed = checklist_items.filter(is_completed=True).count()
            total = checklist_items.count()

            if completed == total and total > 0:
                return redirect('onboarding_complete', token=token)

            return redirect('day1_checklist', token=token)
    else:
        form = OnboardingChecklistForm(checklist_items=checklist_items)

    context = {
        'form': form,
        'employee': employee,
        'token': token,
        'checklist_items': checklist_items,
    }

    return render(request, 'onboarding/portal/day1_checklist.html', context)


@require_http_methods(["GET"])
def onboarding_complete(request, token):
    """
    Show completion message and summary after all onboarding steps
    """
    invitation = get_object_or_404(OnboardingInvitation, invitation_token=token)

    # Verify token
    token_check = verify_token(token, invitation)
    if not token_check['valid']:
        return render(request, 'onboarding/portal/invalid_token.html')

    employee = invitation.employee

    # Send completion email
    send_onboarding_complete_email(employee)

    # Send notification
    send_status_update_whatsapp(
        employee.phone_number,
        employee.name,
        "Congratulations! Your onboarding is complete. You will receive your login credentials shortly."
    )

    context = {
        'employee': employee,
        'token': token,
    }

    return render(request, 'onboarding/portal/completion.html', context)


@require_http_methods(["GET"])
def invalid_token_view(request):
    """
    Show message for invalid or expired tokens
    """
    return render(request, 'onboarding/portal/invalid_token.html')


# ==================== EMPLOYEE LOGIN & DASHBOARD ====================

@require_http_methods(["GET", "POST"])
def employee_login(request):
    """
    Employee login to access onboarding portal
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        employee_id = request.POST.get('employee_id', '').strip()

        try:
            # Find employee by email and ID
            employee = Employee.objects.filter(email=email, id=employee_id).first()

            if employee:
                # Check if invitation exists
                invitation = OnboardingInvitation.objects.filter(
                    employee=employee
                ).order_by('-created_at').first()

                if invitation:
                    # Store in session
                    request.session['employee_id'] = employee.id
                    request.session['invitation_token'] = invitation.invitation_token
                    request.session['employee_email'] = employee.email
                    request.session['employee_name'] = employee.name

                    messages.success(request, f"Welcome {employee.name}!")
                    return redirect('employee_dashboard')
                else:
                    messages.error(request, "No active onboarding invitation found for this employee.")
            else:
                messages.error(request, "Employee not found. Please check your email and ID.")
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            messages.error(request, "An error occurred during login. Please try again.")

    return render(request, 'onboarding/employee/login.html')


@require_http_methods(["GET"])
def employee_dashboard(request):
    """
    Employee onboarding dashboard showing progress
    """
    if 'employee_id' not in request.session:
        messages.warning(request, "Please login first.")
        return redirect('employee_login')

    employee_id = request.session.get('employee_id')
    token = request.session.get('invitation_token')

    try:
        employee = Employee.objects.get(id=employee_id)
        invitation = OnboardingInvitation.objects.filter(invitation_token=token).first()

        if not invitation:
            return redirect('employee_login')

        # Get onboarding status
        offer_letter = OfferLetter.objects.filter(employee=employee).order_by('-created_at').first()
        documents = EmployeeDocument.objects.filter(employee=employee)
        required_docs = DocumentRequirement.objects.filter(is_required=True)
        checklists = OnboardingChecklist.objects.filter(employee=employee)

        # Calculate progress
        progress = 0
        steps_completed = 0
        total_steps = 4

        # Step 1: Accept Invitation
        if invitation.status == 'accepted':
            progress += 25
            steps_completed += 1
            step1_complete = True
        else:
            step1_complete = False

        # Step 2: Upload Documents
        docs_uploaded = documents.filter(admin_verified=True).count()
        if docs_uploaded >= required_docs.count() and required_docs.exists():
            progress += 25
            steps_completed += 1
            step2_complete = True
        else:
            step2_complete = False

        # Step 3: Review Offer Letter
        if offer_letter and offer_letter.status == 'signed':
            progress += 25
            steps_completed += 1
            step3_complete = True
        else:
            step3_complete = False

        # Step 4: Day-1 Checklist
        if checklists.exists() and checklists.filter(is_completed=True).count() == checklists.count():
            progress += 25
            steps_completed += 1
            step4_complete = True
        else:
            step4_complete = False

        context = {
            'employee': employee,
            'invitation': invitation,
            'token': token,
            'offer_letter': offer_letter,
            'documents_count': documents.count(),
            'verified_documents': docs_uploaded,
            'total_documents': required_docs.count(),
            'checklist_count': checklists.count(),
            'completed_checklist': checklists.filter(is_completed=True).count(),
            'progress': progress,
            'step1_complete': step1_complete,
            'step2_complete': step2_complete,
            'step3_complete': step3_complete,
            'step4_complete': step4_complete,
            'steps_completed': steps_completed,
            'total_steps': total_steps,
        }

        return render(request, 'onboarding/employee/dashboard.html', context)

    except Employee.DoesNotExist:
        messages.error(request, "Employee not found.")
        return redirect('employee_login')


@require_http_methods(["GET"])
def employee_logout(request):
    """
    Employee logout
    """
    request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect('employee_login')


@login_required
@require_http_methods(["GET"])
def onboarding_progress_dashboard(request):
    """
    Admin dashboard showing overall onboarding progress for all employees
    """
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page")
        return redirect('home')

    # Get all onboarding invitations
    onboardings = OnboardingInvitation.objects.select_related('employee').order_by('-created_at')

    # Statistics
    total_invitations = onboardings.count()
    accepted_invitations = onboardings.filter(status='accepted').count()
    pending_invitations = onboardings.filter(status='pending').count()
    sent_invitations = onboardings.filter(status='sent').count()

    # Calculate progress for each employee
    onboarding_list = []
    for invitation in onboardings:
        employee = invitation.employee

        # Get documents
        documents = EmployeeDocument.objects.filter(employee=employee)
        verified_docs = documents.filter(admin_verified=True).count()
        required_docs = DocumentRequirement.objects.filter(is_required=True).count()

        # Get offer letter
        offer_letter = OfferLetter.objects.filter(employee=employee).order_by('-created_at').first()

        # Get checklist
        checklists = OnboardingChecklist.objects.filter(employee=employee)
        completed_checklists = checklists.filter(is_completed=True).count()

        # Calculate progress
        progress = 0
        if invitation.status == 'accepted':
            progress += 25
        if verified_docs > 0:
            progress += 25
        if offer_letter and offer_letter.status == 'signed':
            progress += 25
        if completed_checklists > 0:
            progress += 25

        onboarding_list.append({
            'invitation': invitation,
            'employee': employee,
            'verified_docs': verified_docs,
            'total_docs': required_docs,
            'offer_letter': offer_letter,
            'checklists_completed': completed_checklists,
            'total_checklists': checklists.count(),
            'progress': progress,
        })

    context = {
        'onboardings': onboarding_list,
        'total_invitations': total_invitations,
        'accepted_invitations': accepted_invitations,
        'pending_invitations': pending_invitations,
        'sent_invitations': sent_invitations,
        'completed_invitations': onboardings.filter(status__in=['accepted']).count(),
    }

    return render(request, 'onboarding/admin/onboarding_dashboard.html', context)
