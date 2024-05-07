# Generated by Django 4.0.8 on 2024-04-16 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_remove_coursecompletionstatusperuser_completion_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursecompletionstatusperuser',
            name='status',
            field=models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='not_started', max_length=20),
        ),
    ]