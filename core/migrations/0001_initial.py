from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Holiday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('holiday_type', models.CharField(
                    choices=[
                        ('public', 'Public Holiday'),
                        ('company', 'Company Holiday'),
                        ('optional', 'Optional Holiday'),
                    ],
                    default='public',
                    max_length=20,
                )),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('priority', models.CharField(
                    choices=[
                        ('low', 'Low'),
                        ('medium', 'Medium'),
                        ('high', 'High'),
                        ('urgent', 'Urgent'),
                    ],
                    default='medium',
                    max_length=10,
                )),
                ('is_active', models.BooleanField(default=True)),
                ('expires_on', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('posted_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='auth.user',
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
