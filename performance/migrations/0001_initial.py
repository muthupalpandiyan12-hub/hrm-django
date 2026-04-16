from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerformanceReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.CharField(
                    choices=[
                        ('Q1', 'Q1 (Jan-Mar)'),
                        ('Q2', 'Q2 (Apr-Jun)'),
                        ('Q3', 'Q3 (Jul-Sep)'),
                        ('Q4', 'Q4 (Oct-Dec)'),
                        ('annual', 'Annual'),
                    ],
                    max_length=10,
                )),
                ('year', models.IntegerField()),
                ('rating', models.IntegerField(
                    choices=[
                        (1, 'Poor'),
                        (2, 'Below Average'),
                        (3, 'Average'),
                        (4, 'Good'),
                        (5, 'Excellent'),
                    ],
                )),
                ('strengths', models.TextField(blank=True)),
                ('improvements', models.TextField(blank=True)),
                ('goals', models.TextField(blank=True)),
                ('status', models.CharField(
                    choices=[
                        ('draft', 'Draft'),
                        ('submitted', 'Submitted'),
                        ('acknowledged', 'Acknowledged'),
                    ],
                    default='draft',
                    max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reviews',
                    to='employees.employee',
                )),
                ('reviewed_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='auth.user',
                )),
            ],
            options={
                'ordering': ['-year', '-created_at'],
                'unique_together': {('employee', 'period', 'year')},
            },
        ),
    ]
