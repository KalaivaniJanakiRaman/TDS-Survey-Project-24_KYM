# Generated by Django 4.1.13 on 2024-11-15 03:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='response',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
