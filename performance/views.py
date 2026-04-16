from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import datetime
from .models import PerformanceReview
from employees.models import Employee
from userroles.helpers import admin_required


@admin_required
def review_list(request):
    reviews = PerformanceReview.objects.select_related('employee', 'reviewed_by').all()

    # Filters
    emp_filter = request.GET.get('employee', '')
    period_filter = request.GET.get('period', '')
    year_filter = request.GET.get('year', '')

    if emp_filter:
        reviews = reviews.filter(employee_id=emp_filter)
    if period_filter:
        reviews = reviews.filter(period=period_filter)
    if year_filter:
        reviews = reviews.filter(year=year_filter)

    total = reviews.count()
    avg_rating = None
    if total:
        total_rating = sum(r.rating for r in reviews)
        avg_rating = round(total_rating / total, 1)
    excellent_count = reviews.filter(rating=5).count()
    pending_count = reviews.filter(status='draft').count()

    employees = Employee.objects.filter(status='active')
    years = list(range(datetime.date.today().year - 3, datetime.date.today().year + 2))

    return render(request, 'performance/list.html', {
        'reviews': reviews,
        'total': total,
        'avg_rating': avg_rating,
        'excellent_count': excellent_count,
        'pending_count': pending_count,
        'employees': employees,
        'period_choices': PerformanceReview.PERIOD_CHOICES,
        'years': years,
        'emp_filter': emp_filter,
        'period_filter': period_filter,
        'year_filter': year_filter,
    })


@admin_required
def review_create(request):
    employees = Employee.objects.filter(status='active')
    years = list(range(datetime.date.today().year - 3, datetime.date.today().year + 2))
    if request.method == 'POST':
        try:
            PerformanceReview.objects.create(
                employee_id=request.POST['employee'],
                reviewed_by=request.user,
                period=request.POST['period'],
                year=int(request.POST['year']),
                rating=int(request.POST['rating']),
                strengths=request.POST.get('strengths', ''),
                improvements=request.POST.get('improvements', ''),
                goals=request.POST.get('goals', ''),
                status=request.POST.get('status', 'draft'),
            )
            messages.success(request, 'Performance review created successfully.')
            return redirect('review_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'performance/form.html', {
        'employees': employees,
        'period_choices': PerformanceReview.PERIOD_CHOICES,
        'rating_choices': PerformanceReview.RATING_CHOICES,
        'status_choices': PerformanceReview.STATUS_CHOICES,
        'years': years,
        'action': 'Create',
    })


@admin_required
def review_detail(request, pk):
    review = get_object_or_404(PerformanceReview, pk=pk)
    return render(request, 'performance/detail.html', {'review': review})


@admin_required
def review_delete(request, pk):
    review = get_object_or_404(PerformanceReview, pk=pk)
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review deleted.')
        return redirect('review_list')
    return redirect('review_detail', pk=pk)
