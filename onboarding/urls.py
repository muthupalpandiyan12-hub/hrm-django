from django.urls import path
from . import views

urlpatterns = [
    # Admin Views
    path('', views.onboarding_dashboard, name='onboarding_dashboard'),
    path('create-employee/', views.create_employee, name='create_employee'),
    path('admin/progress/', views.onboarding_progress_dashboard, name='onboarding_progress_dashboard'),
    path('employee/<int:employee_id>/invite/', views.send_invitation, name='send_invitation'),
    path('employee/<int:employee_id>/offer/', views.create_offer_letter, name='create_offer_letter'),
    path('employee/<int:employee_id>/documents/', views.document_verification, name='document_verification'),
    path('document/<int:document_id>/verify/', views.verify_document, name='verify_document'),
    path('employee/<int:employee_id>/checklist/', views.manage_onboarding_checklist, name='manage_onboarding_checklist'),

    # Employee Login & Dashboard
    path('employee/login/', views.employee_login, name='employee_login'),
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('employee/logout/', views.employee_logout, name='employee_logout'),

    # Portal Views (New Joiner)
    path('join/<str:token>/', views.accept_invitation, name='accept_invitation'),
    path('portal/<str:token>/', views.onboarding_portal, name='onboarding_portal'),
    path('documents/<str:token>/', views.upload_documents, name='upload_documents'),
    path('offer/<str:token>/', views.view_and_sign_offer, name='view_and_sign_offer'),
    path('checklist/<str:token>/', views.day1_checklist, name='day1_checklist'),
    path('complete/<str:token>/', views.onboarding_complete, name='onboarding_complete'),
    path('invalid/', views.invalid_token_view, name='invalid_token'),
]
