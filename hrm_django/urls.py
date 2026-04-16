from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('employees/', include('employees.urls')),
    path('attendance/', include('attendance.urls')),
    path('leave/', include('leave.urls')),
    path('payroll/', include('payroll.urls')),
    path('punch/', include('punch.urls')),
    path('core/', include('core.urls')),
    path('performance/', include('performance.urls')),
    path('', include('userroles.urls')),
]
