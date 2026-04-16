from django.urls import path
from . import views

urlpatterns = [
    path('', views.payroll_list, name='payroll_list'),
    path('generate/', views.payroll_generate, name='payroll_generate'),
    path('<int:pk>/delete/', views.payroll_delete, name='payroll_delete'),
    path('<int:pk>/pdf/', views.payroll_pdf, name='payroll_pdf'),
    path('export/', views.payroll_export, name='payroll_export'),
]
