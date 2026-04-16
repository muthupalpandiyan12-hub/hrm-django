from django.urls import path
from . import views

urlpatterns = [
    path('', views.leave_list, name='leave_list'),
    path('apply/', views.leave_apply, name='leave_apply'),
    path('<int:pk>/approve/', views.leave_approve, name='leave_approve'),
    path('<int:pk>/delete/', views.leave_delete, name='leave_delete'),
    path('balance/', views.leave_balance, name='leave_balance'),
]
