from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resultapp', '0003_add_hotelsettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='check_in_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='check_out_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
