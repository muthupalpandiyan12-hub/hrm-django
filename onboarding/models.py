from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid
import os

from employees.models import Employee


class OnboardingInvitation(models.Model):
    """
    Tracks invitation sent to new joiners
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='onboarding_invitation')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    invitation_token = models.CharField(max_length=100, unique=True)

    email_sent_at = models.DateTimeField(null=True, blank=True)
    whatsapp_sent_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Invitation for {self.employee.name} - {self.status}"

    def is_expired(self):
        """Check if invitation token has expired"""
        return timezone.now() > self.expires_at

    def is_valid(self):
        """Check if invitation is valid (not expired and not rejected)"""
        return not self.is_expired() and self.status != 'rejected'

    def save(self, *args, **kwargs):
        if not self.invitation_token:
            self.invitation_token = str(uuid.uuid4())
        if not self.expires_at:
            from django.conf import settings
            validity_days = getattr(settings, 'INVITATION_VALIDITY_DAYS', 30)
            self.expires_at = timezone.now() + timedelta(days=validity_days)
        super().save(*args, **kwargs)


class OfferLetter(models.Model):
    """
    Professional offer letter for new joiners
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('signed', 'Signed'),
        ('rejected', 'Rejected'),
    ]

    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='offer_letter')

    title = models.CharField(max_length=200, default="Offer of Employment")
    salary_amount = models.DecimalField(max_digits=10, decimal_places=2)
    department = models.CharField(max_length=100)
    start_date = models.DateField()

    offer_content = models.TextField(help_text="Full offer letter content in HTML")
    pdf_file = models.FileField(upload_to='offer_letters/', null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Offer Letter - {self.employee.name}"


class DocumentRequirement(models.Model):
    """
    Define what documents are required for onboarding
    """
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('jpg', 'JPG'),
        ('png', 'PNG'),
        ('doc', 'Word Document'),
        ('docx', 'Word Document (.docx)'),
    ]

    name = models.CharField(max_length=100, unique=True)  # e.g., "Resume", "ID Proof"
    is_required = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    file_type_allowed = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES, default='pdf')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class EmployeeDocument(models.Model):
    """
    Documents uploaded by new joiners
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document_type = models.ForeignKey(DocumentRequirement, on_delete=models.SET_NULL, null=True)

    file = models.FileField(upload_to='employee_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    admin_verified = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_documents')
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']
        unique_together = ['employee', 'document_type']

    def __str__(self):
        return f"{self.employee.name} - {self.document_type.name}"

    def mark_verified(self, user, notes=""):
        """Mark document as verified by admin"""
        self.admin_verified = True
        self.verified_by = user
        self.verified_at = timezone.now()
        self.admin_notes = notes
        self.save()


class OnboardingChecklist(models.Model):
    """
    Tracks onboarding tasks and day-1 readiness
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='onboarding_checklists')

    title = models.CharField(max_length=200)  # e.g., "IT Setup", "Office Access"
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)

    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.employee.name} - {self.title}"

    def mark_completed(self):
        """Mark checklist item as completed"""
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()


class DigitalSignature(models.Model):
    """
    Track digital signatures on offer letters and documents
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('signed', 'Signed'),
        ('rejected', 'Rejected'),
    ]

    DOCUMENT_TYPE_CHOICES = [
        ('offer_letter', 'Offer Letter'),
        ('documents', 'Documents'),
        ('agreement', 'Agreement'),
    ]

    invitation = models.OneToOneField(OnboardingInvitation, on_delete=models.CASCADE, related_name='digital_signature')

    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='offer_letter')
    signature_token = models.CharField(max_length=100, unique=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    employee_signature = models.ImageField(upload_to='signatures/', null=True, blank=True)
    signed_on = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Signature - {self.invitation.employee.name}"

    def is_valid(self):
        """Check if signature token is still valid"""
        return timezone.now() <= self.expires_at and self.status == 'pending'

    def save(self, *args, **kwargs):
        if not self.signature_token:
            self.signature_token = str(uuid.uuid4())
        if not self.expires_at:
            from django.conf import settings
            validity_days = getattr(settings, 'INVITATION_VALIDITY_DAYS', 30)
            self.expires_at = timezone.now() + timedelta(days=validity_days)
        super().save(*args, **kwargs)
