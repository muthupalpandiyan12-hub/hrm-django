from django.urls import path
from . import views

urlpatterns = [
    path('',                                views.punch_dashboard,       name='punch_dashboard'),
    path('in/',                             views.punch_in,              name='punch_in'),
    path('out/',                            views.punch_out,             name='punch_out'),
    path('admin/',                          views.punch_admin,           name='punch_admin'),
    path('admin/<int:emp_id>/',             views.punch_employee_detail, name='punch_employee_detail'),
    path('admin/close/<int:session_id>/',   views.force_close_session,   name='force_close_session'),
    path('admin/unclosed/',                 views.unclosed_sessions,     name='unclosed_sessions'),
]
