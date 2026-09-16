from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resultapp', '0006_booking_actual_timestamps'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='guest',
            name='user',
        ),
    ]
