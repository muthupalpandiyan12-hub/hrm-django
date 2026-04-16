import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
                ('punch_in', models.DateTimeField()),
                ('punch_out', models.DateTimeField(blank=True, null=True)),
                ('employee', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='work_sessions',
                    to='employees.employee'
                )),
            ],
            options={
                'ordering': ['punch_in'],
            },
        ),
    ]
