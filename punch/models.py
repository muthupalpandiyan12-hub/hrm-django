from django.db import models
from employees.models import Employee
from django.utils import timezone
import datetime


class WorkSession(models.Model):
    """Tracks each individual punch-in / punch-out block within a day"""
    employee  = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='work_sessions')
    date      = models.DateField(default=datetime.date.today)
    punch_in  = models.DateTimeField()
    punch_out = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['punch_in']

    def __str__(self):
        out = self.punch_out.strftime('%H:%M') if self.punch_out else 'Active'
        return f"{self.employee.name} | {self.date} | {self.punch_in.strftime('%H:%M')} → {out}"

    # ── Duration helpers ──────────────────────────────────
    def duration_minutes(self):
        """Minutes worked in this session (live if still active)"""
        end = self.punch_out if self.punch_out else timezone.now()
        return max(0, int((end - self.punch_in).total_seconds() / 60))

    def duration_display(self):
        mins = self.duration_minutes()
        return f"{mins // 60}h {mins % 60:02d}m"

    @property
    def is_active(self):
        return self.punch_out is None
