# Generated by Django 5.1.7 on 2025-03-14 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='confirmation',
            constraint=models.UniqueConstraint(fields=('tableID', 'booking_date', 'booking_start', 'booking_end'), name='unique_booking'),
        ),
    ]
