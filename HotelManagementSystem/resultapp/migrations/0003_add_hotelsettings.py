# Generated migration: add HotelSettings model
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resultapp', '0002_alter_payment_payment_method'),
    ]

    operations = [
        migrations.CreateModel(
            name='HotelSettings',
            fields=[
                ('id',              models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency',        models.CharField(default='USD ($)',      max_length=20)),
                ('payment_gateway', models.CharField(default='Stripe',       max_length=50)),
                ('tax_rate',        models.CharField(default='10',           max_length=10)),
                ('date_format',     models.CharField(default='MM/DD/YYYY',   max_length=20)),
                ('time_zone',       models.CharField(default='UTC-5',        max_length=30)),
                ('language',        models.CharField(default='English',      max_length=30)),
                ('check_in_time',   models.CharField(default='15:00',        max_length=10)),
                ('check_out_time',  models.CharField(default='11:00',        max_length=10)),
                ('cleaning_time',   models.CharField(default='30',           max_length=10)),
                ('payment_timeout', models.CharField(default='3600',         max_length=10)),
                ('currency_code',   models.CharField(default='USD',          max_length=5)),
                ('base_rate',       models.CharField(default='150',          max_length=20)),
                ('updated_at',      models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Hotel Settings',
                'verbose_name_plural': 'Hotel Settings',
            },
        ),
    ]