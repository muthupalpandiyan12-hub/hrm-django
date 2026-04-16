from django.urls import path
from . import views

urlpatterns = [
    # Employee Portal
    path('portal/',             views.employee_portal,    name='employee_portal'),
    path('portal/profile/',     views.portal_profile,     name='portal_profile'),
    path('portal/attendance/',  views.portal_attendance,  name='portal_attendance'),
    path('portal/leaves/',      views.portal_leaves,      name='portal_leaves'),
    path('portal/payslips/',    views.portal_payslips,    name='portal_payslips'),
    path('portal/reviews/',     views.portal_reviews,     name='portal_reviews'),

    # Admin — User Management
    path('users/',              views.user_list,          name='user_list'),
    path('users/create/',       views.user_create,        name='user_create'),
    path('users/<int:pk>/delete/', views.user_delete,     name='user_delete'),
]
