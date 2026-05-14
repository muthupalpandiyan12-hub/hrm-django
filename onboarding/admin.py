from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from .models import (
    OnboardingInvitation, OfferLetter, DocumentRequirement,
    EmployeeDocument, OnboardingChecklist, DigitalSignature
)


@admin.register(OnboardingInvitation)
class OnboardingInvitationAdmin(admin.ModelAdmin):
    list_display = ['employee_name', 'status_badge', 'invitation_token_short', 'email_sent_at', 'accepted_at', 'created_at']
    list_filter = ['status', 'created_at', 'email_sent_at']
    search_fields = ['employee__name', 'employee__email', 'invitation_token']
    readonly_fields = ['invitation_token', 'created_at', 'email_sent_at', 'whatsapp_sent_at', 'accepted_at', 'expires_at']

    fieldsets = (
        ('Employee Information', {
            'fields': ('employee',)
        }),
        ('Invitation Status', {
            'fields': ('status', 'invitation_token')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at', 'email_sent_at', 'whatsapp_sent_at', 'accepted_at'),
            'classes': ('collapse',)
        }),
    )

    def employee_name(self, obj):
        return obj.employee.name
    employee_name.short_description = 'Employee'

    def invitation_token_short(self, obj):
        return f"{obj.invitation_token[:8]}..."
    invitation_token_short.short_description = 'Token'

    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'sent': '#0066CC',
            'accepted': '#00AA00',
            'rejected': '#CC0000',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#999999'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    actions = ['mark_as_sent']

    def mark_as_sent(self, request, queryset):
        count = queryset.update(status='sent')
        self.message_user(request, f'{count} invitations marked as sent.')
    mark_as_sent.short_description = 'Mark selected as sent'


@admin.register(OfferLetter)
class OfferLetterAdmin(admin.ModelAdmin):
    list_display = ['employee_name', 'status_badge', 'salary_display', 'start_date', 'created_at', 'sent_at']
    list_filter = ['status', 'created_at', 'start_date']
    search_fields = ['employee__name', 'employee__email', 'department']
    readonly_fields = ['created_at', 'sent_at', 'signed_at', 'created_by', 'pdf_preview']

    fieldsets = (
        ('Employee Information', {
            'fields': ('employee', 'created_by')
        }),
        ('Offer Details', {
            'fields': ('title', 'department', 'salary_amount', 'start_date')
        }),
        ('Offer Content', {
            'fields': ('offer_content',),
            'classes': ('wide',)
        }),
        ('Document', {
            'fields': ('pdf_file', 'pdf_preview'),
            'classes': ('collapse',)
        }),
        ('Status & Timestamps', {
            'fields': ('status', 'created_at', 'sent_at', 'signed_at'),
            'classes': ('collapse',)
        }),
    )

    def employee_name(self, obj):
        return obj.employee.name
    employee_name.short_description = 'Employee'

    def salary_display(self, obj):
        return f"₹{obj.salary_amount:,.2f}"
    salary_display.short_description = 'Salary'

    def status_badge(self, obj):
        colors = {
            'draft': '#CCCCCC',
            'sent': '#0066CC',
            'signed': '#00AA00',
            'rejected': '#CC0000',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#999999'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def pdf_preview(self, obj):
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank">Download PDF</a>',
                obj.pdf_file.url
            )
        return 'No PDF generated'
    pdf_preview.short_description = 'PDF File'

    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(DocumentRequirement)
class DocumentRequirementAdmin(admin.ModelAdmin):
    list_display = ['name', 'required_badge', 'file_type_allowed', 'created_at']
    list_filter = ['is_required', 'file_type_allowed', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Document Type', {
            'fields': ('name', 'is_required')
        }),
        ('Requirements', {
            'fields': ('file_type_allowed', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def required_badge(self, obj):
        if obj.is_required:
            return format_html(
                '<span style="background-color: #00AA00; color: white; padding: 3px 8px; border-radius: 3px;">Required</span>'
            )
        return format_html(
            '<span style="background-color: #CCCCCC; color: white; padding: 3px 8px; border-radius: 3px;">Optional</span>'
        )
    required_badge.short_description = 'Type'


@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ['employee_name', 'document_type', 'verification_badge', 'uploaded_at', 'verified_at']
    list_filter = ['admin_verified', 'document_type', 'uploaded_at']
    search_fields = ['employee__name', 'employee__email', 'document_type__name']
    readonly_fields = ['uploaded_at', 'verified_at', 'verified_by', 'file_preview']

    fieldsets = (
        ('Employee Information', {
            'fields': ('employee',)
        }),
        ('Document Details', {
            'fields': ('document_type', 'file', 'file_preview')
        }),
        ('Verification', {
            'fields': ('admin_verified', 'verified_by', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'verified_at'),
            'classes': ('collapse',)
        }),
    )

    def employee_name(self, obj):
        return obj.employee.name
    employee_name.short_description = 'Employee'

    def verification_badge(self, obj):
        if obj.admin_verified:
            return format_html(
                '<span style="background-color: #00AA00; color: white; padding: 3px 8px; border-radius: 3px;">✓ Verified</span>'
            )
        return format_html(
            '<span style="background-color: #FFA500; color: white; padding: 3px 8px; border-radius: 3px;">⏳ Pending</span>'
        )
    verification_badge.short_description = 'Status'

    def file_preview(self, obj):
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank">Download</a>',
                obj.file.url
            )
        return 'No file'
    file_preview.short_description = 'File'

    actions = ['mark_as_verified']

    def mark_as_verified(self, request, queryset):
        count = 0
        for doc in queryset:
            if not doc.admin_verified:
                doc.mark_verified(request.user, 'Verified via admin action')
                count += 1
        self.message_user(request, f'{count} documents marked as verified.')
    mark_as_verified.short_description = 'Mark selected as verified'


@admin.register(OnboardingChecklist)
class OnboardingChecklistAdmin(admin.ModelAdmin):
    list_display = ['employee_name', 'title', 'completion_badge', 'due_date', 'completed_at']
    list_filter = ['is_completed', 'due_date', 'created_at']
    search_fields = ['employee__name', 'title', 'description']
    readonly_fields = ['created_at', 'completed_at']

    fieldsets = (
        ('Employee & Task', {
            'fields': ('employee', 'title', 'description')
        }),
        ('Status', {
            'fields': ('is_completed', 'due_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

    def employee_name(self, obj):
        return obj.employee.name
    employee_name.short_description = 'Employee'

    def completion_badge(self, obj):
        if obj.is_completed:
            return format_html(
                '<span style="background-color: #00AA00; color: white; padding: 3px 8px; border-radius: 3px;">✓ Completed</span>'
            )
        return format_html(
            '<span style="background-color: #CCCCCC; color: white; padding: 3px 8px; border-radius: 3px;">⏳ Pending</span>'
        )
    completion_badge.short_description = 'Status'

    actions = ['mark_as_completed']

    def mark_as_completed(self, request, queryset):
        count = 0
        for item in queryset:
            if not item.is_completed:
                item.mark_completed()
                count += 1
        self.message_user(request, f'{count} checklist items marked as completed.')
    mark_as_completed.short_description = 'Mark selected as completed'


@admin.register(DigitalSignature)
class DigitalSignatureAdmin(admin.ModelAdmin):
    list_display = ['employee_name', 'document_type', 'status_badge', 'signed_on', 'created_at']
    list_filter = ['status', 'document_type', 'created_at']
    search_fields = ['invitation__employee__name', 'signature_token']
    readonly_fields = ['signature_token', 'created_at', 'expires_at', 'signature_preview']

    fieldsets = (
        ('Invitation & Document', {
            'fields': ('invitation', 'document_type')
        }),
        ('Signature', {
            'fields': ('signature_token', 'status', 'employee_signature', 'signature_preview', 'signed_on')
        }),
        ('Expiry', {
            'fields': ('expires_at', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def employee_name(self, obj):
        return obj.invitation.employee.name
    employee_name.short_description = 'Employee'

    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'signed': '#00AA00',
            'rejected': '#CC0000',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#999999'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def signature_preview(self, obj):
        if obj.employee_signature:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 150px;" />',
                obj.employee_signature.url
            )
        return 'No signature yet'
    signature_preview.short_description = 'Signature Image'
