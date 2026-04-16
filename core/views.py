from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import datetime
from .models import Holiday, Announcement
from userroles.helpers import admin_required


@admin_required
def holiday_list(request):
    if request.method == 'POST':
        try:
            Holiday.objects.create(
                name=request.POST['name'],
                date=request.POST['date'],
                holiday_type=request.POST.get('holiday_type', 'public'),
                description=request.POST.get('description', ''),
            )
            messages.success(request, 'Holiday added successfully.')
            return redirect('holiday_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')

    today = datetime.date.today()
    holidays = Holiday.objects.all()
    # Annotate days until each holiday
    holiday_data = []
    for h in holidays:
        if h.date >= today:
            days_until = (h.date - today).days
        else:
            days_until = None
        holiday_data.append({'holiday': h, 'days_until': days_until})

    return render(request, 'core/holiday_list.html', {
        'holiday_data': holiday_data,
        'type_choices': Holiday.TYPE_CHOICES,
    })


@admin_required
def holiday_delete(request, pk):
    holiday = get_object_or_404(Holiday, pk=pk)
    if request.method == 'POST':
        holiday.delete()
        messages.success(request, 'Holiday deleted.')
        return redirect('holiday_list')
    return redirect('holiday_list')


@admin_required
def announcement_list(request):
    if request.method == 'POST':
        try:
            Announcement.objects.create(
                title=request.POST['title'],
                content=request.POST['content'],
                priority=request.POST.get('priority', 'medium'),
                is_active=request.POST.get('is_active') == 'on',
                expires_on=request.POST.get('expires_on') or None,
                posted_by=request.user,
            )
            messages.success(request, 'Announcement posted successfully.')
            return redirect('announcement_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')

    announcements = Announcement.objects.all()
    return render(request, 'core/announcement_list.html', {
        'announcements': announcements,
        'priority_choices': Announcement.PRIORITY_CHOICES,
    })


@admin_required
def announcement_delete(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        announcement.delete()
        messages.success(request, 'Announcement deleted.')
        return redirect('announcement_list')
    return redirect('announcement_list')
