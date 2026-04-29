from django.urls import path
from . import views

urlpatterns = [
    path('holidays/', views.holiday_list, name='holiday_list'),
    path('holidays/<int:pk>/delete/', views.holiday_delete, name='holiday_delete'),
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),
    path('reports/', views.reports, name='reports'),
]
