from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_list, name='attendance_list'),
    path('mark/', views.attendance_mark, name='attendance_mark'),
    path('<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),
    path('export/', views.attendance_export, name='attendance_export'),
]
