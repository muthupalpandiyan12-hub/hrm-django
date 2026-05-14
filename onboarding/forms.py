from django import forms
from django.core.exceptions import ValidationError
from .models import (
    OfferLetter, EmployeeDocument, OnboardingChecklist,
    DocumentRequirement, OnboardingInvitation
)
from employees.models import Employee, Department
from django.conf import settings


class EmployeeCreationForm(forms.ModelForm):
    """
    Custom form for admin to create employees and start onboarding
    Bypasses Django's problematic admin change_form template
    """
    class Meta:
        model = Employee
        fields = ['employee_id', 'name', 'email', 'phone', 'position', 'department', 'salary', 'status']
        widgets = {
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'E.g., EMP001',
                'required': True
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job Position',
                'required': True
            }),
            'department': forms.Select(attrs={
                'class': 'form-control'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.all()
        self.fields['department'].required = False
        self.fields['status'].initial = 'active'

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if Employee.objects.filter(employee_id=employee_id).exclude(pk=self.instance.pk if self.instance.pk else None).exists():
            raise ValidationError("This Employee ID already exists")
        return employee_id

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Employee.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance.pk else None).exists():
            raise ValidationError("An employee with this email already exists")
        return email


class OfferLetterForm(forms.ModelForm):
    """
    Form for creating and editing offer letters
    """
    send_immediately = forms.BooleanField(
        required=False,
        label="Send Offer Letter Immediately After Saving",
        help_text="Check this to automatically send the offer letter via email"
    )

    class Meta:
        model = OfferLetter
        fields = ['title', 'salary_amount', 'department', 'start_date', 'offer_content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'E.g., Offer of Employment'
            }),
            'salary_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter annual salary amount',
                'step': '0.01'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'E.g., Software Engineer'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'offer_content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Enter full offer letter content (HTML supported)'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = "Offer Letter Title"
        self.fields['salary_amount'].label = "Annual Salary (₹)"
        self.fields['department'].label = "Department / Position"
        self.fields['start_date'].label = "Employment Start Date"
        self.fields['offer_content'].label = "Offer Letter Content"

    def clean_salary_amount(self):
        salary = self.cleaned_data.get('salary_amount')
        if salary and salary <= 0:
            raise ValidationError("Salary amount must be greater than 0")
        return salary

    def clean_start_date(self):
        from django.utils import timezone
        start_date = self.cleaned_data.get('start_date')
        if start_date and start_date < timezone.now().date():
            raise ValidationError("Start date cannot be in the past")
        return start_date


class DocumentUploadForm(forms.ModelForm):
    """
    Form for employees to upload required documents during onboarding
    """
    notes = forms.CharField(
        required=False,
        label="Notes (Optional)",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add any notes about this document'
        })
    )

    class Meta:
        model = EmployeeDocument
        fields = ['document_type', 'file']
        widgets = {
            'document_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'
            })
        }

    def __init__(self, *args, **kwargs):
        employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)

        # Filter document requirements to only required ones
        self.fields['document_type'].queryset = DocumentRequirement.objects.filter(
            is_required=True
        )
        self.fields['document_type'].label = "Document Type"

        # Store employee for validation
        self.employee = employee

    def clean_file(self):
        file = self.cleaned_data.get('file')

        if not file:
            raise ValidationError("File is required")

        # Check file size
        max_size = settings.MAX_DOCUMENT_SIZE
        if file.size > max_size:
            max_size_mb = settings.MAX_DOCUMENT_SIZE_MB
            raise ValidationError(
                f"File size exceeds maximum allowed size of {max_size_mb}MB. "
                f"Current file size: {file.size / (1024*1024):.2f}MB"
            )

        # Check file extension
        allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx']
        file_extension = file.name.split('.')[-1].lower()

        if file_extension not in allowed_extensions:
            raise ValidationError(
                f"File type '.{file_extension}' is not allowed. "
                f"Allowed types: {', '.join(allowed_extensions)}"
            )

        return file

    def clean_document_type(self):
        document_type = self.cleaned_data.get('document_type')

        if not document_type:
            raise ValidationError("Please select a document type")

        # Check if document already uploaded
        if self.employee and hasattr(self, 'instance'):
            existing = EmployeeDocument.objects.filter(
                employee=self.employee,
                document_type=document_type
            ).exclude(pk=self.instance.pk if self.instance.pk else None)

            if existing.exists():
                raise ValidationError(
                    f"You have already uploaded a {document_type.name} document. "
                    f"Please upload a different document type or replace the existing one."
                )

        return document_type


class OnboardingChecklistForm(forms.Form):
    """
    Form for employees to mark onboarding checklist items as complete
    """
    def __init__(self, *args, checklist_items=None, **kwargs):
        super().__init__(*args, **kwargs)

        if checklist_items:
            for item in checklist_items:
                field_name = f'task_{item.id}'
                self.fields[field_name] = forms.BooleanField(
                    required=False,
                    label=item.title,
                    help_text=item.description if item.description else '',
                    widget=forms.CheckboxInput(attrs={
                        'class': 'form-check-input',
                        'data-task-id': item.id
                    })
                )


class AdminChecklistManagementForm(forms.ModelForm):
    """
    Form for admin to manage onboarding checklist items
    """
    class Meta:
        model = OnboardingChecklist
        fields = ['title', 'description', 'due_date', 'is_completed']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'E.g., IT Setup, Office Access'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description of the task'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_completed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = "Checklist Item Title"
        self.fields['description'].label = "Description"
        self.fields['due_date'].label = "Due Date"
        self.fields['is_completed'].label = "Mark as Completed"

    def clean_due_date(self):
        from django.utils import timezone
        due_date = self.cleaned_data.get('due_date')

        if due_date and due_date < timezone.now().date():
            raise ValidationError("Due date cannot be in the past")

        return due_date


class DocumentVerificationForm(forms.Form):
    """
    Form for admin to verify documents uploaded by employees
    """
    VERIFICATION_CHOICES = [
        ('pending', 'Pending Review'),
        ('verified', 'Verified & Approved'),
        ('rejected', 'Rejected - Request Resubmission'),
    ]

    verification_status = forms.ChoiceField(
        choices=VERIFICATION_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label="Verification Status"
    )

    admin_notes = forms.CharField(
        required=False,
        label="Verification Notes",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Add notes for this verification (e.g., reason for rejection)'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        verification_status = cleaned_data.get('verification_status')
        admin_notes = cleaned_data.get('admin_notes')

        # If rejected, notes are required
        if verification_status == 'rejected' and not admin_notes:
            raise ValidationError("Please provide notes when rejecting a document")

        return cleaned_data


class InvitationResendForm(forms.Form):
    """
    Form for admin to resend invitation to employee
    """
    CONTACT_METHOD_CHOICES = [
        ('email', 'Send via Email'),
        ('whatsapp', 'Send via WhatsApp'),
        ('both', 'Send via Both Email and WhatsApp'),
    ]

    contact_method = forms.ChoiceField(
        choices=CONTACT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label="Send Invitation Via"
    )

    custom_message = forms.CharField(
        required=False,
        label="Custom Message (Optional)",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add a custom message to the invitation (optional)'
        })
    )


class SignatureForm(forms.Form):
    """
    Form for employee to provide digital signature
    """
    signature_image = forms.ImageField(
        label="Your Signature",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text="Upload a clear image of your signature"
    )

    agree_terms = forms.BooleanField(
        label="I agree to the terms and conditions of this document",
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def clean_signature_image(self):
        image = self.cleaned_data.get('signature_image')

        if not image:
            raise ValidationError("Signature image is required")

        # Check file size (max 2MB for images)
        if image.size > 2 * 1024 * 1024:
            raise ValidationError("Signature image must be less than 2MB")

        # Check file type
        if not image.content_type.startswith('image/'):
            raise ValidationError("Please upload a valid image file")

        return image

    def clean_agree_terms(self):
        agree = self.cleaned_data.get('agree_terms')

        if not agree:
            raise ValidationError("You must agree to the terms to sign the document")

        return agree
