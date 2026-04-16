from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalaryHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_salary', models.DecimalField(decimal_places=2, max_digits=10)),
                ('new_salary', models.DecimalField(decimal_places=2, max_digits=10)),
                ('effective_date', models.DateField()),
                ('reason', models.CharField(blank=True, max_length=200)),
                ('reason_type', models.CharField(
                    choices=[
                        ('appraisal', 'Annual Appraisal'),
                        ('promotion', 'Promotion'),
                        ('correction', 'Correction'),
                        ('joining', 'Joining'),
                        ('other', 'Other'),
                    ],
                    default='other',
                    max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='salary_history',
                    to='employees.employee',
                )),
            ],
            options={
                'ordering': ['-effective_date'],
            },
        ),
    ]
